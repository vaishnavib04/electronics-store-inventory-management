
from sqlalchemy import text

from app import create_app
from app.extensions import db


def test_app_with_temporary_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()

    with app.app_context():
        try:
            result = db.session.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            db.session.remove()
