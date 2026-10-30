import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Category, Product, User


@pytest.fixture
def security_app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "nfr-security-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def security_data(security_app):
    with security_app.app_context():
        user = User(
            username="security_tester",
            password_hash=generate_password_hash("test-password"),
            role="Store Staff",
            is_active=True,
        )
        inactive_user = User(
            username="inactive_tester",
            password_hash=generate_password_hash("test-password"),
            role="Store Staff",
            is_active=False,
        )
        category = Category(name="Security Test Category")
        db.session.add_all([user, inactive_user, category])
        db.session.flush()
        product = Product(
            sku="SEC-001",
            name="Security Test Product",
            category_id=category.category_id,
            unit_price=10,
            reorder_level=1,
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()
        return {
            "user_id": user.user_id,
            "inactive_username": inactive_user.username,
            "product_id": product.product_id,
            "password_hash": user.password_hash,
        }


@pytest.fixture
def authenticated_client(security_app, security_data):
    client = security_app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(security_data["user_id"])
        session["_fresh"] = True
    return client


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard",
        "/products",
        "/inventory",
        "/inventory/low-stock",
        "/purchases/",
        "/sales",
        "/reports/inventory",
        "/reports/sales",
    ],
)
def test_protected_pages_require_authentication(security_app, path):
    response = security_app.test_client().get(path)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_inactive_user_cannot_authenticate(security_app, security_data):
    response = security_app.test_client().post(
        "/login",
        data={
            "username": security_data["inactive_username"],
            "password": "test-password",
        },
    )
    assert response.status_code == 401


def test_password_is_stored_as_a_hash(security_data):
    stored = security_data["password_hash"]
    assert stored != "test-password"
    assert check_password_hash(stored, "test-password")


def test_logout_invalidates_session_and_protects_dashboard(
    authenticated_client,
):
    response = authenticated_client.post("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    dashboard = authenticated_client.get("/dashboard")
    assert dashboard.status_code == 302
    assert "/login" in dashboard.headers["Location"]


def test_invalid_product_input_is_rejected_without_modification(
    authenticated_client, security_data
):
    response = authenticated_client.post(
        f"/products/{security_data['product_id']}/edit",
        data={
            "name": "",
            "sku": "SEC-001",
            "category_id": "1",
            "unit_price": "10.00",
            "reorder_level": "1",
        },
    )
    assert response.status_code == 400

    with authenticated_client.application.app_context():
        product = db.session.get(Product, security_data["product_id"])
        assert product.name == "Security Test Product"


@pytest.mark.parametrize(
    ("method", "path", "data"),
    [
        ("post", "/products/{product_id}/deactivate", {}),
        ("post", "/purchases/new", {}),
        ("post", "/sales/new", {}),
    ],
)
def test_unauthenticated_modifications_are_rejected(
    security_app, security_data, method, path, data
):
    path = path.format(product_id=security_data["product_id"])
    response = getattr(security_app.test_client(), method)(path, data=data)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    with security_app.app_context():
        product = db.session.get(Product, security_data["product_id"])
        assert product.is_active is True
