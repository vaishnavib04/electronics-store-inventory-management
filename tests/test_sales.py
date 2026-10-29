"""Tests for the sales module (Member 4, ESIMS-F-012 to F-014).

Self-contained: builds its own test app on an in-memory SQLite database with
its own fixtures, so it never depends on or clashes with other test files.
"""
from decimal import Decimal

import pytest
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import (
    Category,
    Inventory,
    Product,
    Sale,
    SaleItem,
    StockMovement,
    User,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app import create_app
    from app.sales import routes  # noqa: F401  (attaches routes to sales_bp)
    from app.sales import sales_bp

    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    # Works before and after sales_bp is registered in app/__init__.py.
    if "sales" not in application.blueprints:
        application.register_blueprint(sales_bp)

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
    """A logged-in user and three products:
    - Phone:  price 100.00, 10 in stock
    - Cable:  price  15.50,  3 in stock
    - Old TV: price 500.00,  5 in stock, but deactivated
    - Charger (no inventory row at all)
    """
    user = User(username="sales_tester", password_hash=generate_password_hash("x"),
                role="Store Staff", is_active=True)
    cat = Category(name="Sales Test")
    db.session.add_all([user, cat])
    db.session.flush()

    phone = Product(sku="S-PHONE", name="Phone", category_id=cat.category_id,
                    unit_price=Decimal("100.00"), reorder_level=2, is_active=True)
    cable = Product(sku="S-CABLE", name="Cable", category_id=cat.category_id,
                    unit_price=Decimal("15.50"), reorder_level=2, is_active=True)
    old_tv = Product(sku="S-TV", name="Old TV", category_id=cat.category_id,
                     unit_price=Decimal("500.00"), reorder_level=0, is_active=False)
    charger = Product(sku="S-CHG", name="Charger", category_id=cat.category_id,
                      unit_price=Decimal("20.00"), reorder_level=0, is_active=True)
    db.session.add_all([phone, cable, old_tv, charger])
    db.session.flush()
    db.session.add_all([
        Inventory(product_id=phone.product_id, quantity_on_hand=10),
        Inventory(product_id=cable.product_id, quantity_on_hand=3),
        Inventory(product_id=old_tv.product_id, quantity_on_hand=5),
    ])
    db.session.commit()
    return {
        "user_id": user.user_id,
        "phone": phone.product_id,
        "cable": cable.product_id,
        "old_tv": old_tv.product_id,
        "charger": charger.product_id,
    }


@pytest.fixture
def logged_in(client, data):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(data["user_id"])
        sess["_fresh"] = True
    return client


def _stock(product_id):
    return db.session.query(Inventory.quantity_on_hand).filter_by(
        product_id=product_id).scalar()


def _counts():
    return (
        db.session.query(Sale).count(),
        db.session.query(SaleItem).count(),
        db.session.query(StockMovement).count(),
    )


def _sell(client, *rows, **extra):
    """Post a sale. rows are (product_id, quantity) pairs."""
    form = {
        "product_id": [str(pid) for pid, _ in rows],
        "quantity": [str(qty) for _, qty in rows],
    }
    form.update(extra)
    return client.post("/sales/new", data=form)


# ---------------------------------------------------------------------------
# Login protection
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path", ["/sales", "/sales/new", "/sales/1"])
def test_sales_pages_require_login(client, path):
    resp = client.get(path)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_post_new_sale_requires_login(client, data):
    resp = _sell(client, (data["phone"], 1))
    assert resp.status_code == 302
    assert _counts() == (0, 0, 0)


# ---------------------------------------------------------------------------
# Form and list pages
# ---------------------------------------------------------------------------
def test_sale_form_lists_active_products_with_stock(logged_in, data):
    resp = logged_in.get("/sales/new")
    assert resp.status_code == 200
    assert b"Phone" in resp.data and b"10 in stock" in resp.data
    assert b"Cable" in resp.data
    assert b"Old TV" not in resp.data  # deactivated products cannot be sold


def test_sales_list_empty(logged_in, data):
    resp = logged_in.get("/sales")
    assert resp.status_code == 200
    assert b"No sales have been recorded yet." in resp.data


# ---------------------------------------------------------------------------
# Successful sales
# ---------------------------------------------------------------------------
def test_successful_sale_saves_everything_and_deducts_stock(logged_in, data):
    resp = _sell(logged_in, (data["phone"], 2))
    assert resp.status_code == 302
    assert "/sales/" in resp.headers["Location"]

    sale = db.session.query(Sale).one()
    item = db.session.query(SaleItem).one()
    movement = db.session.query(StockMovement).one()

    assert sale.user_id == data["user_id"]
    assert sale.status == "COMPLETED"
    assert sale.total_amount == Decimal("200.00")
    assert item.product_id == data["phone"]
    assert item.quantity == 2
    assert item.unit_price == Decimal("100.00")
    assert _stock(data["phone"]) == 8
    assert movement.movement_type == "OUT"
    assert movement.quantity == 2
    assert movement.product_id == data["phone"]
    assert movement.reference_id == sale.sale_id
    assert movement.user_id == data["user_id"]


def test_multi_item_sale_total_is_calculated_on_server(logged_in, data):
    _sell(logged_in, (data["phone"], 1), (data["cable"], 3))
    sale = db.session.query(Sale).one()
    assert sale.total_amount == Decimal("146.50")  # 100.00 + 3 x 15.50
    assert db.session.query(SaleItem).count() == 2
    assert db.session.query(StockMovement).count() == 2
    assert _stock(data["phone"]) == 9
    assert _stock(data["cable"]) == 0


def test_browser_submitted_price_and_total_are_ignored(logged_in, data):
    _sell(logged_in, (data["phone"], 1),
          unit_price="0.01", total_amount="1.00", total="1.00")
    sale = db.session.query(Sale).one()
    item = db.session.query(SaleItem).one()
    assert sale.total_amount == Decimal("100.00")
    assert item.unit_price == Decimal("100.00")


def test_selling_exactly_all_stock_is_allowed(logged_in, data):
    resp = _sell(logged_in, (data["cable"], 3))
    assert resp.status_code == 302
    assert _stock(data["cable"]) == 0


def test_blank_extra_rows_are_ignored(logged_in, data):
    resp = _sell(logged_in, (data["phone"], 1), ("", ""))
    assert resp.status_code == 302
    assert db.session.query(SaleItem).count() == 1


def test_price_is_captured_at_time_of_sale(logged_in, data):
    _sell(logged_in, (data["phone"], 1))
    db.session.get(Product, data["phone"]).unit_price = Decimal("120.00")
    db.session.commit()
    item = db.session.query(SaleItem).one()
    assert item.unit_price == Decimal("100.00")


def test_success_redirects_to_sale_details_with_message(logged_in, data):
    resp = logged_in.post(
        "/sales/new",
        data={"product_id": [str(data["phone"])], "quantity": ["2"]},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"recorded successfully" in resp.data
    assert b"Phone" in resp.data
    assert b"200.00" in resp.data


# ---------------------------------------------------------------------------
# Rejected sales (nothing must change)
# ---------------------------------------------------------------------------
def test_insufficient_stock_is_rejected_and_nothing_changes(logged_in, data):
    resp = _sell(logged_in, (data["cable"], 4))
    assert resp.status_code == 400
    assert b"Insufficient stock" in resp.data
    assert _counts() == (0, 0, 0)
    assert _stock(data["cable"]) == 3


def test_failed_item_rolls_back_earlier_items_in_same_sale(logged_in, data):
    # Phone is fine, cable is short: the phone deduction must be undone too.
    resp = _sell(logged_in, (data["phone"], 2), (data["cable"], 5))
    assert resp.status_code == 400
    assert _counts() == (0, 0, 0)
    assert _stock(data["phone"]) == 10
    assert _stock(data["cable"]) == 3


def test_duplicate_rows_for_same_product_are_checked_together(logged_in, data):
    # 2 + 2 = 4 cables, but only 3 in stock.
    resp = _sell(logged_in, (data["cable"], 2), (data["cable"], 2))
    assert resp.status_code == 400
    assert _stock(data["cable"]) == 3
    assert _counts() == (0, 0, 0)


def test_duplicate_rows_are_combined_into_one_item(logged_in, data):
    _sell(logged_in, (data["phone"], 1), (data["phone"], 2))
    item = db.session.query(SaleItem).one()
    assert item.quantity == 3
    assert _stock(data["phone"]) == 7


def test_product_without_inventory_record_is_rejected(logged_in, data):
    resp = _sell(logged_in, (data["charger"], 1))
    assert resp.status_code == 400
    assert _counts() == (0, 0, 0)


def test_inactive_product_is_rejected(logged_in, data):
    resp = _sell(logged_in, (data["old_tv"], 1))
    assert resp.status_code == 400
    assert _stock(data["old_tv"]) == 5
    assert _counts() == (0, 0, 0)


@pytest.mark.parametrize("bad_qty", ["0", "-1", "2.5", "abc", ""])
def test_invalid_quantity_is_rejected(logged_in, data, bad_qty):
    resp = _sell(logged_in, (data["phone"], bad_qty))
    assert resp.status_code == 400
    assert _counts() == (0, 0, 0)
    assert _stock(data["phone"]) == 10


@pytest.mark.parametrize("bad_pid", ["abc", "99999"])
def test_invalid_product_is_rejected(logged_in, data, bad_pid):
    resp = _sell(logged_in, (bad_pid, 1))
    assert resp.status_code == 400
    assert _counts() == (0, 0, 0)


def test_sale_with_no_items_is_rejected(logged_in, data):
    resp = logged_in.post("/sales/new", data={})
    assert resp.status_code == 400
    assert b"Add at least one product" in resp.data


def test_form_keeps_entered_rows_after_error(logged_in, data):
    resp = _sell(logged_in, (data["cable"], 9))
    assert resp.status_code == 400
    assert b'value="9"' in resp.data


def test_concurrent_sale_cannot_make_stock_negative(logged_in, data, monkeypatch):
    """Another sale takes the last cables just before this sale saves.

    The form was valid when submitted (3 in stock, asking for 3), but by the
    time the stock is reduced someone else has sold 2. The sale must be
    rejected, nothing saved, and stock must never go below zero.
    """
    from sqlalchemy import update
    import app.sales.routes as sales_routes

    real_reduce = sales_routes.reduce_stock

    def other_sale_first(product_id, quantity):
        db.session.execute(
            update(Inventory)
            .where(Inventory.product_id == product_id)
            .values(quantity_on_hand=Inventory.quantity_on_hand - 2)
        )
        return real_reduce(product_id, quantity)

    monkeypatch.setattr(sales_routes, "reduce_stock", other_sale_first)
    resp = _sell(logged_in, (data["cable"], 3))
    monkeypatch.undo()

    assert resp.status_code == 400
    assert b"Insufficient stock" in resp.data
    assert _counts() == (0, 0, 0)
    assert _stock(data["cable"]) >= 0


def test_two_sales_for_the_last_items_only_one_succeeds(logged_in, data):
    first = _sell(logged_in, (data["cable"], 3))
    second = _sell(logged_in, (data["cable"], 3))
    assert first.status_code == 302
    assert second.status_code == 400
    assert _stock(data["cable"]) == 0
    assert db.session.query(Sale).count() == 1


def test_database_error_rolls_back_everything(logged_in, data, monkeypatch):
    def failing_commit():
        raise SQLAlchemyError("simulated failure")

    monkeypatch.setattr(db.session, "commit", failing_commit)
    resp = _sell(logged_in, (data["phone"], 2))
    monkeypatch.undo()

    assert resp.status_code == 500
    assert b"No sale or stock changes were saved" in resp.data
    db.session.rollback()
    assert _counts() == (0, 0, 0)
    assert _stock(data["phone"]) == 10


# ---------------------------------------------------------------------------
# Viewing sales
# ---------------------------------------------------------------------------
def test_view_sale_shows_items_and_total(logged_in, data):
    _sell(logged_in, (data["phone"], 1), (data["cable"], 2))
    sale_id = db.session.query(Sale.sale_id).scalar()
    resp = logged_in.get(f"/sales/{sale_id}")
    assert resp.status_code == 200
    assert b"Phone" in resp.data and b"Cable" in resp.data
    assert b"31.00" in resp.data   # cable line total 2 x 15.50
    assert b"131.00" in resp.data  # sale total


def test_view_unknown_sale_returns_404(logged_in, data):
    assert logged_in.get("/sales/9999").status_code == 404


def test_sales_list_shows_recorded_sales(logged_in, data):
    _sell(logged_in, (data["phone"], 1))
    _sell(logged_in, (data["cable"], 1))
    resp = logged_in.get("/sales")
    assert resp.status_code == 200
    assert b"100.00" in resp.data
    assert b"15.50" in resp.data
    assert b"sales_tester" in resp.data
