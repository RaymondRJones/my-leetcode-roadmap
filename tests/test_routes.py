"""
Tests for routes module.
"""
import pytest
from flask import session


class TestPublicRoutes:
    """Tests for public routes that don't require authentication."""

    def test_homepage_returns_200(self, client):
        """Test that homepage returns 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_homepage_contains_courses(self, client):
        """Test that homepage contains course content."""
        response = client.get('/')
        assert b'Beginner' in response.data or b'course' in response.data.lower()

    def test_classroom_redirects_to_homepage(self, client):
        """Test that /classroom redirects to /."""
        response = client.get('/classroom')
        assert response.status_code == 302
        assert response.location == '/'

    def test_landing_page_returns_200(self, client):
        """Test that landing page returns 200."""
        response = client.get('/landing')
        assert response.status_code == 200

    def test_beginner_page_returns_200(self, client):
        """Test that beginner page returns 200."""
        response = client.get('/beginner')
        assert response.status_code == 200

    def test_intermediate_page_returns_200(self, client):
        """Test that intermediate page returns 200."""
        response = client.get('/intermediate')
        assert response.status_code == 200

    def test_roadmap_page_returns_200(self, client):
        """Test that software roadmap page returns 200."""
        response = client.get('/roadmap')
        assert response.status_code == 200

    def test_python_assessment_returns_200(self, client):
        """Test that Python assessment page returns 200."""
        response = client.get('/python-assessment')
        assert response.status_code == 200

    def test_java_assessment_returns_200(self, client):
        """Test that Java assessment page returns 200."""
        response = client.get('/java-assessment')
        assert response.status_code == 200

    def test_privacy_policy_returns_200(self, client):
        """Test that privacy policy page returns 200."""
        response = client.get('/privacy')
        assert response.status_code == 200

    def test_terms_of_service_returns_200(self, client):
        """Test that terms of service page returns 200."""
        response = client.get('/terms')
        assert response.status_code == 200

    def test_intermediate_month_1_is_free(self, client):
        """Test that intermediate Month 1 is accessible without auth."""
        response = client.get('/intermediate/month/Month 1')
        assert response.status_code == 200


class TestPremiumRoutes:
    """Tests for premium routes that require authentication."""

    def test_advanced_redirects_without_auth(self, client):
        """Test that advanced page redirects without authentication."""
        response = client.get('/advanced')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_complete_list_redirects_without_auth(self, client):
        """Test that complete-list redirects without authentication."""
        response = client.get('/complete-list')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_guides_redirects_without_auth(self, client):
        """Test that guides page redirects without authentication."""
        response = client.get('/guides')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_behavioral_guide_redirects_without_auth(self, client):
        """Test that behavioral guide redirects without authentication."""
        response = client.get('/behavioral-guide')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_intermediate_month_2_redirects_without_auth(self, client):
        """Test that intermediate Month 2 redirects without authentication."""
        response = client.get('/intermediate/month/Month 2')
        assert response.status_code == 302


class TestSystemDesignRoutes:
    """Tests for system design routes."""

    def test_system_design_redirects_without_auth(self, client):
        """Test that system design page redirects without authentication."""
        response = client.get('/system-design/')
        assert response.status_code == 302
        assert '/landing' in response.location

    def test_real_life_problems_redirects_without_auth(self, client):
        """Test that real-life problems redirects without authentication."""
        response = client.get('/system-design/real-life-problems')
        assert response.status_code == 302

    def test_trivia_redirects_without_auth(self, client):
        """Test that trivia page redirects without authentication."""
        response = client.get('/system-design/trivia')
        assert response.status_code == 302

    def test_low_level_design_redirects_without_auth(self, client):
        """Test that low-level design redirects without authentication."""
        response = client.get('/system-design/low-level-design')
        assert response.status_code == 302


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_login_page_returns_200(self, client):
        """Test that login page returns 200."""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_logout_redirects_to_homepage(self, client):
        """Test that logout redirects to homepage."""
        response = client.get('/auth/logout')
        assert response.status_code == 302
        assert response.location == '/'

    def test_auth_status_returns_200(self, client):
        """Test that auth status page returns 200."""
        response = client.get('/auth/status')
        assert response.status_code == 200

    def test_auth_debug_returns_json(self, client):
        """Test that auth debug returns JSON."""
        response = client.get('/auth/debug')
        assert response.status_code == 200
        data = response.get_json()
        assert 'authenticated' in data
        assert 'has_premium' in data

    def test_auth_callback_requires_post(self, client):
        """Test that auth callback requires POST method."""
        response = client.get('/auth/callback')
        assert response.status_code == 405

    def test_auth_callback_accepts_post(self, client):
        """Test that auth callback accepts POST."""
        response = client.post('/auth/callback',
                              json={'user': {'id': 'test'}},
                              content_type='application/json')
        assert response.status_code == 200

    def test_auth_callback_stores_user_in_session(self, app, client):
        """Test that auth callback stores user in session."""
        with client.session_transaction() as sess:
            assert 'user' not in sess

        response = client.post('/auth/callback',
                              json={'user': {'id': 'test_user'}},
                              content_type='application/json')

        with client.session_transaction() as sess:
            assert 'user' in sess
            assert sess['user']['id'] == 'test_user'


class TestApiRoutes:
    """Tests for API routes."""

    def test_api_test_returns_200(self, client):
        """Test that API test endpoint returns 200."""
        response = client.get('/api/test')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'API working'

    def test_api_roadmap_returns_json(self, client):
        """Test that API roadmap returns JSON."""
        response = client.get('/api/roadmap')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    def test_api_atcoder_returns_json(self, client):
        """Test that API atcoder returns JSON."""
        response = client.get('/api/atcoder')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    def test_api_refresh_requires_post(self, client):
        """Test that API refresh requires POST method."""
        response = client.get('/api/refresh')
        assert response.status_code == 405

    def test_api_behavioral_feedback_redirects_without_auth(self, client):
        """Test that behavioral feedback redirects without auth."""
        response = client.post('/api/behavioral-feedback',
                              json={'question': 'test', 'story': 'test'})
        assert response.status_code == 302

    def test_stripe_webhook_accepts_post(self, client):
        """Test that Stripe webhook endpoint accepts POST."""
        response = client.post('/api/webhooks/stripe',
                              data=b'{}',
                              content_type='application/json')
        # Will return 200 even on errors for webhook resilience
        assert response.status_code in [200, 400]


class TestMonthRedirects:
    """Tests for month route redirects."""

    def test_old_month_url_redirects(self, client):
        """Test that old month URL format redirects."""
        response = client.get('/month/Month 1')
        assert response.status_code == 302
        # URL may be encoded (Month%201) or unencoded (Month 1)
        assert '/intermediate/month/Month' in response.location
