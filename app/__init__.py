import os

from flask import Flask
from dotenv import load_dotenv

from app.extensions import db

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL is missing. Configure it in your .env file.")

    db.init_app(app)

    from app import models  # noqa: F401
    from app.auth import auth_bp
    from app.auth import routes  # noqa: F401

    app.register_blueprint(auth_bp)

    return app