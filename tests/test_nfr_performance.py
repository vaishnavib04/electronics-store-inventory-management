import time
import pytest


@pytest.fixture
def performance_data(monkeypatch):
    """Create an isolated app and sample inventory for performance testing."""
    monkeypatch.setenv("SECRET_KEY", "nfr-test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    from app import create_app
    from app.extensions import db
    from app.models import User, Category, Product, Inventory, Supplier
    from werkzeug.security import generate_password_hash

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    with app.app_context():
        db.create_all()

        user = User(
            username="nfr_tester",
            password_hash=generate_password_hash("test-password"),
            role="Store Staff",
            is_active=True,
        )
        category = Category(name="NFR Test Category")
        supplier = Supplier(name="NFR Test Supplier", is_active=True)
        db.session.add_all([user, category, supplier])
        db.session.flush()

        products = [
            Product(
                sku=f"NFR-{i:03}",
                name=f"NFR Test Product {i:03}",
                category_id=category.category_id,
                unit_price=100,
                reorder_level=5,
                is_active=True,
            )
            for i in range(100)
        ]
        db.session.add_all(products)
        db.session.flush()

        db.session.add_all([
            Inventory(
                product_id=product.product_id,
                quantity_on_hand=2 if i < 10 else 50,
            )
            for i, product in enumerate(products)
        ])
        db.session.commit()

        client = app.test_client()

        # Authenticate using Flask-Login's session.
        with client.session_transaction() as session:
            session["_user_id"] = str(user.user_id)
            session["_fresh"] = True

        yield client

        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize(
    "path",
    [
        "/inventory",
        "/inventory?q=NFR-050",
        "/inventory/low-stock",
        "/products?q=NFR-050",
    ],
)
def test_common_read_response_time_meets_srs_target(performance_data, path):
    """At least 90% of common read requests must complete within three seconds."""
    client = performance_data

    warmup = client.get(path)
    assert warmup.status_code == 200, (
        f"{path} returned HTTP {warmup.status_code}; expected 200."
    )

    timings = []

    for _ in range(10):
        start = time.perf_counter()
        response = client.get(path)
        elapsed = time.perf_counter() - start

        assert response.status_code == 200, (
            f"{path} returned HTTP {response.status_code}; expected 200."
        )
        timings.append(elapsed)

    average = sum(timings) / len(timings)
    passing = sum(elapsed < 3.0 for elapsed in timings)
    pass_rate = passing / len(timings)

    print(f"\nNFR performance: {path}")
    print(f"Runs: {len(timings)}")
    print(f"Average response time: {average:.4f} seconds")
    print(f"Requests under 3 seconds: {passing}/{len(timings)}")
    print(f"Pass rate: {pass_rate:.0%}")

    assert pass_rate >= 0.9, (
        f"{path} met the 3-second target for only {pass_rate:.0%} "
        f"of requests; expected at least 90%."
    )


def test_purchase_and_sale_response_time_under_3_seconds(performance_data):
    """Recording common purchase and sale operations must stay under three seconds."""
    client = performance_data
    with client.application.app_context():
        from app.models import Product, Supplier

        product = Product.query.filter_by(sku="NFR-000").one()
        supplier = Supplier.query.filter_by(name="NFR Test Supplier").one()
        product_id = product.product_id
        supplier_id = supplier.supplier_id

    timings = []
    for _ in range(10):
        start = time.perf_counter()
        response = client.post(
            "/purchases/new",
            data={
                "supplier_id": str(supplier_id),
                "product_id": [str(product_id)],
                "quantity": ["1"],
                "unit_cost": ["10.00"],
            },
        )
        elapsed = time.perf_counter() - start
        assert response.status_code == 302
        timings.append(elapsed)

    for _ in range(10):
        start = time.perf_counter()
        response = client.post(
            "/sales/new",
            data={"product_id": [str(product_id)], "quantity": ["1"]},
        )
        elapsed = time.perf_counter() - start
        assert response.status_code == 302
        timings.append(elapsed)

    passing = sum(elapsed < 3.0 for elapsed in timings)
    assert passing / len(timings) >= 0.9, (
        f"Only {passing}/{len(timings)} transaction requests completed "
        "within three seconds; expected at least 90%."
    )