
import os

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app import create_app
from app.extensions import db


def _create_test_category(connection):
    connection.execute(
        text("INSERT INTO categories (name) VALUES ('__constraint_test_category__')")
    )
    return connection.execute(
        text(
            "SELECT category_id FROM categories "
            "WHERE name = '__constraint_test_category__'"
        )
    ).scalar_one()


def _insert_test_product(connection, category_id, *, sku, unit_price=1, reorder_level=0):
    connection.execute(
        text(
            """
            INSERT INTO products
                (sku, name, category_id, unit_price, reorder_level, is_active)
            VALUES (:sku, 'Constraint Test', :category_id, :unit_price,
                    :reorder_level, 1)
            """
        ),
        {
            "sku": sku,
            "category_id": category_id,
            "unit_price": unit_price,
            "reorder_level": reorder_level,
        },
    )


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL", "").startswith("mysql"),
    reason="MySQL constraint test requires a MySQL DATABASE_URL",
)
def test_mysql_rejects_negative_product_price():
    app = create_app()

    with app.app_context():
        try:
            with db.engine.begin() as connection:
                category_id = _create_test_category(connection)
                _insert_test_product(
                    connection,
                    category_id,
                    sku="__constraint_test_price__",
                    unit_price=-1,
                )

        except DBAPIError as exc:
            assert "ck_product_unit_price" in str(exc.orig)
            return

        raise AssertionError("MySQL accepted a negative product price.")


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL", "").startswith("mysql"),
    reason="MySQL constraint test requires a MySQL DATABASE_URL",
)
def test_mysql_rejects_negative_product_reorder_level():
    app = create_app()

    with app.app_context():
        try:
            with db.engine.begin() as connection:
                category_id = _create_test_category(connection)
                _insert_test_product(
                    connection,
                    category_id,
                    sku="__constraint_test_reorder__",
                    reorder_level=-1,
                )

        except DBAPIError as exc:
            assert "ck_product_reorder_level" in str(exc.orig)
            return

        raise AssertionError("MySQL accepted a negative product reorder level.")


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL", "").startswith("mysql"),
    reason="MySQL constraint test requires a MySQL DATABASE_URL",
)
def test_mysql_rejects_duplicate_product_sku():
    app = create_app()
    duplicate_sku = "__constraint_test_duplicate_sku__"

    with app.app_context():
        try:
            with db.engine.begin() as connection:
                category_id = _create_test_category(connection)
                _insert_test_product(connection, category_id, sku=duplicate_sku)
                _insert_test_product(connection, category_id, sku=duplicate_sku)

        except DBAPIError as exc:
            assert exc.orig.args[0] == 1062
            assert duplicate_sku in str(exc.orig)
            return

        raise AssertionError("MySQL accepted a duplicate product SKU.")
