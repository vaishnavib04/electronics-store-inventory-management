"""
Sales module (Member 4), ESIMS-F-012 to F-014.

Routes (agreed names, do not rename):
    GET      /sales                  -> list_sales()
    GET/POST /sales/new              -> create_sale()
    GET      /sales/<int:sale_id>    -> view_sale()

Rules this module enforces:
    - Requested quantities are checked against available stock; a sale that
      needs more than is in stock is rejected.
    - Prices and totals are calculated on the server from the product's
      current unit_price. Any price or total sent by the browser is ignored.
    - The sale, its sale items, the stock deductions and the OUT stock
      movements are saved in ONE database transaction: either all of it is
      saved, or none of it is.
    - Stock is reduced with reduce_stock() from the inventory module, so
      concurrent sales cannot push stock below zero.
"""
from collections import OrderedDict
from decimal import Decimal

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.inventory.routes import StockValidationError, parse_quantity, reduce_stock
from app.models import Inventory, Product, Sale, SaleItem, StockMovement
from app.sales import sales_bp

SALE_STATUS_COMPLETED = "COMPLETED"
MAX_SALE_TOTAL = Decimal("9999999999.99")  # sales.total_amount is Numeric(12, 2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _products_for_form():
    """Active products with their current stock, for the product dropdown."""
    rows = (
        db.session.query(Product, Inventory.quantity_on_hand)
        .outerjoin(Inventory, Inventory.product_id == Product.product_id)
        .filter(Product.is_active.is_(True))
        .order_by(Product.name)
        .all()
    )
    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "sku": product.sku,
            "unit_price": product.unit_price,
            "available": qty or 0,
        }
        for product, qty in rows
    ]


def _submitted_rows():
    """The product/quantity rows exactly as submitted, to refill the form after an error."""
    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    rows = [
        {"product_id": pid, "quantity": qty}
        for pid, qty in zip(product_ids, quantities)
    ]
    return rows or [{"product_id": "", "quantity": ""}]


def _render_form(rows=None, status=200):
    return (
        render_template(
            "sales/form.html",
            products=_products_for_form(),
            rows=rows or [{"product_id": "", "quantity": ""}],
        ),
        status,
    )


def _read_sale_form():
    """Validate the submitted items and price them on the server.

    Returns (lines, total, error). Each line is a dict with product,
    quantity, unit_price and line_total. If the same product appears in
    more than one row, the quantities are added together, so the stock
    check covers the full amount being sold.
    """
    raw_product_ids = request.form.getlist("product_id")
    raw_quantities = request.form.getlist("quantity")

    if len(raw_product_ids) != len(raw_quantities):
        return None, None, "Each product must have a quantity."

    # Ignore completely empty rows (e.g. an extra row the user added but left blank).
    pairs = [
        (pid.strip(), qty.strip())
        for pid, qty in zip(raw_product_ids, raw_quantities)
        if pid.strip() or qty.strip()
    ]
    if not pairs:
        return None, None, "Add at least one product to the sale."

    quantities_by_product = OrderedDict()
    for raw_product_id, raw_quantity in pairs:
        try:
            product_id = int(raw_product_id)
        except ValueError:
            return None, None, "Please select a valid product."
        try:
            quantity = parse_quantity(raw_quantity)
        except StockValidationError as exc:
            return None, None, str(exc)
        quantities_by_product[product_id] = (
            quantities_by_product.get(product_id, 0) + quantity
        )

    lines = []
    total = Decimal("0.00")
    for product_id, quantity in quantities_by_product.items():
        product = db.session.get(Product, product_id)
        if product is None or not product.is_active:
            return None, None, "Please select an active product."
        unit_price = Decimal(product.unit_price)  # server-side price, never from the form
        line_total = (unit_price * quantity).quantize(Decimal("0.01"))
        total += line_total
        lines.append(
            {
                "product_id": product.product_id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )

    if total > MAX_SALE_TOTAL:
        return None, None, "Sale total is too large."

    return lines, total, None


def _save_sale(lines, total, user_id):
    """Save the sale, items, stock deductions and movements atomically.

    Raises StockValidationError (not enough stock) or SQLAlchemyError.
    The caller commits nothing itself; this function commits on success
    and rolls back on any failure.
    """
    try:
        sale = Sale(
            user_id=user_id,
            total_amount=total,
            status=SALE_STATUS_COMPLETED,
        )
        db.session.add(sale)
        db.session.flush()
        sale_id = sale.sale_id

        for line in lines:
            # Atomic check-and-subtract; raises if stock is insufficient.
            reduce_stock(line["product_id"], line["quantity"])

            db.session.add(
                SaleItem(
                    sale_id=sale_id,
                    product_id=line["product_id"],
                    quantity=line["quantity"],
                    unit_price=line["unit_price"],
                )
            )
            db.session.add(
                StockMovement(
                    product_id=line["product_id"],
                    movement_type="OUT",
                    quantity=line["quantity"],
                    reference_id=sale_id,
                    user_id=user_id,
                )
            )
            db.session.flush()

        db.session.commit()
        return sale_id
    except (StockValidationError, SQLAlchemyError):
        db.session.rollback()
        raise


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@sales_bp.route("/sales")
@login_required
def list_sales():
    sales = (
        db.session.query(Sale)
        .order_by(Sale.sale_datetime.desc(), Sale.sale_id.desc())
        .all()
    )
    return render_template("sales/list.html", sales=sales)


@sales_bp.route("/sales/new", methods=["GET", "POST"])
@login_required
def create_sale():
    if request.method == "GET":
        return _render_form()

    lines, total, error = _read_sale_form()
    if error:
        flash(error, "error")
        return _render_form(_submitted_rows(), status=400)

    try:
        sale_id = _save_sale(lines, total, current_user.user_id)
    except StockValidationError as exc:
        flash(f"{exc} The sale was not recorded.", "error")
        return _render_form(_submitted_rows(), status=400)
    except SQLAlchemyError:
        flash(
            "Unable to record the sale. No sale or stock changes were saved.",
            "error",
        )
        return _render_form(_submitted_rows(), status=500)

    flash(f"Sale #{sale_id} recorded successfully.", "success")
    return redirect(url_for("sales.view_sale", sale_id=sale_id))


@sales_bp.route("/sales/<int:sale_id>")
@login_required
def view_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if sale is None:
        abort(404)
    items = [
        {
            "product_name": item.product.name,
            "sku": item.product.sku,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": (Decimal(item.unit_price) * item.quantity).quantize(
                Decimal("0.01")
            ),
        }
        for item in sale.items
    ]
    return render_template("sales/detail.html", sale=sale, items=items)
