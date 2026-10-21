from flask import Flask

from app.extensions import db
from app.auth.routes import auth_bp
from app.products.routes import products_bp
from app.inventory.routes import inventory_bp
from app.suppliers.routes import suppliers_bp
from app.purchases.routes import purchases_bp
from app.sales.routes import sales_bp
from app.reports.routes import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///esims.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        return "ESIMS - Electronics Store Inventory Management System"

    return app
