from sqlalchemy import text

from app import create_app
from app.extensions import db


def test_database_connection():
    app = create_app()

    with app.app_context():
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1
