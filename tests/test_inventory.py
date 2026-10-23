"""Tests for the inventory module (Member 4, GitHub issue #5, ESIMS-F-005 to F-008).

Self-contained on purpose: this file builds its own test app on an in-memory
SQLite database and defines its own fixtures (prefixed inv_), so it never
depends on or clashes with anyone else's tests/conftest.py.

Part 1 tests the validation helpers (no database).
Part 2 tests the pages and the stock-reduction function.
"""
import pytest

from app.inventory.routes import (
    StockValidationError,
    check_sufficient_stock,
    is_low_stock,
    parse_quantity,
    reduce_stock,
    validate_stock_level,
)


# ---------- Part 1: validation (no database needed) ----------

@pytest.mark.parametrize("raw, expected", [("5", 5), (" 12 ", 12), (3, 3)])
def test_parse_quantity_accepts_positive_whole_numbers(raw, expected):
    assert parse_quantity(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None, "0", "-3", "2.5", "abc"])
def test_parse_quantity_rejects_invalid_input(raw):
    with pytest.raises(StockValidationError):
        parse_quantity(raw)


@pytest.mark.parametrize("qty", [0, 1, 500])
def test_validate_stock_level_accepts_zero_and_positive(qty):
    assert validate_stock_level(qty) == qty


@pytest.mark.parametrize("qty", [-1, 2.5, "10", None, True])
def test_validate_stock_level_rejects_invalid(qty):
    with pytest.raises(StockValidationError):
        validate_stock_level(qty)


def test_check_sufficient_stock_returns_remaining():
    assert check_sufficient_stock(10, 4) == 6


def test_check_sufficient_stock_allows_exact_amount():
    assert check_sufficient_stock(5, 5) == 0


def test_check_sufficient_stock_rejects_too_much():
    with pytest.raises(StockValidationError, match="Insufficient stock"):
        check_sufficient_stock(3, 4)


@pytest.mark.parametrize("requested", [0, -2])
def test_check_sufficient_stock_rejects_non_positive_request(requested):
    with pytest.raises(StockValidationError):
        check_sufficient_stock(10, requested)


@pytest.mark.parametrize(
    "qty, reorder, expected",
    [(0, 5, True), (5, 5, True), (6, 5, False), (0, 0, True)],
)
def test_is_low_stock_threshold(qty, reorder, expected):
    assert is_low_stock(qty, reorder) is expected


# ---------- Part 2: pages and database (own fixtures, no shared conftest) ----------

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app import create_app
    from app.extensions import db
    from app.inventory.routes import inventory_bp

    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    # Works before and after the team registers inventory_bp in app/__init__.py.
    if "inventory" not in application.blueprints:
        application.register_blueprint(inventory_bp)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(app, client):
    """Logs in through Flask-Login's session key, as Member 1's auth does."""
    from app.extensions import db
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User(username="inv_tester", password_hash=generate_password_hash("x"),
                role="Store Staff", is_active=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.user_id)
        sess["_fresh"] = True
    return client


def _seed(db):
    from app.models import Category, Inventory, Product

    cat = Category(name="Phones")
    db.session.add(cat)
    db.session.flush()
    plenty = Product(sku="SKU-OK", name="Plenty Phone", category_id=cat.category_id,
                     unit_price=100, reorder_level=5, is_active=True)
    low = Product(sku="SKU-LOW", name="Scarce Phone", category_id=cat.category_id,
                  unit_price=100, reorder_level=5, is_active=True)
    gone = Product(sku="SKU-OFF", name="Retired Phone", category_id=cat.category_id,
                   unit_price=100, reorder_level=5, is_active=False)
    db.session.add_all([plenty, low, gone])
    db.session.flush()
    db.session.add_all([
        Inventory(product_id=plenty.product_id, quantity_on_hand=50),
        Inventory(product_id=low.product_id, quantity_on_hand=2),
        Inventory(product_id=gone.product_id, quantity_on_hand=0),
    ])
    db.session.commit()


def _qty(db, sku):
    from app.models import Inventory, Product
    return (db.session.query(Inventory.quantity_on_hand)
            .join(Product, Product.product_id == Inventory.product_id)
            .filter(Product.sku == sku).scalar())


def _pid(db, sku):
    from app.models import Product
    return db.session.query(Product.product_id).filter(Product.sku == sku).scalar()


def test_inventory_requires_login(client):
    resp = client.get("/inventory")
    assert resp.status_code in (302, 401)


def test_low_stock_requires_login(client):
    resp = client.get("/inventory/low-stock")
    assert resp.status_code in (302, 401)


def test_inventory_lists_active_products_with_stock(app, logged_in_client):
    from app.extensions import db
    _seed(db)
    resp = logged_in_client.get("/inventory")
    assert resp.status_code == 200
    assert b"Plenty Phone" in resp.data and b"50" in resp.data
    assert b"Scarce Phone" in resp.data
    assert b"Retired Phone" not in resp.data


def test_inventory_search_by_name(app, logged_in_client):
    from app.extensions import db
    _seed(db)
    resp = logged_in_client.get("/inventory?q=scarce")
    assert b"Scarce Phone" in resp.data
    assert b"Plenty Phone" not in resp.data


def test_inventory_search_by_sku(app, logged_in_client):
    from app.extensions import db
    _seed(db)
    resp = logged_in_client.get("/inventory?q=SKU-OK")
    assert b"Plenty Phone" in resp.data
    assert b"Scarce Phone" not in resp.data


def test_low_stock_shows_only_low_items(app, logged_in_client):
    from app.extensions import db
    _seed(db)
    resp = logged_in_client.get("/inventory/low-stock")
    assert resp.status_code == 200
    assert b"Scarce Phone" in resp.data
    assert b"Plenty Phone" not in resp.data
    assert b"Retired Phone" not in resp.data


def test_reduce_stock_subtracts(app):
    from app.extensions import db
    _seed(db)
    reduce_stock(_pid(db, "SKU-OK"), 20)
    db.session.commit()
    assert _qty(db, "SKU-OK") == 30


def test_reduce_stock_to_exactly_zero(app):
    from app.extensions import db
    _seed(db)
    reduce_stock(_pid(db, "SKU-LOW"), 2)
    db.session.commit()
    assert _qty(db, "SKU-LOW") == 0


def test_reduce_stock_rejects_going_negative_and_changes_nothing(app):
    from app.extensions import db
    _seed(db)
    with pytest.raises(StockValidationError, match="Insufficient stock"):
        reduce_stock(_pid(db, "SKU-LOW"), 3)
    db.session.rollback()
    assert _qty(db, "SKU-LOW") == 2


@pytest.mark.parametrize("bad", [0, -1, 1.5, "2", True])
def test_reduce_stock_rejects_invalid_quantity(app, bad):
    from app.extensions import db
    _seed(db)
    with pytest.raises(StockValidationError):
        reduce_stock(_pid(db, "SKU-OK"), bad)


def test_reduce_stock_ignores_stale_reads(app):
    """Two sales both saw 2 in stock and each try to sell 2.
    Only the first may succeed; stock must never go below 0."""
    from app.extensions import db
    _seed(db)
    pid = _pid(db, "SKU-LOW")
    assert _qty(db, "SKU-LOW") == 2   # both "sales" read 2
    reduce_stock(pid, 2)              # first sale succeeds
    db.session.commit()
    with pytest.raises(StockValidationError):
        reduce_stock(pid, 2)          # second sale's stale check is not trusted
    db.session.rollback()
    assert _qty(db, "SKU-LOW") == 0
