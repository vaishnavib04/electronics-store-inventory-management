"""Tests for Member 2's product management and Sprint 2 UI/module integration (UI-001)."""

from decimal import Decimal
import re

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
    assert b"Quantity on hand</dt><dd class=\"col-sm-9\">10</dd>" in detail_after_purchase.data
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
    assert b"Quantity on hand</dt><dd class=\"col-sm-9\">3</dd>" in detail_after_sale.data
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


# ---------------------------------------------------------------------------
# Sprint 2 [UI-001]: Comprehensive End-to-End UI & Cross-Module Integration
# ---------------------------------------------------------------------------
def test_navigation_links_resolve_and_render_module_content(logged_in_client):
    """Step 5A: Parse actual navbar hrefs from base.html, follow every link, and
    verify each module page renders its expected content and cross-page links."""
    client, _ = logged_in_client

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    html = dashboard.data.decode("utf-8")

    nav_match = re.search(
        r'<nav[^>]*aria-label="Main navigation"[^>]*>(.*?)</nav>',
        html,
        re.DOTALL,
    )
    assert nav_match is not None, "Shared navigation bar not found in base.html"
    nav_links = dict(
        re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', nav_match.group(1))
    )

    expected_destinations = {
        "/dashboard": (b"Welcome to ESIMS", b"Logout"),
        "/products": (b"Products", b"Add product"),
        "/inventory": (b"Inventory", b"View low-stock items"),
        "/inventory/low-stock": (b"Low-stock items", b"Back to inventory"),
        "/suppliers/": (b"Supplier Management", b"Add Supplier"),
        "/purchases/": (b"Purchase Transactions", b"Record New Purchase"),
        "/sales": (b"Sales", b"Record a new sale"),
        "/reports/inventory": (b"Inventory report", b"Stock by product"),
        "/reports/sales": (b"Sales report", b"Inventory report"),
    }

    for expected_path, (heading_bytes, action_bytes) in expected_destinations.items():
        assert expected_path in nav_links, f"Missing nav link for {expected_path}"
        page = client.get(expected_path)
        assert page.status_code == 200
        assert b"https://cdn.jsdelivr.net/npm/bootstrap" in page.data
        assert b'aria-label="Main navigation"' in page.data
        assert heading_bytes in page.data
        assert action_bytes in page.data


def test_purchase_workflow_ui_empty_state_validation_and_success(logged_in_client, app):
    """Step 5B: Verify purchase list empty state, Bootstrap form controls,
    validation errors, and successful purchase feedback and table display."""
    from app.extensions import db
    from app.models import Supplier

    client, category_id = logged_in_client
    with app.app_context():
        supplier = Supplier(name="Volt Electronics", is_active=True)
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.supplier_id

    client.post(
        "/products/new",
        data=_form(category_id, name="Mechanical Keyboard", sku="KEY-101", unit_price="75.00"),
    )

    # 1. Empty state on purchase list
    empty_list = client.get("/purchases/")
    assert empty_list.status_code == 200
    assert b"No purchase transactions have been recorded yet." in empty_list.data
    assert b"alert alert-info" in empty_list.data

    # 2. Purchase form renders with Bootstrap controls and active options
    form_page = client.get("/purchases/new")
    assert form_page.status_code == 200
    assert b"form-select" in form_page.data
    assert b"form-control" in form_page.data
    assert b"Volt Electronics" in form_page.data
    assert b"Mechanical Keyboard (KEY-101)" in form_page.data

    # 3. Validation error displays Bootstrap alert
    invalid_resp = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(supplier_id),
            "product_id": ["1"],
            "quantity": ["0"],
            "unit_cost": ["45.00"],
        },
    )
    assert invalid_resp.status_code == 400
    assert b"alert alert-danger" in invalid_resp.data
    assert b"Quantity must be greater than 0." in invalid_resp.data

    # 4. Valid purchase shows success feedback and populates purchase list table
    valid_resp = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(supplier_id),
            "product_id": ["1"],
            "quantity": ["5"],
            "unit_cost": ["45.00"],
        },
        follow_redirects=True,
    )
    assert valid_resp.status_code == 200
    assert b"alert alert-success" in valid_resp.data
    assert b"Purchase recorded successfully." in valid_resp.data
    assert b"Volt Electronics" in valid_resp.data
    assert b"225.00" in valid_resp.data
    assert b"Mechanical Keyboard" in valid_resp.data
    assert b"Quantity: 5" in valid_resp.data


def test_supplier_workflow_ui_empty_state_validation_and_success(logged_in_client):
    """Step 5C: Verify supplier list empty state, Bootstrap form styling,
    validation errors, creation, and editing workflows."""
    client, _ = logged_in_client

    # 1. Empty state on supplier list
    empty_list = client.get("/suppliers/")
    assert empty_list.status_code == 200
    assert b"No suppliers found." in empty_list.data
    assert b"alert alert-info" in empty_list.data

    # 2. Supplier form renders with Bootstrap classes
    add_page = client.get("/suppliers/add")
    assert add_page.status_code == 200
    assert b"form-control" in add_page.data
    assert b"form-label" in add_page.data
    assert b"btn btn-primary" in add_page.data

    # 3. Validation failure renders Bootstrap alert
    invalid_resp = client.post(
        "/suppliers/add",
        data={
            "name": "   ",
            "phone": "bad-phone",
            "email": "not-an-email",
        },
    )
    assert invalid_resp.status_code == 400
    assert b"alert alert-danger" in invalid_resp.data
    assert b"Supplier name is required." in invalid_resp.data
    assert b"Enter a valid phone number." in invalid_resp.data
    assert b"Enter a valid email address." in invalid_resp.data

    # 4. Create supplier and verify feedback and table row
    create_resp = client.post(
        "/suppliers/add",
        data={
            "name": "Silicon Distributors",
            "contact_person": "Aarav Mehta",
            "phone": "+91 9876543210",
            "email": "aarav@silicon.example.com",
            "address": "Indiranagar, Bengaluru",
        },
        follow_redirects=True,
    )
    assert create_resp.status_code == 200
    assert b"alert alert-success" in create_resp.data
    assert b"Supplier added successfully." in create_resp.data
    assert b"Silicon Distributors" in create_resp.data
    assert b"Aarav Mehta" in create_resp.data

    # 5. Edit supplier and verify updated values
    edit_page = client.get("/suppliers/1/edit")
    assert edit_page.status_code == 200
    assert b"Silicon Distributors" in edit_page.data

    edit_resp = client.post(
        "/suppliers/1/edit",
        data={
            "name": "Silicon Distributors Pvt Ltd",
            "contact_person": "Aarav Mehta",
            "phone": "+91 9876543210",
            "email": "contact@silicon.example.com",
            "address": "Koramangala, Bengaluru",
        },
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"alert alert-success" in edit_resp.data
    assert b"Supplier updated successfully." in edit_resp.data
    assert b"Silicon Distributors Pvt Ltd" in edit_resp.data
    assert b"Koramangala, Bengaluru" in edit_resp.data


def test_sales_workflow_ui_empty_state_validation_and_success(logged_in_client, app):
    """Step 5D: Verify sales list/form empty states, Bootstrap styling,
    insufficient stock validation feedback, and successful sale workflow."""
    from app.extensions import db
    from app.models import Inventory

    client, category_id = logged_in_client

    # 1. Empty sales list and empty products state on sale form
    empty_sales = client.get("/sales")
    assert empty_sales.status_code == 200
    assert b"No sales have been recorded yet." in empty_sales.data
    assert b"alert alert-info" in empty_sales.data

    empty_form = client.get("/sales/new")
    assert empty_form.status_code == 200
    assert b"There are no active products to sell yet." in empty_form.data

    # 2. Add product with stock and verify sale form
    client.post(
        "/products/new",
        data=_form(category_id, name="Noise-Cancelling Headphones", sku="ANC-200", unit_price="150.00"),
    )
    with app.app_context():
        db.session.add(Inventory(product_id=1, quantity_on_hand=4))
        db.session.commit()

    sale_form = client.get("/sales/new")
    assert sale_form.status_code == 200
    assert b"form-select" in sale_form.data
    assert b"form-control" in sale_form.data
    assert b"Noise-Cancelling Headphones (ANC-200): 150.00, 4 in stock" in sale_form.data

    # 3. Validation error on insufficient stock
    bad_sale = client.post(
        "/sales/new",
        data={"product_id": ["1"], "quantity": ["6"]},
    )
    assert bad_sale.status_code == 400
    assert b"alert alert-danger" in bad_sale.data
    assert b"Insufficient stock: requested 6, only 4 available." in bad_sale.data

    # 4. Valid sale redirects to sale detail page with Bootstrap alert and table
    good_sale = client.post(
        "/sales/new",
        data={"product_id": ["1"], "quantity": ["2"]},
        follow_redirects=True,
    )
    assert good_sale.status_code == 200
    assert b"alert alert-success" in good_sale.data
    assert b"recorded successfully" in good_sale.data
    assert b"Noise-Cancelling Headphones" in good_sale.data
    assert b"300.00" in good_sale.data


def test_reports_workflow_empty_states_navigation_and_feedback(logged_in_client, app):
    """Step 5E: Verify inventory and sales report empty states, cross-report
    navigation, live data rendering, and invalid date filter feedback."""
    from app.extensions import db
    from app.models import Inventory

    client, category_id = logged_in_client

    # 1. Empty states when no active products or sales exist
    inv_report_empty = client.get("/reports/inventory")
    assert inv_report_empty.status_code == 200
    assert b"No active products found." in inv_report_empty.data
    assert b"alert alert-info" in inv_report_empty.data
    assert b'/reports/sales' in inv_report_empty.data

    sales_report_empty = client.get("/reports/sales")
    assert sales_report_empty.status_code == 200
    assert b"No sales found for this period." in sales_report_empty.data
    assert b"alert alert-info" in sales_report_empty.data
    assert b'/reports/inventory' in sales_report_empty.data

    # 2. Populate product, inventory, and sale, then verify report figures
    client.post(
        "/products/new",
        data=_form(category_id, name="SSD 1TB", sku="SSD-1TB", unit_price="80.00", reorder_level="3"),
    )
    with app.app_context():
        db.session.add(Inventory(product_id=1, quantity_on_hand=5))
        db.session.commit()

    client.post("/sales/new", data={"product_id": ["1"], "quantity": ["2"]})

    inv_report = client.get("/reports/inventory")
    assert inv_report.status_code == 200
    assert b"SSD 1TB" in inv_report.data
    assert b"240.00" in inv_report.data  # 3 remaining x 80.00
    assert b"Low stock" in inv_report.data

    sales_report = client.get("/reports/sales")
    assert sales_report.status_code == 200
    assert b"SSD 1TB" in sales_report.data
    assert b"160.00" in sales_report.data  # 2 sold x 80.00

    # 3. Invalid date range shows error alert and preserves entered dates
    bad_dates = client.get("/reports/sales?start=2026-10-25&end=2026-10-10")
    assert bad_dates.status_code == 400
    assert b"alert alert-danger" in bad_dates.data
    assert b"Start date cannot be after the end date." in bad_dates.data
    assert b"Please correct the dates above to see the report." in bad_dates.data
    assert b'value="2026-10-25"' in bad_dates.data
    assert b'value="2026-10-10"' in bad_dates.data


def test_form_value_preservation_across_modules_on_validation_error(logged_in_client, app):
    """Step 5F: Submit invalid forms across Products, Suppliers, Purchases, and Sales,
    and verify both the validation error alert and preserved user inputs."""
    from app.extensions import db
    from app.models import Inventory, Supplier

    client, category_id = logged_in_client
    with app.app_context():
        supplier = Supplier(name="Preservation Supplier", is_active=True)
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.supplier_id

    # 1. Product form preserves valid fields when unit_price is invalid
    bad_product = client.post(
        "/products/new",
        data={
            "name": "4K Gaming Monitor",
            "sku": "MON-4K-01",
            "category_id": str(category_id),
            "unit_price": "-10.00",
            "reorder_level": "8",
        },
    )
    assert bad_product.status_code == 400
    assert b"Unit price must be a valid non-negative amount." in bad_product.data
    assert b'value="4K Gaming Monitor"' in bad_product.data
    assert b'value="MON-4K-01"' in bad_product.data
    assert b'value="8"' in bad_product.data
    assert f'value="{category_id}" selected'.encode() in bad_product.data

    # Create a valid product with stock for purchase and sale form tests
    client.post(
        "/products/new",
        data=_form(category_id, name="4K Gaming Monitor", sku="MON-4K-01", unit_price="300.00"),
    )
    with app.app_context():
        db.session.add(Inventory(product_id=1, quantity_on_hand=3))
        db.session.commit()

    # 2. Supplier form preserves valid fields when phone is invalid
    bad_supplier = client.post(
        "/suppliers/add",
        data={
            "name": "Apex Components",
            "contact_person": "Riya Sharma",
            "phone": "invalid-phone",
            "email": "riya@apex.example.com",
            "address": "MG Road, Bengaluru",
        },
    )
    assert bad_supplier.status_code == 400
    assert b"Enter a valid phone number." in bad_supplier.data
    assert b'value="Apex Components"' in bad_supplier.data
    assert b'value="Riya Sharma"' in bad_supplier.data
    assert b'value="invalid-phone"' in bad_supplier.data
    assert b'value="riya@apex.example.com"' in bad_supplier.data
    assert b"MG Road, Bengaluru</textarea>" in bad_supplier.data

    # 3. Purchase form preserves selected supplier, product, quantity, and unit_cost on error
    bad_purchase = client.post(
        "/purchases/new",
        data={
            "supplier_id": str(supplier_id),
            "product_id": ["1"],
            "quantity": ["6"],
            "unit_cost": "-15.00",
        },
    )
    assert bad_purchase.status_code == 400
    assert b"Unit cost must be a valid non-negative amount." in bad_purchase.data
    assert re.search(
        rf'<option value="{supplier_id}"\s+selected>',
        bad_purchase.data.decode("utf-8"),
    )
    assert re.search(
        r'<option value="1"\s+selected>',
        bad_purchase.data.decode("utf-8"),
    )
    assert b'name="quantity" class="form-control" min="1" step="1" required value="6"' in bad_purchase.data
    assert b'name="unit_cost" class="form-control" min="0" step="0.01" required value="-15.00"' in bad_purchase.data

    # 4. Sales form preserves selected product and quantity when stock is insufficient
    bad_sale = client.post(
        "/sales/new",
        data={
            "product_id": ["1"],
            "quantity": ["99"],
        },
    )
    assert bad_sale.status_code == 400
    assert b"Insufficient stock" in bad_sale.data
    assert re.search(
        r'<option value="1"\s+selected>',
        bad_sale.data.decode("utf-8"),
    )
    assert b'value="99"' in bad_sale.data
