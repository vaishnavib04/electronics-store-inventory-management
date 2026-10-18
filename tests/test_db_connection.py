import os

import pytest
from sqlalchemy import text

from app import create_app
from app.extensions import db


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="MySQL connection test requires DATABASE_URL",
)
def test_database_connection():
    app = create_app()

    with app.app_context():
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1