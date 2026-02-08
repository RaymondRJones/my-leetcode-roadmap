"""
Tests for routes with authenticated users.
"""
import pytest


class TestAuthenticatedPremiumRoutes:
    """Tests for premium routes with authenticated premium user."""

    def test_advanced_accessible_with_premium(self, authenticated_client):
        """Test that advanced page is accessible with premium access."""
        response = authenticated_client.get('/advanced')
        assert response.status_code == 200

    def test_complete_list_accessible_with_premium(self, authenticated_client):
        """Test that complete-list is accessible with premium access."""
        response = authenticated_client.get('/complete-list')
        assert response.status_code == 200


    def test_intermediate_month_2_accessible_with_premium(self, authenticated_client):
        """Test that intermediate Month 2 is accessible with premium."""
        response = authenticated_client.get('/intermediate/month/Month 2')
        assert response.status_code == 200

    def test_intermediate_month_3_accessible_with_premium(self, authenticated_client):
        """Test that intermediate Month 3 is accessible with premium."""
        response = authenticated_client.get('/intermediate/month/Month 3')
        assert response.status_code == 200

    def test_advanced_month_accessible_with_premium(self, authenticated_client):
        """Test that advanced month pages are accessible with premium."""
        response = authenticated_client.get('/advanced/month/Month 1')
        assert response.status_code == 200


class TestNonPremiumUserRoutes:
    """Tests for routes with non-premium authenticated user."""

    def test_public_routes_accessible(self, non_premium_client):
        """Test that public routes are accessible for non-premium users."""
        routes = ['/', '/beginner', '/intermediate', '/roadmap',
                  '/python-assessment', '/java-assessment']
        for route in routes:
            response = non_premium_client.get(route)
            assert response.status_code == 200, f"Route {route} should be accessible"

    def test_advanced_redirects_non_premium(self, non_premium_client):
        """Test that advanced page redirects non-premium users."""
        response = non_premium_client.get('/advanced')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_complete_list_redirects_non_premium(self, non_premium_client):
        """Test that complete-list redirects non-premium users."""
        response = non_premium_client.get('/complete-list')
        assert response.status_code == 302

    def test_guides_redirects_non_premium(self, non_premium_client):
        """Test that guides redirects non-premium users."""
        response = non_premium_client.get('/guides')
        assert response.status_code == 302

    def test_intermediate_month_1_accessible(self, non_premium_client):
        """Test that Month 1 is accessible for non-premium users."""
        response = non_premium_client.get('/intermediate/month/Month 1')
        assert response.status_code == 200

    def test_intermediate_month_2_redirects_non_premium(self, non_premium_client):
        """Test that Month 2 redirects non-premium users."""
        response = non_premium_client.get('/intermediate/month/Month 2')
        assert response.status_code == 302


class TestAllowedUserRoutes:
    """Tests for routes with allowed (admin) user without premium metadata."""

    def test_advanced_accessible_for_allowed_user(self, allowed_user_client):
        """Test that allowed users can access premium content."""
        response = allowed_user_client.get('/advanced')
        assert response.status_code == 200

    def test_complete_list_accessible_for_allowed_user(self, allowed_user_client):
        """Test that allowed users can access complete-list."""
        response = allowed_user_client.get('/complete-list')
        assert response.status_code == 200

    def test_system_design_accessible_for_allowed_user(self, allowed_user_client):
        """Test that allowed users can access system design."""
        response = allowed_user_client.get('/system-design/')
        assert response.status_code == 200


class TestGuidesRoutesAuthenticated:
    """Tests for guides routes with authenticated users."""

    def test_guides_redirects_to_classroom(self, guides_client):
        """Test that /guides redirects to classroom (legacy URL redirect)."""
        response = guides_client.get('/guides')
        assert response.status_code == 302
        assert '/' == response.location or response.location.endswith('/')

    def test_guides_resume_accessible_with_guides_access(self, guides_client):
        """Test that guides/resume is accessible with guides access."""
        response = guides_client.get('/guides/resume')
        assert response.status_code == 200

    def test_guides_job_search_accessible_with_guides_access(self, guides_client):
        """Test that guides/job-search is accessible with guides access."""
        response = guides_client.get('/guides/job-search')
        assert response.status_code == 200

    def test_guides_leetcode_accessible_with_full_access(self, full_access_client):
        """Test that guides/leetcode is accessible with full access."""
        response = full_access_client.get('/guides/leetcode')
        assert response.status_code == 200

    def test_guides_behavioral_accessible_with_ai_access(self, full_access_client):
        """Test that guides/behavioral is accessible with AI access."""
        response = full_access_client.get('/guides/behavioral')
        assert response.status_code == 200

    def test_guides_resume_accessible_for_allowed_user(self, allowed_user_client):
        """Test that allowed users can access guide wrapper pages."""
        response = allowed_user_client.get('/guides/resume')
        assert response.status_code == 200


class TestSystemDesignRoutesAuthenticated:
    """Tests for system design routes with authenticated users."""

    def test_system_design_accessible_with_access(self, authenticated_client):
        """Test system design accessible with system_design_access."""
        # authenticated_client has has_system_design_access: True
        response = authenticated_client.get('/system-design/')
        assert response.status_code == 200

    def test_system_design_real_life_accessible(self, authenticated_client):
        """Test real-life problems accessible with access."""
        response = authenticated_client.get('/system-design/real-life-problems')
        assert response.status_code == 200

    def test_system_design_trivia_accessible(self, authenticated_client):
        """Test trivia accessible with access."""
        response = authenticated_client.get('/system-design/trivia')
        assert response.status_code == 200

    def test_system_design_low_level_accessible(self, authenticated_client):
        """Test low-level design accessible with access."""
        response = authenticated_client.get('/system-design/low-level-design')
        assert response.status_code == 200


class TestAuthDebugWithUser:
    """Tests for auth debug endpoint with authenticated user."""

    def test_auth_debug_shows_authenticated(self, authenticated_client):
        """Test that auth debug shows authenticated status."""
        response = authenticated_client.get('/auth/debug')
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['has_premium'] is True
        assert data['has_system_design_access'] is True

    def test_auth_debug_shows_non_premium(self, non_premium_client):
        """Test that auth debug shows non-premium status."""
        response = non_premium_client.get('/auth/debug')
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['has_premium'] is False

    def test_auth_debug_shows_allowed_user(self, allowed_user_client):
        """Test that auth debug shows allowed user status."""
        response = allowed_user_client.get('/auth/debug')
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['is_allowed'] is True


class TestLogoutClearsSession:
    """Tests for logout functionality."""

    def test_logout_clears_user_session(self, authenticated_client):
        """Test that logout clears the user from session."""
        # Verify user is in session
        response = authenticated_client.get('/auth/debug')
        assert response.get_json()['authenticated'] is True

        # Logout
        response = authenticated_client.get('/auth/logout')
        assert response.status_code == 302

        # Verify user is no longer authenticated
        response = authenticated_client.get('/auth/debug')
        assert response.get_json()['authenticated'] is False


class TestContextProcessor:
    """Tests for template context processor."""

    def test_context_has_auth_variables(self, authenticated_client):
        """Test that templates have access to auth variables."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        # The page should render without errors, meaning context vars are available

    def test_context_with_unauthenticated_user(self, client):
        """Test context processor with unauthenticated user."""
        response = client.get('/')
        assert response.status_code == 200
