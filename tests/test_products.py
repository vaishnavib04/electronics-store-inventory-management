"""Tests for Member 2's product management and Sprint 2 integration (UI-001)."""

from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app import create_app
    from app.extensions import db

    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def logged_in_client(app):
    from app.extensions import db
    from app.models import Category, User

    user = User(
        username="product_tester",
        password_hash=generate_password_hash("test-password"),
        role="Store Staff",
        is_active=True,
    )
    category = Category(name="Electronics")
    db.session.add_all([user, category])
    db.session.commit()

    client = app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)
        session["_fresh"] = True
    return client, category.category_id


def _form(default_category_id, **overrides):
    values = {
        "name": "Wireless Mouse",
        "sku": "MOUSE-001",
        "category_id": str(default_category_id),
        "unit_price": "24.50",
        "reorder_level": "5",
    }
    values.update(overrides)
    return values


def test_product_pages_require_login(app):
    response = app.test_client().get("/products")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_create_list_view_and_edit_product(logged_in_client):
    client, category_id = logged_in_client

    response = client.post("/products/new", data=_form(category_id))
    assert response.status_code == 302
    assert "/products/1" in response.headers["Location"]

    listing = client.get("/products?q=MOUSE-001")
    assert listing.status_code == 200
    assert b"Wireless Mouse" in listing.data

    details = client.get("/products/1")
    assert details.status_code == 200
    assert b"Electronics" in details.data
    assert b"24.50" in details.data

    updated = client.post(
        "/products/1/edit",
        data=_form(category_id, name="Wireless Mouse Pro", unit_price="29.99"),
    )
    assert updated.status_code == 302
    assert b"Wireless Mouse Pro" in client.get("/products/1").data


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"name": "   "}, "Product name is required."),
        ({"name": "A" * 151}, "Product name must be 150 characters or fewer."),
        ({"sku": ""}, "SKU is required."),
        ({"sku": "S" * 81}, "SKU must be 80 characters or fewer."),
        ({"unit_price": "-1"}, "Unit price must be a valid non-negative amount."),
        ({"unit_price": "NaN"}, "Unit price must be a valid non-negative amount."),
        ({"unit_price": "1.239"}, "Unit price can have at most two decimal places."),
        ({"unit_price": "100000000.00"}, "Unit price is too large."),
        ({"reorder_level": "-1"}, "Reorder level must be a whole number of 0 or more."),
        ({"reorder_level": "1.5"}, "Reorder level must be a whole number of 0 or more."),
        ({"category_id": "999"}, "Please select a valid category."),
        ({"category_id": "abc"}, "Please select a valid category."),
    ],
)
def test_create_rejects_invalid_product_values(logged_in_client, changes, message):
    client, category_id = logged_in_client
    response = client.post("/products/new", data=_form(category_id, **changes))
    assert response.status_code == 400
    assert message.encode() in response.data


def test_duplicate_skus_are_rejected_case_insensitively(logged_in_client):
    client, category_id = logged_in_client
    assert client.post("/products/new", data=_form(category_id)).status_code == 302

    response = client.post(
        "/products/new", data=_form(category_id, name="Another Mouse", sku="mouse-001")
    )
    assert response.status_code == 400
    assert b"That SKU is already in use" in response.data


def test_deactivate_is_a_post_and_keeps_record(logged_in_client, app):
    from app.extensions import db
    from app.models import Product

    client, category_id = logged_in_client
    client.post("/products/new", data=_form(category_id))

    response = client.post("/products/1/deactivate")
    assert response.status_code == 302
    assert client.get("/products").status_code == 200
    assert b"Wireless Mouse" not in client.get("/products").data
    with app.app_context():
        product = db.session.get(Product, 1)
        assert product is not None
        assert product.is_active is False


# ---------------------------------------------------------------------------
# Sprint 2: Product & Inventory Integration and Regression Tests (Member 2)
# ---------------------------------------------------------------------------
def test_deactivated_product_routes_return_404(logged_in_client):
    client, category_id = logged_in_client
    client.post("/products/new", data=_form(category_id))
    client.post("/products/1/deactivate")

    assert client.get("/products/1").status_code == 404
    assert client.get("/products/1/edit").status_code == 404
    assert client.post("/products/1/edit", data=_form(category_id)).status_code == 404
    assert client.post("/products/1/deactivate").status_code == 404


def test_product_inventory_integration_across_purchases_and_sales(logged_in_client, app):
    """Verify product quantities display accurately across product detail,
    inventory listing, and low-stock pages after purchase and sale transactions."""
    from app.extensions import db
    from app.models import Supplier

    client, category_id = logged_in_client
    with app.app_context():
        supplier = Supplier(name="Integration Supplier", is_active=True)
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.supplier_id

    # 1. Create product with reorder_level = 5 (initially 0 in stock -> low stock)
    resp = client.post(
        "/products/new",
        data=_form(category_id, name="USB-C Hub", sku="HUB-100", unit_price="40.00", reorder_level="5"),
    )
    assert resp.status_code == 302

    inv_page = client.get("/inventory?q=HUB-100")
    assert inv_page.status_code == 200
    assert b"USB-C Hub" in inv_page.data
    assert b"Low stock" in inv_page.data
    assert b"USB-C Hub" in client.get("/inventory/low-stock").data

    # 2. Record a purchase of 10 units -> stock becomes 10 (> reorder_level 5 -> OK)
    purchase_resp = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(supplier_id),
            "product_id": ["1"],
            "quantity": ["10"],
            "unit_cost": ["20.00"],
        },
        follow_redirects=True,
    )
    assert purchase_resp.status_code == 200
    assert b"Purchase recorded successfully." in purchase_resp.data

    detail_after_purchase = client.get("/products/1")
    assert b"<dd>10</dd>" in detail_after_purchase.data
    assert b"USB-C Hub" not in client.get("/inventory/low-stock").data

    # 3. Record a sale of 7 units -> stock becomes 3 (<= reorder_level 5 -> Low stock again)
    sale_resp = client.post(
        "/sales/new",
        data={"product_id": ["1"], "quantity": ["7"]},
        follow_redirects=True,
    )
    assert sale_resp.status_code == 200
    assert b"recorded successfully" in sale_resp.data

    detail_after_sale = client.get("/products/1")
    assert b"<dd>3</dd>" in detail_after_sale.data
    assert b"USB-C Hub" in client.get("/inventory/low-stock").data


def test_inactive_product_handled_consistently_across_modules(logged_in_client, app):
    """Deactivating a product hides it from product listing, inventory, low-stock,
    inventory report, and transaction forms, and rejects new purchases/sales."""
    from app.extensions import db
    from app.models import Inventory, Product, Supplier

    client, category_id = logged_in_client
    with app.app_context():
        supplier = Supplier(name="Test Supplier", is_active=True)
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.supplier_id

    client.post(
        "/products/new",
        data=_form(category_id, name="Legacy Monitor", sku="MON-OLD", reorder_level="5"),
    )
    with app.app_context():
        db.session.add(Inventory(product_id=1, quantity_on_hand=2))
        db.session.commit()

    client.post("/products/1/deactivate")

    assert b"Legacy Monitor" not in client.get("/products").data
    assert b"Legacy Monitor" not in client.get("/inventory").data
    assert b"Legacy Monitor" not in client.get("/inventory/low-stock").data
    assert b"Legacy Monitor" not in client.get("/reports/inventory").data
    assert b"Legacy Monitor" not in client.get("/purchases/new").data
    assert b"Legacy Monitor" not in client.get("/sales/new").data

    # Attempting to purchase or sell a deactivated product must be rejected
    bad_purchase = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(supplier_id),
            "product_id": ["1"],
            "quantity": ["5"],
            "unit_cost": ["10.00"],
        },
    )
    assert bad_purchase.status_code == 400
    assert b"Please select an active product." in bad_purchase.data

    bad_sale = client.post(
        "/sales/new",
        data={"product_id": ["1"], "quantity": ["1"]},
    )
    assert bad_sale.status_code == 400
    assert b"Please select an active product." in bad_sale.data

    with app.app_context():
        assert db.session.get(Product, 1).is_active is False


def test_ui_integration_shared_navigation_and_feedback(logged_in_client):
    """Verify [UI-001] shared base layout, navigation links, and flash feedback."""
    client, category_id = logged_in_client
    for path in [
        "/dashboard",
        "/products",
        "/inventory",
        "/inventory/low-stock",
        "/suppliers/",
        "/purchases/",
        "/sales",
        "/reports/inventory",
        "/reports/sales",
    ]:
        resp = client.get(path)
        assert resp.status_code == 200
        assert b"Electronics Store Inventory Management System" in resp.data
        assert b'aria-label="Main navigation"' in resp.data
