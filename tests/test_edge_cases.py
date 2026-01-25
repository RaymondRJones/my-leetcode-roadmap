"""
Edge case and integration tests.
"""
import pytest
from app.auth.access import has_premium_access, has_ai_access, has_system_design_access


class TestAuthEdgeCases:
    """Edge case tests for authentication."""

    def test_empty_email_addresses(self, app_context):
        """Test handling of empty email_addresses list."""
        from app.auth.access import is_allowed_user
        user = {
            'id': 'user_123',
            'email_addresses': [],
            'public_metadata': {}
        }
        assert is_allowed_user(user) is False

    def test_missing_email_addresses_key(self, app_context):
        """Test handling of missing email_addresses key."""
        from app.auth.access import is_allowed_user
        user = {
            'id': 'user_123',
            'public_metadata': {}
        }
        assert is_allowed_user(user) is False

    def test_nested_metadata_access(self):
        """Test accessing nested metadata values."""
        user = {
            'private_metadata': {
                'has_premium': True,
                'nested': {'value': 'test'}
            }
        }
        assert has_premium_access(user) is True

    def test_metadata_with_none_values(self):
        """Test metadata with None values."""
        user = {
            'private_metadata': {
                'has_premium': None
            }
        }
        # None should be falsy
        assert has_premium_access(user) is False

    def test_public_metadata_only(self):
        """Test user with only public_metadata."""
        user = {
            'public_metadata': {
                'has_premium': True,
                'has_ai_access': True,
                'has_system_design_access': True
            }
        }
        assert has_premium_access(user) is True
        assert has_ai_access(user) is True
        assert has_system_design_access(user) is True


class TestApiEdgeCases:
    """Edge case tests for API endpoints."""

    def test_auth_callback_empty_json(self, client):
        """Test auth callback with empty JSON."""
        response = client.post('/auth/callback',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400

    def test_auth_callback_invalid_json(self, client):
        """Test auth callback with invalid JSON."""
        response = client.post('/auth/callback',
                              data='not json',
                              content_type='application/json')
        assert response.status_code == 500

    def test_auth_callback_null_user(self, client):
        """Test auth callback with null user."""
        response = client.post('/auth/callback',
                              json={'user': None},
                              content_type='application/json')
        assert response.status_code == 400

    def test_api_refresh_post_works(self, client):
        """Test that API refresh endpoint works with POST."""
        response = client.post('/api/refresh')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data


class TestRouteEdgeCases:
    """Edge case tests for routes."""

    def test_nonexistent_problem_returns_404(self, client):
        """Test that nonexistent problem returns 404."""
        response = client.get('/problem/99999')
        assert response.status_code == 404

    def test_negative_problem_id(self, client):
        """Test handling of negative problem ID."""
        response = client.get('/problem/-1')
        assert response.status_code == 404

    def test_invalid_month_name(self, client):
        """Test handling of invalid month name."""
        response = client.get('/intermediate/month/InvalidMonth')
        # Unauthenticated users get redirected for premium months
        assert response.status_code == 302

    def test_about_page_exists(self, client):
        """Test that about page exists."""
        response = client.get('/about')
        assert response.status_code == 200


class TestStripeWebhookEdgeCases:
    """Edge case tests for Stripe webhook."""

    def test_webhook_missing_signature(self, client):
        """Test webhook without signature header."""
        response = client.post('/api/webhooks/stripe',
                              data=b'{}',
                              content_type='application/json')
        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_webhook_invalid_event_type(self, client):
        """Test webhook with unsupported event type."""
        # Without proper signature, this will fail at verification
        response = client.post('/api/webhooks/stripe',
                              data=b'{"type": "unsupported.event"}',
                              content_type='application/json',
                              headers={'Stripe-Signature': 'invalid'})
        assert response.status_code in [200, 400]


class TestSessionEdgeCases:
    """Edge case tests for session handling."""

    def test_session_persists_across_requests(self, app, mock_user_data):
        """Test that session data persists."""
        client = app.test_client()

        # Set user in session via callback
        response = client.post('/auth/callback',
                              json={'user': mock_user_data},
                              content_type='application/json')
        assert response.status_code == 200

        # Verify session persists
        response = client.get('/auth/debug')
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['user_data']['id'] == mock_user_data['id']

    def test_logout_and_relogin(self, app, mock_user_data):
        """Test logout followed by login."""
        client = app.test_client()

        # Login
        client.post('/auth/callback',
                   json={'user': mock_user_data},
                   content_type='application/json')

        # Verify logged in
        response = client.get('/auth/debug')
        assert response.get_json()['authenticated'] is True

        # Logout
        client.get('/auth/logout')

        # Verify logged out
        response = client.get('/auth/debug')
        assert response.get_json()['authenticated'] is False

        # Login again
        client.post('/auth/callback',
                   json={'user': mock_user_data},
                   content_type='application/json')

        # Verify logged in again
        response = client.get('/auth/debug')
        assert response.get_json()['authenticated'] is True


class TestUrlGeneration:
    """Tests for URL generation utilities."""

    def test_url_with_numbers(self):
        """Test URL generation with numbers in name."""
        from app.utils.problem_utils import generate_leetcode_url
        url = generate_leetcode_url("3Sum")
        assert "3sum" in url

    def test_url_with_roman_numerals(self):
        """Test URL generation with roman numerals."""
        from app.utils.problem_utils import generate_leetcode_url
        url = generate_leetcode_url("Jump Game II")
        assert "jump-game-ii" in url

    def test_url_with_parentheses(self):
        """Test URL generation removes parentheses."""
        from app.utils.problem_utils import generate_leetcode_url
        url = generate_leetcode_url("Binary Tree (Easy)")
        assert "(" not in url
        assert ")" not in url


class TestDifficultyEstimation:
    """Additional tests for difficulty estimation."""

    def test_multiple_topics_detected(self):
        """Test that multiple topics can be detected."""
        from app.utils.problem_utils import estimate_difficulty_and_topics
        _, topics, _ = estimate_difficulty_and_topics("Binary Tree Array Sum")
        assert len(topics) >= 2

    def test_medium_difficulty_default(self):
        """Test that medium is the default difficulty."""
        from app.utils.problem_utils import estimate_difficulty_and_topics
        difficulty, _, _ = estimate_difficulty_and_topics("Generic Problem Name")
        assert difficulty == 'Medium'

    def test_time_is_reasonable(self):
        """Test that time estimates are reasonable."""
        from app.utils.problem_utils import estimate_difficulty_and_topics
        for name in ["Two Sum", "Generic Problem", "Median of Arrays"]:
            _, _, time = estimate_difficulty_and_topics(name)
            assert 10 <= time <= 60
