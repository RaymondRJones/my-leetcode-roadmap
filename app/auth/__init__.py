"""
Authentication package for the LeetCode Roadmap Generator.
"""
from .access import (
    get_current_user,
    has_premium_access,
    has_ai_access,
    has_system_design_access,
    is_allowed_user
)
from .decorators import (
    login_required,
    premium_required,
    ai_access_required,
    system_design_access_required
)

__all__ = [
    'get_current_user',
    'has_premium_access',
    'has_ai_access',
    'has_system_design_access',
    'is_allowed_user',
    'login_required',
    'premium_required',
    'ai_access_required',
    'system_design_access_required'
]
