
import os

from flask import Flask
from dotenv import load_dotenv

from app.extensions import db, login_manager, csrf

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "SECRET_KEY is missing. Configure it in your .env file."
        )

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure it in your .env file."
        )

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from app import models  # noqa: F401
    from app.auth import auth_bp
    from app.auth import routes  # noqa: F401
    from app.products import products_bp
    from app.products import routes as product_routes  # noqa: F401
    from app.suppliers import suppliers_bp
    from app.inventory.routes import inventory_bp
    from app.purchases import purchases_bp
    from app.purchases import routes as purchase_routes  # noqa: F401

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(purchases_bp, url_prefix="/purchases")

    return app

