from flask import Blueprint

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@inventory_bp.route("/")
def index():
    return "ESIMS Inventory Module"
