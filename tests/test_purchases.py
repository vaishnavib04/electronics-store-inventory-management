
from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (
    Category,
    Inventory,
    Product,
    Purchase,
    PurchaseItem,
    StockMovement,
    Supplier,
    User,
)


@pytest.fixture
def purchase_app(monkeypatch):
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
def purchase_client(purchase_app):
    return purchase_app.test_client()


@pytest.fixture
def purchase_setup(purchase_app, purchase_client):
    with purchase_app.app_context():
        user = User(
            username="purchase_tester",
            password_hash=generate_password_hash("test-password"),
            role="Store Staff",
            is_active=True,
        )
        supplier = Supplier(
            name="Test Supplier",
            is_active=True,
        )
        category = Category(name="Test Category")

        db.session.add_all([user, supplier, category])
        db.session.flush()

        product = Product(
            sku="PUR-001",
            name="Test Keyboard",
            category_id=category.category_id,
            unit_price=Decimal("50.00"),
            reorder_level=5,
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()

        user_id = user.user_id
        supplier_id = supplier.supplier_id
        product_id = product.product_id

    with purchase_client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True

    return {
        "client": purchase_client,
        "user_id": user_id,
        "supplier_id": supplier_id,
        "product_id": product_id,
    }


def test_purchase_pages_require_login(purchase_app, purchase_client):
    response = purchase_client.get("/purchases/")
    assert response.status_code == 302

    response = purchase_client.get("/purchases/new")
    assert response.status_code == 302


def test_purchase_creation_updates_inventory_and_records_movement(
    purchase_app, purchase_setup
):
    client = purchase_setup["client"]

    response = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(purchase_setup["supplier_id"]),
            "product_id": [str(purchase_setup["product_id"])],
            "quantity": ["4"],
            "unit_cost": ["25.50"],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Purchase recorded successfully." in response.data

    with purchase_app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()

        item = db.session.execute(
            db.select(PurchaseItem)
        ).scalar_one()

        inventory = db.session.execute(
            db.select(Inventory).where(
                Inventory.product_id == purchase_setup["product_id"]
            )
        ).scalar_one()

        movement = db.session.execute(
            db.select(StockMovement)
        ).scalar_one()

        assert purchase.supplier_id == purchase_setup["supplier_id"]
        assert purchase.user_id == purchase_setup["user_id"]
        assert purchase.total_cost == Decimal("102.00")

        assert item.product_id == purchase_setup["product_id"]
        assert item.quantity == 4
        assert item.unit_cost == Decimal("25.50")

        assert inventory.quantity_on_hand == 4

        assert movement.movement_type == "IN"
        assert movement.quantity == 4
        assert movement.reference_id == purchase.purchase_id
        assert movement.user_id == purchase_setup["user_id"]


def test_purchase_adds_to_existing_inventory(
    purchase_app, purchase_setup
):
    with purchase_app.app_context():
        inventory = Inventory(
            product_id=purchase_setup["product_id"],
            quantity_on_hand=6,
        )
        db.session.add(inventory)
        db.session.commit()

    response = purchase_setup["client"].post(
        "/purchases/new",
        data={
            "supplier_id": str(purchase_setup["supplier_id"]),
            "product_id": [str(purchase_setup["product_id"])],
            "quantity": ["3"],
            "unit_cost": ["10.00"],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with purchase_app.app_context():
        inventory = db.session.execute(
            db.select(Inventory).where(
                Inventory.product_id == purchase_setup["product_id"]
            )
        ).scalar_one()

        assert inventory.quantity_on_hand == 9


@pytest.mark.parametrize(
    ("quantity", "unit_cost"),
    [
        ("0", "10.00"),
        ("-2", "10.00"),
        ("1.5", "10.00"),
        ("2", "-1.00"),
        ("2", "10.999"),
        ("2", "invalid"),
    ],
)
def test_invalid_purchase_does_not_change_database(
    purchase_app, purchase_setup, quantity, unit_cost
):
    response = purchase_setup["client"].post(
        "/purchases/new",
        data={
            "supplier_id": str(purchase_setup["supplier_id"]),
            "product_id": [str(purchase_setup["product_id"])],
            "quantity": [quantity],
            "unit_cost": [unit_cost],
        },
    )

    assert response.status_code == 400

    with purchase_app.app_context():
        assert db.session.execute(
            db.select(Purchase)
        ).scalars().all() == []

        assert db.session.execute(
            db.select(PurchaseItem)
        ).scalars().all() == []

        assert db.session.execute(
            db.select(StockMovement)
        ).scalars().all() == []

        assert db.session.execute(
            db.select(Inventory)
        ).scalars().all() == []
