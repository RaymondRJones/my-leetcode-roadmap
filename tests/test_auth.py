"""
Tests for auth module.
"""
import pytest
from flask import session
from app.auth.access import (
    get_current_user,
    has_premium_access,
    has_ai_access,
    has_system_design_access,
    has_guides_access,
    is_allowed_user
)


class TestHasPremiumAccess:
    """Tests for has_premium_access function."""

    def test_returns_false_for_none(self):
        """Test that None user returns False."""
        assert has_premium_access(None) is False

    def test_returns_false_for_empty_dict(self):
        """Test that empty user dict returns False."""
        assert has_premium_access({}) is False

    def test_returns_true_from_private_metadata(self):
        """Test that premium access from private_metadata works."""
        user = {
            'private_metadata': {'has_premium': True}
        }
        assert has_premium_access(user) is True

    def test_returns_false_from_private_metadata(self):
        """Test that non-premium from private_metadata works."""
        user = {
            'private_metadata': {'has_premium': False}
        }
        assert has_premium_access(user) is False

    def test_falls_back_to_public_metadata(self):
        """Test fallback to public_metadata when private_metadata missing."""
        user = {
            'public_metadata': {'has_premium': True}
        }
        assert has_premium_access(user) is True

    def test_private_metadata_takes_precedence(self):
        """Test that private_metadata takes precedence over public_metadata."""
        user = {
            'private_metadata': {'has_premium': False},
            'public_metadata': {'has_premium': True}
        }
        assert has_premium_access(user) is False


class TestHasAiAccess:
    """Tests for has_ai_access function."""

    def test_returns_false_for_none(self):
        """Test that None user returns False."""
        assert has_ai_access(None) is False

    def test_returns_true_from_private_metadata(self):
        """Test that AI access from private_metadata works."""
        user = {
            'private_metadata': {'has_ai_access': True}
        }
        assert has_ai_access(user) is True

    def test_returns_false_by_default(self):
        """Test that AI access returns False by default."""
        user = {'private_metadata': {}}
        assert has_ai_access(user) is False


class TestHasSystemDesignAccess:
    """Tests for has_system_design_access function."""

    def test_returns_false_for_none(self):
        """Test that None user returns False."""
        assert has_system_design_access(None) is False

    def test_returns_true_from_private_metadata(self):
        """Test that system design access from private_metadata works."""
        user = {
            'private_metadata': {'has_system_design_access': True}
        }
        assert has_system_design_access(user) is True

    def test_returns_false_by_default(self):
        """Test that system design access returns False by default."""
        user = {'private_metadata': {}}
        assert has_system_design_access(user) is False


class TestIsAllowedUser:
    """Tests for is_allowed_user function."""

    def test_returns_false_for_none(self, app_context):
        """Test that None user returns False."""
        assert is_allowed_user(None) is False

    def test_returns_true_for_allowed_email(self, app, app_context):
        """Test that allowed email returns True."""
        user = {
            'email_addresses': [
                {'email_address': 'admin@example.com'}
            ],
            'public_metadata': {}
        }
        assert is_allowed_user(user) is True

    def test_returns_false_for_non_allowed_email(self, app, app_context):
        """Test that non-allowed email returns False."""
        user = {
            'email_addresses': [
                {'email_address': 'random@example.com'}
            ],
            'public_metadata': {}
        }
        assert is_allowed_user(user) is False

    def test_returns_true_for_special_access(self, app, app_context):
        """Test that specialAccess flag grants access."""
        user = {
            'email_addresses': [
                {'email_address': 'random@example.com'}
            ],
            'public_metadata': {'specialAccess': True}
        }
        assert is_allowed_user(user) is True


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    def test_returns_none_when_no_session(self, app):
        """Test that returns None when no user in session."""
        with app.test_request_context():
            assert get_current_user() is None

    def test_returns_user_from_session(self, app):
        """Test that returns user from session."""
        with app.test_request_context():
            session['user'] = {'id': 'user_123'}
            assert get_current_user() == {'id': 'user_123'}


class TestHasGuidesAccess:
    """Tests for has_guides_access function."""

    def test_returns_false_for_none(self):
        """Test that None user returns False."""
        assert has_guides_access(None) is False

    def test_returns_false_for_empty_dict(self):
        """Test that empty user dict returns False."""
        assert has_guides_access({}) is False

    def test_returns_true_from_private_metadata(self):
        """Test that guides access from private_metadata works."""
        user = {
            'private_metadata': {'has_guides_access': True}
        }
        assert has_guides_access(user) is True

    def test_returns_false_from_private_metadata(self):
        """Test that non-guides access from private_metadata works."""
        user = {
            'private_metadata': {'has_guides_access': False}
        }
        assert has_guides_access(user) is False

    def test_falls_back_to_public_metadata(self):
        """Test fallback to public_metadata when private_metadata missing."""
        user = {
            'public_metadata': {'has_guides_access': True}
        }
        assert has_guides_access(user) is True

    def test_private_metadata_takes_precedence(self):
        """Test that private_metadata takes precedence over public_metadata."""
        user = {
            'private_metadata': {'has_guides_access': False},
            'public_metadata': {'has_guides_access': True}
        }
        assert has_guides_access(user) is False

    def test_returns_false_by_default(self):
        """Test that guides access returns False by default."""
        user = {'private_metadata': {}}
        assert has_guides_access(user) is False


class TestAdminHasAllAccess:
    """Tests that admin users have all access types."""

    def test_admin_has_premium_access(self):
        """Test that admin users have premium access."""
        user = {'private_metadata': {'is_admin': True}}
        assert has_premium_access(user) is True

    def test_admin_has_ai_access(self):
        """Test that admin users have AI access."""
        user = {'private_metadata': {'is_admin': True}}
        assert has_ai_access(user) is True

    def test_admin_has_system_design_access(self):
        """Test that admin users have system design access."""
        user = {'private_metadata': {'is_admin': True}}
        assert has_system_design_access(user) is True

    def test_admin_has_guides_access(self):
        """Test that admin users have guides access."""
        user = {'private_metadata': {'is_admin': True}}
        assert has_guides_access(user) is True

    def test_admin_from_public_metadata_has_all_access(self):
        """Test that admin flag in public_metadata also grants all access."""
        user = {'public_metadata': {'is_admin': True}}
        assert has_premium_access(user) is True
        assert has_ai_access(user) is True
        assert has_system_design_access(user) is True
        assert has_guides_access(user) is True

    def test_non_admin_without_flags_has_no_access(self):
        """Test that non-admin users without flags have no access."""
        user = {'private_metadata': {'is_admin': False}}
        assert has_premium_access(user) is False
        assert has_ai_access(user) is False
        assert has_system_design_access(user) is False
        assert has_guides_access(user) is False
