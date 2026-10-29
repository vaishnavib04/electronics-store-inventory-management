import time
import pytest


@pytest.fixture
def performance_data(monkeypatch):
    """Create an isolated app and sample inventory for performance testing."""
    monkeypatch.setenv("SECRET_KEY", "nfr-test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    from app import create_app
    from app.extensions import db
    from app.models import User, Category, Product, Inventory
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
        db.session.add_all([user, category])
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
    ],
)
def test_inventory_response_time_under_3_seconds(performance_data, path):
    """Measure authenticated inventory response time against the 3-second target."""
    client = performance_data

    warmup = client.get(path)
    assert warmup.status_code == 200, (
        f"{path} returned HTTP {warmup.status_code}; expected 200."
    )

    timings = []

    for _ in range(5):
        start = time.perf_counter()
        response = client.get(path)
        elapsed = time.perf_counter() - start

        assert response.status_code == 200, (
            f"{path} returned HTTP {response.status_code}; expected 200."
        )
        timings.append(elapsed)

    average = sum(timings) / len(timings)
    maximum = max(timings)

    print(f"\nNFR performance: {path}")
    print(f"Runs: {len(timings)}")
    print(f"Average response time: {average:.4f} seconds")
    print(f"Maximum response time: {maximum:.4f} seconds")

    assert maximum < 3.0, (
        f"{path} exceeded the 3-second target: maximum {maximum:.4f} seconds"
    )