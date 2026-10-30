from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.inventory.routes import StockValidationError, parse_quantity
from app.models import (
    Inventory,
    Product,
    Purchase,
    PurchaseItem,
    StockMovement,
    Supplier,
)
from app.purchases import purchases_bp


def _submitted_purchase_rows():
    """Return submitted product/quantity/unit_cost rows to repopulate the form after an error."""
    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    unit_costs = request.form.getlist("unit_cost")
    max_len = max(len(product_ids), len(quantities), len(unit_costs), 0)
    rows = []
    for idx in range(max_len):
        pid = product_ids[idx].strip() if idx < len(product_ids) else ""
        qty = quantities[idx].strip() if idx < len(quantities) else ""
        cost = unit_costs[idx].strip() if idx < len(unit_costs) else ""
        if pid or qty or cost:
            rows.append({"product_id": pid, "quantity": qty, "unit_cost": cost})
    return rows or [{"product_id": "", "quantity": "", "unit_cost": ""}]


def _render_purchase_form(form_data=None, rows=None, status=200):
    return (
        render_template(
            "purchases/form.html",
            suppliers=Supplier.query.filter_by(is_active=True)
            .order_by(Supplier.name)
            .all(),
            products=Product.query.filter_by(is_active=True)
            .order_by(Product.name)
            .all(),
            form_data=form_data if form_data is not None else {},
            rows=rows or [{"product_id": "", "quantity": "", "unit_cost": ""}],
        ),
        status,
    )


def _read_purchase_form():
    """Validate purchase form fields and return (values, error)."""
    raw_supplier_id = request.form.get("supplier_id", "").strip()

    try:
        supplier_id = int(raw_supplier_id)
    except (TypeError, ValueError):
        return None, "Please select a valid supplier."

    supplier = db.session.get(Supplier, supplier_id)
    if supplier is None or not supplier.is_active:
        return None, "Please select an active supplier."

    raw_product_ids = request.form.getlist("product_id")
    raw_quantities = request.form.getlist("quantity")
    raw_unit_costs = request.form.getlist("unit_cost")

    if not raw_product_ids:
        return None, "Add at least one product to the purchase."

    if not (
        len(raw_product_ids) == len(raw_quantities) == len(raw_unit_costs)
    ):
        return None, "Each product must have a quantity and unit cost."

    items = []
    total_cost = Decimal("0.00")

    for raw_product_id, raw_quantity, raw_unit_cost in zip(
        raw_product_ids, raw_quantities, raw_unit_costs
    ):
        try:
            product_id = int(raw_product_id)
        except (TypeError, ValueError):
            return None, "Please select a valid product."

        product = db.session.get(Product, product_id)
        if product is None or not product.is_active:
            return None, "Please select an active product."

        try:
            quantity = parse_quantity(raw_quantity)
        except StockValidationError as exc:
            return None, str(exc)

        try:
            unit_cost = Decimal(raw_unit_cost.strip())
        except (InvalidOperation, AttributeError, TypeError, ValueError):
            return None, "Unit cost must be a valid non-negative amount."

        if not unit_cost.is_finite() or unit_cost < 0:
            return None, "Unit cost must be a valid non-negative amount."

        if unit_cost.as_tuple().exponent < -2:
            return None, "Unit cost can have at most two decimal places."

        if unit_cost > Decimal("99999999.99"):
            return None, "Unit cost is too large."

        line_total = quantity * unit_cost
        total_cost += line_total

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_cost": unit_cost,
            }
        )

    if total_cost > Decimal("9999999999.99"):
        return None, "Purchase total is too large."

    return {
        "supplier": supplier,
        "items": items,
        "total_cost": total_cost,
    }, None


@purchases_bp.route("/")
@login_required
def list_purchases():
    purchases = (
        db.session.query(Purchase)
        .order_by(Purchase.purchase_date.desc(), Purchase.purchase_id.desc())
        .all()
    )
    return render_template("purchases/list.html", purchases=purchases)


@purchases_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_purchase():
    if current_user.user_id is None:
        flash("Unable to identify the logged-in user.", "error")
        return redirect(url_for("purchases.list_purchases"))

    if request.method == "POST":
        values, error = _read_purchase_form()
        if error:
            flash(error, "error")
            return _render_purchase_form(
                form_data=request.form,
                rows=_submitted_purchase_rows(),
                status=400,
            )

        try:
            purchase = Purchase(
                supplier_id=values["supplier"].supplier_id,
                user_id=current_user.user_id,
                total_cost=values["total_cost"],
            )
            db.session.add(purchase)
            db.session.flush()

            for item in values["items"]:
                product = item["product"]
                quantity = item["quantity"]

                purchase_item = PurchaseItem(
                    purchase_id=purchase.purchase_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_cost=item["unit_cost"],
                )
                db.session.add(purchase_item)

                inventory = (
                    db.session.query(Inventory)
                    .filter_by(product_id=product.product_id)
                    .with_for_update()
                    .first()
                )

                if inventory is None:
                    inventory = Inventory(
                        product_id=product.product_id,
                        quantity_on_hand=quantity,
                    )
                    db.session.add(inventory)
                else:
                    inventory.quantity_on_hand += quantity

                movement = StockMovement(
                    product_id=product.product_id,
                    movement_type="IN",
                    quantity=quantity,
                    reference_id=purchase.purchase_id,
                    user_id=current_user.user_id,
                )
                db.session.add(movement)

            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Unable to record the purchase. No purchase or stock changes were saved.",
                "error",
            )
            return _render_purchase_form(
                form_data=request.form,
                rows=_submitted_purchase_rows(),
                status=500,
            )

        flash("Purchase recorded successfully.", "success")
        return redirect(url_for("purchases.list_purchases"))

    return _render_purchase_form()
