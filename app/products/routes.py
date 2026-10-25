"""Product catalogue routes owned by Member 2."""

from decimal import Decimal, InvalidOperation

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category, Product
from app.products import products_bp


def _get_active_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or not product.is_active:
        abort(404)
    return product


def _read_product_form(existing_product=None):
    """Validate submitted fields and return (values, error)."""
    name = request.form.get("name", "").strip()
    sku = request.form.get("sku", "").strip()
    raw_category_id = request.form.get("category_id", "").strip()
    raw_unit_price = request.form.get("unit_price", "").strip()
    raw_reorder_level = request.form.get("reorder_level", "").strip()

    if not name:
        return None, "Product name is required."
    if len(name) > 150:
        return None, "Product name must be 150 characters or fewer."
    if not sku:
        return None, "SKU is required."
    if len(sku) > 80:
        return None, "SKU must be 80 characters or fewer."

    try:
        category_id = int(raw_category_id)
    except (TypeError, ValueError):
        return None, "Please select a valid category."
    category = db.session.get(Category, category_id)
    if category is None:
        return None, "Please select a valid category."

    try:
        unit_price = Decimal(raw_unit_price)
    except (InvalidOperation, TypeError, ValueError):
        return None, "Unit price must be a valid non-negative amount."
    if not unit_price.is_finite() or unit_price < 0:
        return None, "Unit price must be a valid non-negative amount."
    if unit_price.as_tuple().exponent < -2:
        return None, "Unit price can have at most two decimal places."
    if unit_price > Decimal("99999999.99"):
        return None, "Unit price is too large."

    try:
        reorder_level = int(raw_reorder_level)
    except (TypeError, ValueError):
        return None, "Reorder level must be a whole number of 0 or more."
    if reorder_level < 0:
        return None, "Reorder level must be a whole number of 0 or more."

    duplicate_sku = Product.query.filter(
        func.lower(Product.sku) == sku.lower(),
        Product.product_id != (existing_product.product_id if existing_product else -1),
    ).first()
    if duplicate_sku:
        return None, "That SKU is already in use. Enter a unique SKU."

    return {
        "name": name,
        "sku": sku,
        "category_id": category_id,
        "unit_price": unit_price,
        "reorder_level": reorder_level,
    }, None


def _render_product_form(*, title, endpoint, product=None, status=200):
    return (
        render_template(
            "products/form.html",
            title=title,
            endpoint=endpoint,
            product=product,
            categories=Category.query.order_by(Category.name).all(),
        ),
        status,
    )


def _save_product(product, values, success_message):
    for field, value in values.items():
        setattr(product, field, value)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("That SKU is already in use. Enter a unique SKU.", "error")
        return False
    flash(success_message, "success")
    return True


@products_bp.route("/products")
@login_required
def list_products():
    search = request.args.get("q", "").strip()
    query = Product.query.filter_by(is_active=True)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
        )
    products = query.order_by(Product.name, Product.sku).all()
    return render_template("products/list.html", products=products, search=search)


@products_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        values, error = _read_product_form()
        if error:
            flash(error, "error")
            return _render_product_form(
                title="Add product", endpoint="products.create_product", status=400
            )
        product = Product(is_active=True)
        if _save_product(product, values, "Product added successfully."):
            return redirect(url_for("products.view_product", product_id=product.product_id))
        return _render_product_form(
            title="Add product", endpoint="products.create_product", status=400
        )

    return _render_product_form(title="Add product", endpoint="products.create_product")


@products_bp.route("/products/<int:product_id>")
@login_required
def view_product(product_id):
    product = _get_active_product(product_id)
    return render_template("products/detail.html", product=product)


@products_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = _get_active_product(product_id)
    if request.method == "POST":
        values, error = _read_product_form(existing_product=product)
        if error:
            flash(error, "error")
            return _render_product_form(
                title="Edit product",
                endpoint="products.edit_product",
                product=product,
                status=400,
            )
        if _save_product(product, values, "Product updated successfully."):
            return redirect(url_for("products.view_product", product_id=product.product_id))
        return _render_product_form(
            title="Edit product",
            endpoint="products.edit_product",
            product=product,
            status=400,
        )

    return _render_product_form(
        title="Edit product", endpoint="products.edit_product", product=product
    )


@products_bp.route("/products/<int:product_id>/deactivate", methods=["POST"])
@login_required
def deactivate_product(product_id):
    product = _get_active_product(product_id)
    product.is_active = False
    db.session.commit()
    flash("Product deactivated successfully.", "success")
    return redirect(url_for("products.list_products"))
