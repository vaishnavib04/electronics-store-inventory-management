
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Supplier, User


@pytest.fixture
def supplier_app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def supplier_client(supplier_app):
    return supplier_app.test_client()


@pytest.fixture
def supplier_logged_in_client(supplier_app, supplier_client):
    with supplier_app.app_context():
        user = User(
            username="supplier_tester",
            password_hash=generate_password_hash("test-password"),
            role="Store Staff",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.user_id

    with supplier_client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True

    return supplier_client


def test_supplier_creation_success(supplier_app, supplier_logged_in_client):
    response = supplier_logged_in_client.post(
        "/suppliers/add",
        data={
            "name": "Test Electronics Supplier",
            "contact_person": "Test Contact",
            "phone": "9876543210",
            "email": "supplier@example.com",
            "address": "Bengaluru",
        },
    )

    assert response.status_code == 302

    with supplier_app.app_context():
        supplier = db.session.execute(
            db.select(Supplier).where(
                Supplier.name == "Test Electronics Supplier"
            )
        ).scalar_one()

        assert supplier.contact_person == "Test Contact"
        assert supplier.phone == "9876543210"
        assert supplier.email == "supplier@example.com"
        assert supplier.address == "Bengaluru"


def test_supplier_edit_success(supplier_app, supplier_logged_in_client):
    with supplier_app.app_context():
        supplier = Supplier(
            name="Old Supplier Name",
            phone="9876543210",
            email="old@example.com",
        )
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.supplier_id

    response = supplier_logged_in_client.post(
        f"/suppliers/{supplier_id}/edit",
        data={
            "name": "Updated Supplier Name",
            "contact_person": "Updated Contact",
            "phone": "9123456780",
            "email": "updated@example.com",
            "address": "Mysuru",
        },
    )

    assert response.status_code == 302

    with supplier_app.app_context():
        updated_supplier = db.session.get(Supplier, supplier_id)

        assert updated_supplier.name == "Updated Supplier Name"
        assert updated_supplier.contact_person == "Updated Contact"
        assert updated_supplier.phone == "9123456780"
        assert updated_supplier.email == "updated@example.com"
        assert updated_supplier.address == "Mysuru"


def test_supplier_creation_rejects_missing_name(
    supplier_app, supplier_logged_in_client
):
    response = supplier_logged_in_client.post(
        "/suppliers/add",
        data={
            "name": "   ",
            "phone": "9876543210",
            "email": "supplier@example.com",
        },
    )

    assert response.status_code == 400

    with supplier_app.app_context():
        assert db.session.execute(
            db.select(Supplier)
        ).scalars().all() == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("phone", "abc123"),
        ("email", "not-an-email"),
    ],
)
def test_supplier_creation_rejects_invalid_phone_or_email(
    supplier_app, supplier_logged_in_client, field, value
):
    data = {
        "name": "Invalid Details Supplier",
        "phone": "9876543210",
        "email": "supplier@example.com",
    }
    data[field] = value

    response = supplier_logged_in_client.post(
        "/suppliers/add",
        data=data,
    )

    assert response.status_code == 400

    with supplier_app.app_context():
        assert db.session.execute(
            db.select(Supplier)
        ).scalars().all() == []


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/suppliers/"),
        ("get", "/suppliers/add"),
        ("post", "/suppliers/add"),
    ],
)
def test_supplier_routes_require_login(supplier_client, method, path):
    response = getattr(supplier_client, method)(path)

    assert response.status_code == 302
    assert "login" in response.headers["Location"].lower()
