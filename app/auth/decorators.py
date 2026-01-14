"""
Authentication decorators for protecting routes.
"""
from functools import wraps
from flask import redirect

from .access import (
    get_current_user,
    has_premium_access,
    has_ai_access,
    has_system_design_access,
    is_allowed_user,
    is_admin
)


def login_required(f):
    """Require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Require user to have premium access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_premium_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function


def ai_access_required(f):
    """Require user to have AI access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_ai_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function


def system_design_access_required(f):
    """Require user to have system design access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_system_design_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require user to be an admin.

    Used for admin-only routes like challenge admin dashboard.
    Redirects non-admins to the home page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not is_admin(user):
            return redirect('/')

        return f(*args, **kwargs)
    return decorated_function
