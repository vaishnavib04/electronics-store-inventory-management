import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def auth_app(monkeypatch):
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


def test_authenticated_login_submission_validates_new_credentials(auth_app):
    from app.extensions import db
    from app.models import User

    user = User(
        username="auth_tester",
        password_hash=generate_password_hash("correct-password"),
        role="Store Staff",
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()

    client = auth_app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)
        session["_fresh"] = True

    response = client.post(
        "/login",
        data={"username": "invalid-user", "password": "correct-password"},
    )

    assert response.status_code == 401
    assert b"Invalid username or password." in response.data
    with client.session_transaction() as session:
        assert "_user_id" not in session


def test_auth_pages_are_not_cached(auth_app):
    response = auth_app.test_client().get("/login")

    assert (
        response.headers["Cache-Control"]
        == "no-store, no-cache, must-revalidate, max-age=0"
    )
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"
