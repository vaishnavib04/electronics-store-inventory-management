from flask import Blueprint

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")

@suppliers_bp.route("/")
def index():
    return "ESIMS Suppliers Module"
