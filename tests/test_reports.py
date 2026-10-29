"""Tests for the reports module (Member 4, ESIMS-F-015 and F-016).

Self-contained: own test app, in-memory SQLite and fixtures. Sales are
inserted directly with the models, so these tests don't depend on the
sales routes.
"""
from datetime import datetime
from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Category, Inventory, Product, Sale, SaleItem, User


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app import create_app
    from app.reports import reports_bp
    from app.reports import routes  # noqa: F401  (attaches routes to reports_bp)

    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    if "reports" not in application.blueprints:
        application.register_blueprint(reports_bp)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def data(app):
    """Products:
    - Laptop: 50,000.00 x 4 in stock, reorder 5  -> low, value 200,000.00
    - Mouse:     500.00 x 30 in stock, reorder 10 -> OK,  value  15,000.00
    - Cable:     250.00 x 0 in stock,  reorder 2  -> out of stock
    - Retired:   999.00 x 7 in stock, inactive   -> excluded
    """
    user = User(username="report_tester", password_hash=generate_password_hash("x"),
                role="Administrator", is_active=True)
    cat = Category(name="Report Test")
    db.session.add_all([user, cat])
    db.session.flush()

    def product(sku, name, price, reorder, active=True):
        p = Product(sku=sku, name=name, category_id=cat.category_id,
                    unit_price=Decimal(price), reorder_level=reorder, is_active=active)
        db.session.add(p)
        db.session.flush()
        return p

    laptop = product("R-LAP", "Laptop", "50000.00", 5)
    mouse = product("R-MOU", "Mouse", "500.00", 10)
    cable = product("R-CAB", "Cable", "250.00", 2)
    retired = product("R-OLD", "Retired", "999.00", 0, active=False)
    db.session.add_all([
        Inventory(product_id=laptop.product_id, quantity_on_hand=4),
        Inventory(product_id=mouse.product_id, quantity_on_hand=30),
        Inventory(product_id=cable.product_id, quantity_on_hand=0),
        Inventory(product_id=retired.product_id, quantity_on_hand=7),
    ])
    db.session.commit()
    return {"user_id": user.user_id, "laptop": laptop.product_id,
            "mouse": mouse.product_id, "cable": cable.product_id}


@pytest.fixture
def logged_in(client, data):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(data["user_id"])
        sess["_fresh"] = True
    return client


def _add_sale(data, when, items, status="COMPLETED"):
    """items: list of (product_key, quantity, unit_price)."""
    total = sum(Decimal(price) * qty for _, qty, price in items)
    sale = Sale(user_id=data["user_id"], sale_datetime=when,
                total_amount=total, status=status)
    db.session.add(sale)
    db.session.flush()
    for key, qty, price in items:
        db.session.add(SaleItem(sale_id=sale.sale_id, product_id=data[key],
                                quantity=qty, unit_price=Decimal(price)))
    db.session.commit()
    return sale


@pytest.fixture
def sales(data):
    _add_sale(data, datetime(2026, 10, 1, 10, 0), [("laptop", 1, "50000.00"), ("mouse", 2, "500.00")])
    _add_sale(data, datetime(2026, 10, 1, 15, 30), [("mouse", 4, "500.00")])
    _add_sale(data, datetime(2026, 10, 5, 9, 0), [("cable", 3, "250.00")])
    _add_sale(data, datetime(2026, 10, 20, 18, 0), [("laptop", 1, "48000.00")])
    # Not COMPLETED: must be ignored by the report.
    _add_sale(data, datetime(2026, 10, 5, 12, 0), [("laptop", 9, "50000.00")], status="CANCELLED")


# ---------------------------------------------------------------------------
# Login protection
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path", ["/reports/inventory", "/reports/sales"])
def test_reports_require_login(client, path):
    resp = client.get(path)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# Inventory report
# ---------------------------------------------------------------------------
def test_inventory_report_totals(app, data):
    from app.reports.routes import build_inventory_report
    rows, summary = build_inventory_report()
    assert summary["product_count"] == 3          # inactive product excluded
    assert summary["total_units"] == 34           # 4 + 30 + 0
    assert summary["total_value"] == Decimal("215000.00")
    assert summary["low_stock_count"] == 2        # laptop (4 <= 5) and cable (0 <= 2)
    assert summary["out_of_stock_count"] == 1     # cable


def test_inventory_report_rows(app, data):
    from app.reports.routes import build_inventory_report
    rows, _ = build_inventory_report()
    by_sku = {r["sku"]: r for r in rows}
    assert set(by_sku) == {"R-LAP", "R-MOU", "R-CAB"}
    assert by_sku["R-LAP"]["stock_value"] == Decimal("200000.00")
    assert by_sku["R-LAP"]["is_low"] is True
    assert by_sku["R-MOU"]["is_low"] is False


def test_inventory_report_page(logged_in):
    resp = logged_in.get("/reports/inventory")
    assert resp.status_code == 200
    assert b"Laptop" in resp.data and b"Mouse" in resp.data
    assert b"215000.00" in resp.data
    assert b"Low stock" in resp.data and b"Out of stock" in resp.data
    assert b"Retired" not in resp.data


def test_inventory_report_reads_live_stock(app, logged_in, data):
    inv = db.session.query(Inventory).filter_by(product_id=data["mouse"]).one()
    inv.quantity_on_hand = 5
    db.session.commit()
    from app.reports.routes import build_inventory_report
    _, summary = build_inventory_report()
    assert summary["total_units"] == 9
    assert summary["low_stock_count"] == 3


def test_inventory_report_empty(app, client):
    user = User(username="empty", password_hash=generate_password_hash("x"),
                role="Store Staff", is_active=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.user_id)
        sess["_fresh"] = True
    resp = client.get("/reports/inventory")
    assert resp.status_code == 200
    assert b"No active products found." in resp.data


# ---------------------------------------------------------------------------
# Sales report
# ---------------------------------------------------------------------------
def test_sales_report_all_time_totals(app, sales):
    from app.reports.routes import build_sales_report
    summary, products, days, _ = build_sales_report()
    assert summary["sale_count"] == 4                       # cancelled sale ignored
    assert summary["total_units"] == 11                     # 1+2 + 4 + 3 + 1
    assert summary["total_revenue"] == Decimal("101750.00")  # 51000 + 2000 + 750 + 48000
    assert summary["average_sale"] == Decimal("25437.50")


def test_sales_report_by_product_uses_price_at_time_of_sale(app, sales):
    from app.reports.routes import build_sales_report
    _, products, _, _ = build_sales_report()
    assert [p["sku"] for p in products] == ["R-LAP", "R-MOU", "R-CAB"]  # by revenue
    laptop = products[0]
    assert laptop["units"] == 2
    assert laptop["revenue"] == Decimal("98000.00")  # 50000 + 48000
    assert products[1]["units"] == 6 and products[1]["revenue"] == Decimal("3000.00")


def test_sales_report_by_day(app, sales):
    from app.reports.routes import build_sales_report
    _, _, days, _ = build_sales_report()
    assert [d["date"].isoformat() for d in days] == ["2026-10-01", "2026-10-05", "2026-10-20"]
    assert days[0]["sale_count"] == 2
    assert days[0]["revenue"] == Decimal("53000.00")


def test_sales_report_date_range_is_inclusive(app, sales):
    from datetime import date
    from app.reports.routes import build_sales_report
    summary, _, _, _ = build_sales_report(date(2026, 10, 1), date(2026, 10, 5))
    assert summary["sale_count"] == 3                 # includes sales late on the end date
    assert summary["total_revenue"] == Decimal("53750.00")


def test_sales_report_lists_each_sale_in_range(app, sales):
    from datetime import date
    from app.reports.routes import build_sales_report
    _, _, _, sale_rows = build_sales_report(date(2026, 10, 5), date(2026, 10, 31))
    assert [r["sale_datetime"].date().isoformat() for r in sale_rows] == ["2026-10-05", "2026-10-20"]
    assert [r["total_amount"] for r in sale_rows] == [Decimal("750.00"), Decimal("48000.00")]
    assert sale_rows[0]["units"] == 3
    assert sale_rows[0]["username"] == "report_tester"


def test_sales_report_page_lists_sales_in_range(logged_in, sales):
    resp = logged_in.get("/reports/sales?start=2026-10-01&end=2026-10-01")
    assert resp.status_code == 200
    assert b"Sales in this period" in resp.data
    assert b"01 Oct 2026 10:00" in resp.data and b"01 Oct 2026 15:30" in resp.data
    assert b"20 Oct 2026" not in resp.data


def test_sales_report_range_with_no_sales_shows_message(logged_in, sales):
    resp = logged_in.get("/reports/sales?start=2025-01-01&end=2025-01-31")
    assert resp.status_code == 200
    assert b"No sales found for this period." in resp.data


def test_sales_report_page_with_filter(logged_in, sales):
    resp = logged_in.get("/reports/sales?start=2026-10-20&end=2026-10-31")
    assert resp.status_code == 200
    assert b"48000.00" in resp.data
    assert b"Mouse" not in resp.data


def test_sales_report_page_all_time(logged_in, sales):
    resp = logged_in.get("/reports/sales")
    assert resp.status_code == 200
    assert b"All completed sales." in resp.data
    assert b"101750.00" in resp.data


@pytest.mark.parametrize("query, message", [
    ("start=2026-13-40", b"Start date must be a valid date"),
    ("end=yesterday", b"End date must be a valid date"),
    ("start=2026-10-20&end=2026-10-01", b"Start date cannot be after the end date"),
])
def test_sales_report_rejects_bad_dates(logged_in, sales, query, message):
    resp = logged_in.get(f"/reports/sales?{query}")
    assert resp.status_code == 400
    assert message in resp.data
    assert b"Please correct the dates above" in resp.data
    # No figures are shown, so unfiltered totals can't be mistaken for the range.
    assert b"101750.00" not in resp.data
    assert b"Number of sales" not in resp.data
    assert b"All completed sales." not in resp.data


def test_sales_report_keeps_entered_dates_after_error(logged_in, sales):
    resp = logged_in.get("/reports/sales?start=2026-10-20&end=2026-10-01")
    assert b'value="2026-10-20"' in resp.data
    assert b'value="2026-10-01"' in resp.data


@pytest.mark.parametrize("role", ["Store Staff", "Administrator"])
def test_both_roles_can_view_reports(app, client, sales, role):
    """SRS F-015 and F-016 list Store Staff as the stakeholder, and the
    Store Manager/Administrator has access to all functions (SRS 2.3)."""
    user = User(username=f"report_{role.replace(' ', '_')}",
                password_hash=generate_password_hash("x"), role=role, is_active=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.user_id)
        sess["_fresh"] = True

    inv = client.get("/reports/inventory")
    sal = client.get("/reports/sales?start=2026-10-01&end=2026-10-31")
    assert inv.status_code == 200 and b"Laptop" in inv.data
    assert sal.status_code == 200 and b"101750.00" in sal.data


def test_sales_report_with_no_sales(logged_in):
    resp = logged_in.get("/reports/sales")
    assert resp.status_code == 200
    assert b"No sales found for this period." in resp.data
