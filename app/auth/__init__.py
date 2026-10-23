
from flask import Blueprint
from flask_login import current_user

from app.extensions import login_manager

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None
