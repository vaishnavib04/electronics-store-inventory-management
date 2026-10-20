
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import create_app
from app.extensions import db


def test_mysql_rejects_negative_product_price():
    app = create_app()

    with app.app_context():
        try:
            with db.engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO categories (name)
                        VALUES ('__constraint_test_category__')
                    """)
                )

                category_id = connection.execute(
                    text("""
                        SELECT category_id
                        FROM categories
                        WHERE name = '__constraint_test_category__'
                    """)
                ).scalar_one()

                connection.execute(
                    text("""
                        INSERT INTO products
                            (sku, name, category_id, unit_price,
                             reorder_level, is_active)
                        VALUES
                            ('__constraint_test__', 'Constraint Test',
                             :category_id, -1, 0, 1)
                    """),
                    {"category_id": category_id},
                )

        except OperationalError as exc:
            assert "ck_product_unit_price" in str(exc)
            print("MySQL correctly rejected the negative product price.")
            return

        raise AssertionError("MySQL accepted a negative product price.")
