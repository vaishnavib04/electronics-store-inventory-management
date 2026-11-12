from flask import Blueprint

from app.extensions import login_manager

auth_bp = Blueprint("auth", __name__)


@auth_bp.after_request
def prevent_auth_page_caching(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None
