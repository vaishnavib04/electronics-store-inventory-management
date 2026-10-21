
from sqlalchemy import CheckConstraint

from app.models import (
    User, Category, Product, Inventory, Supplier,
    Purchase, PurchaseItem, Sale, SaleItem, StockMovement
)


def test_all_ten_models_exist():
    models = [
        User, Category, Product, Inventory, Supplier,
        Purchase, PurchaseItem, Sale, SaleItem, StockMovement
    ]
    assert len(models) == 10
    assert len({model.__tablename__ for model in models}) == 10


def test_primary_keys_and_table_names():
    expected = {
        User: ("users", "user_id"),
        Category: ("categories", "category_id"),
        Product: ("products", "product_id"),
        Inventory: ("inventory", "inventory_id"),
        Supplier: ("suppliers", "supplier_id"),
        Purchase: ("purchases", "purchase_id"),
        PurchaseItem: ("purchase_items", "purchase_item_id"),
        Sale: ("sales", "sale_id"),
        SaleItem: ("sale_items", "sale_item_id"),
        StockMovement: ("stock_movements", "movement_id"),
    }

    for model, (table_name, primary_key) in expected.items():
        assert model.__tablename__ == table_name
        assert list(model.__table__.primary_key.columns.keys()) == [primary_key]


def test_required_relationships_and_unique_fields():
    assert User.username.unique
    assert Category.name.unique
    assert Product.sku.unique
    assert Inventory.product_id.unique

    assert Product.category_id.foreign_keys
    assert Inventory.product_id.foreign_keys
    assert Purchase.supplier_id.foreign_keys
    assert Purchase.user_id.foreign_keys
    assert PurchaseItem.purchase_id.foreign_keys
    assert PurchaseItem.product_id.foreign_keys
    assert Sale.user_id.foreign_keys
    assert SaleItem.sale_id.foreign_keys
    assert SaleItem.product_id.foreign_keys
    assert StockMovement.product_id.foreign_keys
    assert StockMovement.user_id.foreign_keys


def test_database_check_constraints():
    constrained_models = [
        Product, Inventory, Purchase, PurchaseItem,
        Sale, SaleItem, StockMovement
    ]

    for model in constrained_models:
        assert any(
            isinstance(constraint, CheckConstraint)
            for constraint in model.__table__.constraints
        ), f"{model.__name__} is missing check constraints"
