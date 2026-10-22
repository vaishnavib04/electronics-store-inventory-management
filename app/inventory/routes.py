"""
Inventory module (Member 4) — ESIMS-F-005 to F-008.

Routes (agreed names, do not rename):
    GET /inventory            -> list_inventory()
    GET /inventory/low-stock  -> low_stock_report()

GitHub issue #5. Acceptance criteria covered:
    - stock shown per product, read from the database   -> list_inventory()
    - search by name or SKU                              -> list_inventory() ?q=
    - at-or-below reorder level identified               -> low_stock_report(), is_low_stock()
    - reductions that would go negative are rejected     -> reduce_stock()
    - concurrent reductions cannot go negative           -> reduce_stock() (single atomic UPDATE)

Shared helpers for Sprint 2 sales (and Member 3's purchases):
    from app.inventory.routes import reduce_stock, check_sufficient_stock, StockValidationError

Models: matches Member 1's DB-001 PR (#14) exactly. Verified, no changes needed.

Login: uses Flask-Login's login_required, as in Member 1's auth PR (#16).
Note: this blueprint has NO url_prefix, because the routes already start with /inventory.
"""
from flask import Blueprint, render_template, request
from sqlalchemy import or_, select, update

from app.extensions import db
from app.models import Product, Inventory
from flask_login import login_required  # Member 1's auth (PR #16) uses Flask-Login

inventory_bp = Blueprint("inventory", __name__)


# ---------------------------------------------------------------------------
# Stock validation helpers (pure functions: no database, easy to unit-test)
# ---------------------------------------------------------------------------
class StockValidationError(ValueError):
    """Raised when a stock quantity or stock change is invalid."""


def _is_int(value):
    # bool is a subclass of int in Python; True must not count as 1 unit.
    return isinstance(value, int) and not isinstance(value, bool)


def parse_quantity(raw, field_name="Quantity"):
    """Turn form input into a positive whole number, or raise StockValidationError."""
    if raw is None or str(raw).strip() == "":
        raise StockValidationError(f"{field_name} is required.")
    text = str(raw).strip()
    try:
        value = int(text)
    except ValueError:
        raise StockValidationError(f"{field_name} must be a whole number.")
    if value <= 0:
        raise StockValidationError(f"{field_name} must be greater than 0.")
    return value


def validate_stock_level(quantity_on_hand):
    """inventory.quantity_on_hand must be a whole number >= 0."""
    if not _is_int(quantity_on_hand):
        raise StockValidationError("Stock quantity must be a whole number.")
    if quantity_on_hand < 0:
        raise StockValidationError("Stock quantity cannot be negative.")
    return quantity_on_hand


def check_sufficient_stock(available, requested):
    """Return the remaining stock after removing `requested`, or raise if not enough."""
    validate_stock_level(available)
    if not _is_int(requested) or requested <= 0:
        raise StockValidationError("Requested quantity must be greater than 0.")
    if requested > available:
        raise StockValidationError(
            f"Insufficient stock: requested {requested}, only {available} available."
        )
    return available - requested


def is_low_stock(quantity_on_hand, reorder_level):
    """Agreed threshold: low stock when quantity on hand <= the product's reorder_level."""
    return quantity_on_hand <= reorder_level


# ---------------------------------------------------------------------------
# Safe stock reduction (shared: sales in Sprint 2 must use this)
# ---------------------------------------------------------------------------
def reduce_stock(product_id, quantity):
    """Remove `quantity` units of a product, never letting stock go below 0.

    Concurrency-safe: the check and the subtraction happen in ONE SQL statement
        UPDATE inventory SET quantity_on_hand = quantity_on_hand - :qty
        WHERE product_id = :id AND quantity_on_hand >= :qty
    so two sales running at the same moment cannot both pass a stale check.
    If no row was updated, there was not enough stock and nothing changes.

    Does NOT commit. The caller (e.g. create_sale) commits once after saving the
    sale, sale items and stock movement, or rolls back on any error, so the whole
    sale succeeds or fails together.
    """
    if not _is_int(quantity) or quantity <= 0:
        raise StockValidationError("Quantity must be greater than 0.")

    result = db.session.execute(
        update(Inventory)
        .where(
            Inventory.product_id == product_id,
            Inventory.quantity_on_hand >= quantity,
        )
        .values(
            quantity_on_hand=Inventory.quantity_on_hand - quantity,
            last_updated=db.func.now(),
        )
        .execution_options(synchronize_session=False)
    )

    if result.rowcount == 0:
        available = db.session.execute(
            select(Inventory.quantity_on_hand).where(Inventory.product_id == product_id)
        ).scalar()
        if available is None:
            raise StockValidationError("This product has no inventory record.")
        raise StockValidationError(
            f"Insufficient stock: requested {quantity}, only {available} available."
        )
    # Make objects already loaded in this session re-read the new value.
    db.session.expire_all()


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------
def _stock_qty():
    # A product with no inventory row is treated as 0 in stock.
    return db.func.coalesce(Inventory.quantity_on_hand, 0)


def _inventory_query():
    return (
        db.session.query(Product, Inventory)
        .outerjoin(Inventory, Inventory.product_id == Product.product_id)
        .filter(Product.is_active.is_(True))
    )


def _to_row(product, inventory):
    qty = inventory.quantity_on_hand if inventory else 0
    category = getattr(product, "category", None)  # works if M1 defined the relationship
    return {
        "product_id": product.product_id,
        "sku": product.sku,
        "name": product.name,
        "category": category.name if category else "—",
        "quantity_on_hand": qty,
        "reorder_level": product.reorder_level,
        "is_low": is_low_stock(qty, product.reorder_level),
        "last_updated": inventory.last_updated if inventory else None,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@inventory_bp.route("/inventory")
@login_required
def list_inventory():
    search = request.args.get("q", "").strip()
    query = _inventory_query()
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
    rows = query.order_by(Product.name).all()
    items = [_to_row(p, inv) for p, inv in rows]
    return render_template("inventory/list.html", items=items, search=search)


@inventory_bp.route("/inventory/low-stock")
@login_required
def low_stock_report():
    rows = (
        _inventory_query()
        .filter(_stock_qty() <= Product.reorder_level)
        .order_by(_stock_qty(), Product.name)
        .all()
    )
    items = [_to_row(p, inv) for p, inv in rows]
    return render_template("inventory/low_stock.html", items=items)
