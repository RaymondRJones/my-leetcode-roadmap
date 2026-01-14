"""
Access checking functions for user authentication and authorization.
"""
from typing import Optional
from flask import session, current_app


def get_current_user() -> Optional[dict]:
    """Get current user from Flask session."""
    return session.get('user')


def _get_metadata_value(user_data: dict, key: str, default=False):
    """
    Get a metadata value, checking private_metadata first, then public_metadata.

    Args:
        user_data: The user data dictionary
        key: The metadata key to look for
        default: Default value if not found

    Returns:
        The metadata value or default
    """
    if not user_data:
        return default

    # Check private_metadata first (more secure)
    private_metadata = user_data.get('private_metadata', {})
    if private_metadata and key in private_metadata:
        return private_metadata.get(key, default)

    # Fallback to public_metadata for backwards compatibility
    public_metadata = user_data.get('public_metadata', {})
    return public_metadata.get(key, default)


def has_premium_access(user_data: Optional[dict]) -> bool:
    """Check if user has premium access."""
    if not user_data:
        return False
    return bool(_get_metadata_value(user_data, 'has_premium', False))


def has_ai_access(user_data: Optional[dict]) -> bool:
    """Check if user has AI access."""
    if not user_data:
        return False
    return bool(_get_metadata_value(user_data, 'has_ai_access', False))


def has_system_design_access(user_data: Optional[dict]) -> bool:
    """Check if user has system design access."""
    if not user_data:
        return False
    return bool(_get_metadata_value(user_data, 'has_system_design_access', False))


def is_allowed_user(user_data: Optional[dict]) -> bool:
    """Check if user is in the special allowed list."""
    if not user_data:
        return False

    # Get allowed emails from config
    allowed_emails = current_app.config.get('ALLOWED_EMAILS', [])

    email_addresses = user_data.get('email_addresses', [])
    primary_email = ''
    if email_addresses:
        primary_email = email_addresses[0].get('email_address', '')

    public_metadata = user_data.get('public_metadata', {})

    return (
        primary_email in allowed_emails or
        public_metadata.get('specialAccess') is True
    )
