
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, UniqueConstraint
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="Store Staff")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    purchases = db.relationship("Purchase", back_populates="user")
    sales = db.relationship("Sale", back_populates="user")
    stock_movements = db.relationship("StockMovement", back_populates="user")


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship("Product", back_populates="category")


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="ck_product_unit_price"),
        CheckConstraint("reorder_level >= 0", name="ck_product_reorder_level"),
    )

    product_id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.category_id"), nullable=False
    )
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    reorder_level = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    category = db.relationship("Category", back_populates="products")
    inventory = db.relationship(
        "Inventory", back_populates="product", uselist=False
    )
    purchase_items = db.relationship("PurchaseItem", back_populates="product")
    sale_items = db.relationship("SaleItem", back_populates="product")
    stock_movements = db.relationship("StockMovement", back_populates="product")


class Inventory(db.Model):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint(
            "quantity_on_hand >= 0", name="ck_inventory_quantity_nonnegative"
        ),
    )

    inventory_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.product_id"),
        unique=True, nullable=False
    )
    quantity_on_hand = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    product = db.relationship("Product", back_populates="inventory")


class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    address = db.Column(db.Text)

    purchases = db.relationship("Purchase", back_populates="supplier")


class Purchase(db.Model):
    __tablename__ = "purchases"
    __table_args__ = (
        CheckConstraint("total_cost >= 0", name="ck_purchase_total_cost"),
    )

    purchase_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(
        db.Integer, db.ForeignKey("suppliers.supplier_id"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_cost = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    supplier = db.relationship("Supplier", back_populates="purchases")
    user = db.relationship("User", back_populates="purchases")
    items = db.relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_purchase_item_quantity"),
        CheckConstraint("unit_cost >= 0", name="ck_purchase_item_unit_cost"),
    )

    purchase_item_id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(
        db.Integer, db.ForeignKey("purchases.purchase_id"), nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.product_id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)

    purchase = db.relationship("Purchase", back_populates="items")
    product = db.relationship("Product", back_populates="purchase_items")


class Sale(db.Model):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_sale_total_amount"),
    )

    sale_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    sale_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(
        db.Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    status = db.Column(db.String(30), nullable=False, default="COMPLETED")

    user = db.relationship("User", back_populates="sales")
    items = db.relationship("SaleItem", back_populates="sale")


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_item_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_sale_item_unit_price"),
    )

    sale_item_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(
        db.Integer, db.ForeignKey("sales.sale_id"), nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.product_id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product", back_populates="sale_items")


class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_movement_quantity"),
        CheckConstraint(
            "movement_type IN ('IN', 'OUT')", name="ck_stock_movement_type"
        ),
    )

    movement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.product_id"), nullable=False
    )
    movement_type = db.Column(db.String(3), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.Integer)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship("Product", back_populates="stock_movements")
    user = db.relationship("User", back_populates="stock_movements")
