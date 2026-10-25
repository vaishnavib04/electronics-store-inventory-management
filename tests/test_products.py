"""Tests for Member 2's product management module."""

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
        ({"sku": ""}, "SKU is required."),
        ({"unit_price": "-1"}, "Unit price must be a valid non-negative amount."),
        ({"unit_price": "1.239"}, "Unit price can have at most two decimal places."),
        ({"reorder_level": "-1"}, "Reorder level must be a whole number of 0 or more."),
        ({"reorder_level": "1.5"}, "Reorder level must be a whole number of 0 or more."),
        ({"category_id": "999"}, "Please select a valid category."),
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
