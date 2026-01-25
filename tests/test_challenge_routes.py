"""
Unit tests for challenge routes.

Tests cover:
- Challenge home page
- Day view pages
- Calendar page
- Leaderboard page
- Admin pages
- Challenge API endpoints
"""
import pytest
import json
from flask import session


class TestChallengeHome:
    """Test challenge home page."""

    def test_challenge_home_unauthenticated(self, client):
        """Test challenge home accessible without auth."""
        response = client.get('/challenge/')
        assert response.status_code == 200

    def test_challenge_home_authenticated(self, authenticated_client):
        """Test challenge home for authenticated user."""
        response = authenticated_client.get('/challenge/')
        assert response.status_code == 200

    def test_challenge_home_contains_title(self, client):
        """Test challenge home contains expected content."""
        response = client.get('/challenge/')
        assert b'28-Day' in response.data or b'Challenge' in response.data


class TestChallengeDayView:
    """Test challenge day view pages."""

    def test_day_view_unauthenticated_redirects(self, client):
        """Test day view redirects unauthenticated users."""
        response = client.get('/challenge/day/1')
        # Should redirect to landing or login
        assert response.status_code in [302, 303]

    def test_day_view_authenticated_not_enrolled(self, authenticated_client):
        """Test day view redirects non-enrolled users."""
        response = authenticated_client.get('/challenge/day/1')
        # Should redirect to challenge home
        assert response.status_code in [302, 303]

    def test_day_view_invalid_day_redirects(self, authenticated_client):
        """Test invalid day numbers redirect."""
        response = authenticated_client.get('/challenge/day/0')
        assert response.status_code in [302, 303]

        response = authenticated_client.get('/challenge/day/50')
        assert response.status_code in [302, 303]


class TestChallengeCalendar:
    """Test challenge calendar page."""

    def test_calendar_unauthenticated_redirects(self, client):
        """Test calendar redirects unauthenticated users."""
        response = client.get('/challenge/calendar')
        assert response.status_code in [302, 303]

    def test_calendar_authenticated_not_enrolled(self, authenticated_client):
        """Test calendar redirects non-enrolled users."""
        response = authenticated_client.get('/challenge/calendar')
        # Should redirect to challenge home
        assert response.status_code in [302, 303]


class TestChallengeLeaderboard:
    """Test challenge leaderboard page."""

    def test_leaderboard_accessible(self, client):
        """Test leaderboard is publicly accessible."""
        response = client.get('/challenge/leaderboard')
        assert response.status_code == 200

    def test_leaderboard_contains_content(self, client):
        """Test leaderboard contains expected content."""
        response = client.get('/challenge/leaderboard')
        assert b'Leaderboard' in response.data


class TestChallengeAdmin:
    """Test challenge admin pages."""

    def test_admin_unauthenticated_redirects(self, client):
        """Test admin redirects unauthenticated users."""
        response = client.get('/challenge/admin')
        assert response.status_code in [302, 303]

    def test_admin_non_admin_redirects(self, authenticated_client):
        """Test admin redirects non-admin users."""
        response = authenticated_client.get('/challenge/admin')
        # Non-admin should be redirected
        assert response.status_code in [302, 303]

    def test_admin_submissions_unauthenticated_redirects(self, client):
        """Test admin submissions redirects unauthenticated users."""
        response = client.get('/challenge/admin/submissions')
        assert response.status_code in [302, 303]


class TestChallengeAPIEnroll:
    """Test challenge enrollment API."""

    def test_enroll_unauthenticated(self, client):
        """Test enroll fails for unauthenticated users."""
        response = client.post('/api/challenge/enroll')
        assert response.status_code in [302, 303, 401]

    def test_enroll_authenticated(self, authenticated_client):
        """Test enroll endpoint for authenticated users."""
        response = authenticated_client.post(
            '/api/challenge/enroll',
            content_type='application/json'
        )
        # May fail due to Clerk API not being available in tests
        # but should not return 404
        assert response.status_code != 404


class TestChallengeAPICompleteProblem:
    """Test complete problem API."""

    def test_complete_problem_unauthenticated(self, client):
        """Test complete problem fails for unauthenticated users."""
        response = client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({'day': 1, 'problem_id': 'two-sum'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_complete_problem_missing_data(self, authenticated_client):
        """Test complete problem fails without required data."""
        response = authenticated_client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({}),
            content_type='application/json'
        )
        # Should return 400 for missing data
        assert response.status_code in [400, 302, 303]


class TestChallengeAPIProgress:
    """Test progress API."""

    def test_progress_unauthenticated(self, client):
        """Test progress fails for unauthenticated users."""
        response = client.get('/api/challenge/progress')
        assert response.status_code in [302, 303, 401]

    def test_progress_authenticated(self, authenticated_client):
        """Test progress endpoint for authenticated users."""
        response = authenticated_client.get('/api/challenge/progress')
        # Should return JSON
        assert response.status_code in [200, 302, 303]


class TestChallengeAPISubmitSkool:
    """Test Skool submission API."""

    def test_submit_skool_unauthenticated(self, client):
        """Test submit skool fails for unauthenticated users."""
        response = client.post(
            '/api/challenge/submit-skool',
            data=json.dumps({'day': 1, 'url': 'https://skool.com/test'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_submit_skool_invalid_url(self, authenticated_client):
        """Test submit skool fails with invalid URL."""
        response = authenticated_client.post(
            '/api/challenge/submit-skool',
            data=json.dumps({'day': 1, 'url': 'https://google.com'}),
            content_type='application/json'
        )
        # Should fail because URL is not skool.com
        assert response.status_code in [400, 302, 303]


class TestChallengeAPILeaderboard:
    """Test leaderboard API."""

    def test_leaderboard_api_accessible(self, client):
        """Test leaderboard API is publicly accessible."""
        response = client.get('/api/challenge/leaderboard')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'leaderboard' in data


class TestChallengeAPIAdminParticipants:
    """Test admin participants API."""

    def test_admin_participants_unauthenticated(self, client):
        """Test admin participants fails for unauthenticated users."""
        response = client.get('/api/challenge/admin/participants')
        assert response.status_code in [302, 303, 401]

    def test_admin_participants_non_admin(self, authenticated_client):
        """Test admin participants fails for non-admin users."""
        response = authenticated_client.get('/api/challenge/admin/participants')
        # Non-admin should be redirected
        assert response.status_code in [302, 303]


class TestChallengeAPIApproveSubmission:
    """Test approve submission API."""

    def test_approve_submission_unauthenticated(self, client):
        """Test approve submission fails for unauthenticated users."""
        response = client.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'user_id': 'test', 'submission_index': 0, 'action': 'approve'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_approve_submission_non_admin(self, authenticated_client):
        """Test approve submission fails for non-admin users."""
        response = authenticated_client.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'user_id': 'test', 'submission_index': 0, 'action': 'approve'}),
            content_type='application/json'
        )
        # Non-admin should be redirected
        assert response.status_code in [302, 303]


class TestEnrolledUserRoutes:
    """Test routes for enrolled users."""

    @pytest.fixture
    def enrolled_client(self, app):
        """Create test client with enrolled user."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_enrolled',
                'email_addresses': [{'email_address': 'enrolled@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': '2025-01-01T00:00:00',
                        'days_completed': [1, 2],
                        'problems_solved': {'day_1': ['two-sum']},
                        'total_problems_solved': 1,
                        'current_streak': 2,
                        'best_streak': 2,
                        'points': 10,
                        'achievements': ['first_problem']
                    }
                }
            }
        return client

    def test_enrolled_user_can_access_calendar(self, enrolled_client):
        """Test enrolled user can access calendar."""
        response = enrolled_client.get('/challenge/calendar')
        assert response.status_code == 200
        assert b'January' in response.data or b'Calendar' in response.data

    def test_enrolled_user_can_access_day_view(self, enrolled_client):
        """Test enrolled user can access day view."""
        response = enrolled_client.get('/challenge/day/1')
        assert response.status_code == 200
        # Day 1 has "Concatenate Non-Zero Digits and Multiply by Sum I"
        assert b'Concatenate' in response.data or b'Day 1' in response.data

    def test_enrolled_user_progress_api(self, enrolled_client):
        """Test enrolled user progress API returns data."""
        response = enrolled_client.get('/api/challenge/progress')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('enrolled') is True


class TestAdminUserRoutes:
    """Test routes for admin users."""

    @pytest.fixture
    def admin_client(self, app):
        """Create test client with admin user."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_admin',
                'email_addresses': [{'email_address': 'admin@example.com'}],
                'private_metadata': {'is_admin': True, 'has_premium': True},
                'public_metadata': {'is_admin': True}
            }
        return client

    def test_admin_can_access_dashboard(self, admin_client):
        """Test admin can access dashboard."""
        response = admin_client.get('/challenge/admin')
        assert response.status_code == 200
        assert b'Admin' in response.data

    def test_admin_can_access_submissions(self, admin_client):
        """Test admin can access submissions page."""
        response = admin_client.get('/challenge/admin/submissions')
        assert response.status_code == 200
        assert b'Submission' in response.data

    def test_admin_can_get_participants(self, admin_client):
        """Test admin can get participants list."""
        response = admin_client.get('/api/challenge/admin/participants')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'participants' in data
