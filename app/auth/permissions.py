from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*allowed_roles):
    """Require an authenticated user with one of the supplied roles."""
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator
