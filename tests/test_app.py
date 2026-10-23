from app import create_app


def test_app_with_temporary_database(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()

    assert app.config["SECRET_KEY"] == "test-secret-key"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
