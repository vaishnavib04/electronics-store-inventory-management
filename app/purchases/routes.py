from flask import Blueprint

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")

@purchases_bp.route("/")
def index():
    return "ESIMS Purchases Module"
