from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/login")

@auth_bp.route("/")
def index():
    return "ESIMS Login Module"
