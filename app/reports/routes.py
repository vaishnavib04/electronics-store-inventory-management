"""
Reports module (Member 4), ESIMS-F-015 and F-016.

Routes (agreed names, do not rename):
    GET /reports/inventory  -> inventory_report()
    GET /reports/sales      -> sales_report()   optional ?start=YYYY-MM-DD&end=YYYY-MM-DD

All figures are read from the database at request time; nothing is hardcoded.
The inventory report reuses get_inventory_rows() from the inventory module,
so /inventory and the report always agree on stock levels.
"""
from collections import OrderedDict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask import flash, render_template, request
from flask_login import login_required
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.inventory.routes import get_inventory_rows
from app.models import Sale, SaleItem
from app.reports import reports_bp

COMPLETED = "COMPLETED"
CENTS = Decimal("0.01")


def _money(value):
    return Decimal(value).quantize(CENTS)


# ---------------------------------------------------------------------------
# Inventory report
# ---------------------------------------------------------------------------
def build_inventory_report():
    """Every active product with stock, stock value and low-stock flag, plus totals."""
    rows = get_inventory_rows()
    for row in rows:
        row["stock_value"] = _money(Decimal(row["unit_price"]) * row["quantity_on_hand"])
    summary = {
        "product_count": len(rows),
        "total_units": sum(r["quantity_on_hand"] for r in rows),
        "total_value": _money(sum((r["stock_value"] for r in rows), Decimal("0"))),
        "low_stock_count": sum(1 for r in rows if r["is_low"]),
        "out_of_stock_count": sum(1 for r in rows if r["quantity_on_hand"] == 0),
    }
    return rows, summary


@reports_bp.route("/reports/inventory")
@login_required
def inventory_report():
    rows, summary = build_inventory_report()
    return render_template(
        "reports/inventory.html",
        rows=rows,
        summary=summary,
        generated_at=datetime.now(),
    )


# ---------------------------------------------------------------------------
# Sales report
# ---------------------------------------------------------------------------
def _parse_date(raw, label):
    """Return (date or None, error or None) for a YYYY-MM-DD form value."""
    raw = (raw or "").strip()
    if not raw:
        return None, None
    try:
        return date.fromisoformat(raw), None
    except ValueError:
        return None, f"{label} must be a valid date (YYYY-MM-DD)."


def build_sales_report(start=None, end=None):
    """Totals for COMPLETED sales between start and end (both inclusive, optional)."""
    query = (
        db.session.query(Sale)
        .options(
            selectinload(Sale.items).selectinload(SaleItem.product),
            selectinload(Sale.user),
        )
        .filter(Sale.status == COMPLETED)
    )
    if start:
        query = query.filter(Sale.sale_datetime >= datetime.combine(start, time.min))
    if end:
        query = query.filter(
            Sale.sale_datetime < datetime.combine(end + timedelta(days=1), time.min)
        )
    sales = query.order_by(Sale.sale_datetime, Sale.sale_id).all()

    by_product = {}
    by_day = OrderedDict()
    total_revenue = Decimal("0")
    total_units = 0

    for sale in sales:
        total_revenue += Decimal(sale.total_amount)
        day = sale.sale_datetime.date()
        day_row = by_day.setdefault(
            day, {"date": day, "sale_count": 0, "units": 0, "revenue": Decimal("0")}
        )
        day_row["sale_count"] += 1
        day_row["revenue"] += Decimal(sale.total_amount)

        for item in sale.items:
            line_total = Decimal(item.unit_price) * item.quantity
            total_units += item.quantity
            day_row["units"] += item.quantity
            prod = by_product.setdefault(
                item.product_id,
                {
                    "sku": item.product.sku,
                    "name": item.product.name,
                    "units": 0,
                    "revenue": Decimal("0"),
                },
            )
            prod["units"] += item.quantity
            prod["revenue"] += line_total

    products = sorted(by_product.values(), key=lambda p: (-p["revenue"], p["name"]))
    for row in products:
        row["revenue"] = _money(row["revenue"])
    days = list(by_day.values())
    for row in days:
        row["revenue"] = _money(row["revenue"])

    sale_count = len(sales)
    summary = {
        "sale_count": sale_count,
        "total_revenue": _money(total_revenue),
        "total_units": total_units,
        "average_sale": _money(total_revenue / sale_count) if sale_count else _money(0),
    }
    sale_rows = [
        {
            "sale_id": sale.sale_id,
            "sale_datetime": sale.sale_datetime,
            "username": sale.user.username if sale.user else "—",
            "units": sum(item.quantity for item in sale.items),
            "total_amount": _money(sale.total_amount),
        }
        for sale in sales
    ]
    return summary, products, days, sale_rows


@reports_bp.route("/reports/sales")
@login_required
def sales_report():
    start, start_error = _parse_date(request.args.get("start"), "Start date")
    end, end_error = _parse_date(request.args.get("end"), "End date")
    errors = [e for e in (start_error, end_error) if e]
    if start and end and start > end:
        errors.append("Start date cannot be after the end date.")

    if errors:
        for error in errors:
            flash(error, "error")
        start = end = None  # fall back to all sales rather than guessing

    summary, products, days, sale_rows = build_sales_report(start, end)
    return render_template(
        "reports/sales.html",
        summary=summary,
        products=products,
        days=days,
        sale_rows=sale_rows,
        start=start,
        end=end,
        raw_start=request.args.get("start", ""),
        raw_end=request.args.get("end", ""),
    ), (400 if errors else 200)
