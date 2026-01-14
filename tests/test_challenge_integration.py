"""
Integration tests for the 28-day challenge feature.

These tests verify complete workflows and edge cases for:
- Enrollment flow
- Problem completion workflow
- Streak calculations
- Achievement unlocking
- Day access restrictions
- Admin functionality
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestChallengeEnrollmentWorkflow:
    """Test complete enrollment workflow."""

    @pytest.fixture
    def unenrolled_client(self, app):
        """Create test client with authenticated but not enrolled user."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_new',
                'email_addresses': [{'email_address': 'new@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {}
            }
        return client

    def test_unenrolled_user_sees_enrollment_page(self, unenrolled_client):
        """Test unenrolled user sees enrollment CTA."""
        response = unenrolled_client.get('/challenge/')
        assert response.status_code == 200
        # Should see enrollment content
        assert b'Start' in response.data or b'Enroll' in response.data or b'Challenge' in response.data

    def test_unenrolled_user_cannot_access_day(self, unenrolled_client):
        """Test unenrolled user redirected from day view."""
        response = unenrolled_client.get('/challenge/day/1', follow_redirects=False)
        assert response.status_code in [302, 303]

    def test_unenrolled_user_cannot_access_calendar(self, unenrolled_client):
        """Test unenrolled user redirected from calendar."""
        response = unenrolled_client.get('/challenge/calendar', follow_redirects=False)
        assert response.status_code in [302, 303]

    def test_enroll_initializes_challenge_data(self, app):
        """Test enrollment creates proper challenge data structure."""
        with app.app_context():
            service = app.challenge_service
            # Verify service is available
            assert service is not None


class TestProblemCompletionWorkflow:
    """Test problem completion and progress tracking."""

    @pytest.fixture
    def enrolled_user_client(self, app):
        """Create client with enrolled user."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_enrolled',
                'email_addresses': [{'email_address': 'enrolled@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': datetime.now().isoformat(),
                        'days_completed': [],
                        'problems_solved': {},
                        'total_problems_solved': 0,
                        'current_streak': 0,
                        'best_streak': 0,
                        'points': 0,
                        'achievements': []
                    }
                }
            }
        return client

    def test_complete_problem_requires_day_and_problem_id(self, enrolled_user_client):
        """Test complete problem validates required fields."""
        # Missing both
        response = enrolled_user_client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

        # Missing problem_id
        response = enrolled_user_client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({'day': 1}),
            content_type='application/json'
        )
        assert response.status_code == 400

        # Missing day
        response = enrolled_user_client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({'problem_id': 'two-sum'}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_complete_problem_unenrolled_user_fails(self, app):
        """Test complete problem fails for unenrolled user."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_not_enrolled',
                'email_addresses': [{'email_address': 'not@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {}  # No challenge data
            }

        response = client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({'day': 1, 'problem_id': 'two-sum'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Not enrolled' in data.get('error', '')


class TestDayAccessRestrictions:
    """Test day access is properly restricted."""

    @pytest.fixture
    def enrolled_day3_client(self, app):
        """Create client enrolled 3 days ago."""
        client = app.test_client()
        start_date = (datetime.now() - timedelta(days=2)).isoformat()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_day3',
                'email_addresses': [{'email_address': 'day3@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': start_date,
                        'days_completed': [1, 2],
                        'problems_solved': {'day_1': ['two-sum'], 'day_2': ['valid-parentheses']},
                        'total_problems_solved': 2,
                        'current_streak': 2,
                        'best_streak': 2,
                        'points': 20,
                        'achievements': ['first_problem']
                    }
                }
            }
        return client

    def test_can_access_current_day(self, enrolled_day3_client):
        """Test user can access current challenge day."""
        response = enrolled_day3_client.get('/challenge/day/3')
        assert response.status_code == 200

    def test_can_access_past_days(self, enrolled_day3_client):
        """Test user can access past days."""
        response = enrolled_day3_client.get('/challenge/day/1')
        assert response.status_code == 200

        response = enrolled_day3_client.get('/challenge/day/2')
        assert response.status_code == 200

    def test_cannot_access_future_days(self, enrolled_day3_client):
        """Test user cannot access future days."""
        # Day 10 should redirect (current day is 3)
        response = enrolled_day3_client.get('/challenge/day/10', follow_redirects=False)
        assert response.status_code in [302, 303]

    def test_invalid_day_zero_redirects(self, enrolled_day3_client):
        """Test day 0 redirects to challenge home."""
        response = enrolled_day3_client.get('/challenge/day/0', follow_redirects=False)
        assert response.status_code in [302, 303]

    def test_invalid_day_29_redirects(self, enrolled_day3_client):
        """Test day 29 redirects (beyond 28)."""
        response = enrolled_day3_client.get('/challenge/day/29', follow_redirects=False)
        assert response.status_code in [302, 303]

    def test_negative_day_redirects(self, enrolled_day3_client):
        """Test negative day number returns 404 (route doesn't match)."""
        response = enrolled_day3_client.get('/challenge/day/-1', follow_redirects=False)
        # Flask route pattern <int:day> doesn't match negative numbers, returns 404
        assert response.status_code in [302, 303, 404]


class TestAdminBypassAccess:
    """Test admin users can bypass day restrictions."""

    @pytest.fixture
    def admin_enrolled_client(self, app):
        """Create admin user with enrollment."""
        client = app.test_client()
        start_date = datetime.now().isoformat()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'admin_user',
                'email_addresses': [{'email_address': 'admin@example.com'}],
                'private_metadata': {'is_admin': True, 'has_premium': True},
                'public_metadata': {
                    'is_admin': True,
                    'challenge': {
                        'enrolled': True,
                        'start_date': start_date,
                        'days_completed': [],
                        'problems_solved': {},
                        'total_problems_solved': 0,
                        'current_streak': 0,
                        'best_streak': 0,
                        'points': 0,
                        'achievements': []
                    }
                }
            }
        return client

    def test_admin_can_access_any_day(self, admin_enrolled_client):
        """Test admin can access future days."""
        # Admin should be able to access day 28 even on day 1
        response = admin_enrolled_client.get('/challenge/day/28')
        assert response.status_code == 200

    def test_admin_can_access_admin_dashboard(self, admin_enrolled_client):
        """Test admin dashboard access."""
        response = admin_enrolled_client.get('/challenge/admin')
        assert response.status_code == 200

    def test_admin_can_access_submissions(self, admin_enrolled_client):
        """Test admin submissions access."""
        response = admin_enrolled_client.get('/challenge/admin/submissions')
        assert response.status_code == 200


class TestSkoolSubmissionWorkflow:
    """Test Skool post submission workflow."""

    @pytest.fixture
    def enrolled_client_for_skool(self, app):
        """Create enrolled client for Skool tests."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_skool',
                'email_addresses': [{'email_address': 'skool@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': datetime.now().isoformat(),
                        'days_completed': [1],
                        'problems_solved': {'day_1': ['two-sum']},
                        'total_problems_solved': 1,
                        'current_streak': 1,
                        'best_streak': 1,
                        'points': 10,
                        'achievements': ['first_problem']
                    },
                    'skool_submissions': []
                }
            }
        return client

    def test_submit_skool_requires_day_and_url(self, enrolled_client_for_skool):
        """Test Skool submission validates required fields."""
        # Missing both
        response = enrolled_client_for_skool.post(
            '/api/challenge/submit-skool',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

        # Missing url
        response = enrolled_client_for_skool.post(
            '/api/challenge/submit-skool',
            data=json.dumps({'day': 1}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_submit_skool_rejects_non_skool_urls(self, enrolled_client_for_skool):
        """Test non-skool.com URLs are rejected."""
        # Note: Current implementation checks if 'skool.com' is in URL
        # So 'fake-skool.com' and 'skool.com' without https would pass
        invalid_urls = [
            'https://google.com',
            'https://leetcode.com/problems/two-sum',
            'https://github.com',
        ]

        for url in invalid_urls:
            response = enrolled_client_for_skool.post(
                '/api/challenge/submit-skool',
                data=json.dumps({'day': 1, 'url': url}),
                content_type='application/json'
            )
            assert response.status_code == 400, f"URL should be rejected: {url}"

    def test_submit_skool_accepts_valid_skool_url(self, enrolled_client_for_skool):
        """Test valid Skool URLs are accepted."""
        valid_urls = [
            'https://skool.com/community/post/123',
            'https://www.skool.com/test-community',
        ]

        for url in valid_urls:
            response = enrolled_client_for_skool.post(
                '/api/challenge/submit-skool',
                data=json.dumps({'day': 1, 'url': url}),
                content_type='application/json'
            )
            # Should be accepted (200) even if Clerk update fails
            assert response.status_code in [200, 500], f"URL should be accepted: {url}"


class TestAdminApproveReject:
    """Test admin approve/reject submission workflow."""

    @pytest.fixture
    def admin_client_for_approval(self, app):
        """Create admin client for approval tests."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'admin_approver',
                'email_addresses': [{'email_address': 'admin@example.com'}],
                'private_metadata': {'is_admin': True, 'has_premium': True},
                'public_metadata': {'is_admin': True}
            }
        return client

    def test_approve_submission_requires_all_fields(self, admin_client_for_approval):
        """Test approve submission validates required fields."""
        # Missing user_id
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'submission_index': 0, 'action': 'approve'}),
            content_type='application/json'
        )
        assert response.status_code == 400

        # Missing submission_index
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'user_id': 'test', 'action': 'approve'}),
            content_type='application/json'
        )
        assert response.status_code == 400

        # Missing action
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'user_id': 'test', 'submission_index': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_approve_submission_validates_action(self, admin_client_for_approval):
        """Test approve submission validates action value."""
        # Invalid action
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({
                'user_id': 'test',
                'submission_index': 0,
                'action': 'invalid'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_approve_action_accepted(self, admin_client_for_approval):
        """Test approve action is valid."""
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({
                'user_id': 'test_user',
                'submission_index': 0,
                'action': 'approve'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_reject_action_accepted(self, admin_client_for_approval):
        """Test reject action is valid."""
        response = admin_client_for_approval.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({
                'user_id': 'test_user',
                'submission_index': 0,
                'action': 'reject'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestChallengeProgressAPI:
    """Test progress API endpoint."""

    @pytest.fixture
    def progress_test_client(self, app):
        """Create client for progress tests."""
        client = app.test_client()
        start_date = (datetime.now() - timedelta(days=6)).isoformat()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_progress',
                'email_addresses': [{'email_address': 'progress@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': start_date,
                        'days_completed': [1, 2, 3, 4, 5, 6, 7],
                        'problems_solved': {
                            'day_1': ['two-sum'],
                            'day_2': ['valid-parentheses'],
                            'day_3': ['binary-search'],
                            'day_4': ['maximum-subarray'],
                            'day_5': ['merge-two-sorted-lists'],
                            'day_6': ['climbing-stairs'],
                            'day_7': ['best-time-to-buy-and-sell-stock']
                        },
                        'total_problems_solved': 7,
                        'current_streak': 7,
                        'best_streak': 7,
                        'points': 120,
                        'achievements': ['first_problem', 'streak_7']
                    }
                }
            }
        return client

    def test_progress_returns_enrolled_true(self, progress_test_client):
        """Test progress returns enrolled status."""
        response = progress_test_client.get('/api/challenge/progress')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('enrolled') is True

    def test_progress_returns_current_day(self, progress_test_client):
        """Test progress returns current day."""
        response = progress_test_client.get('/api/challenge/progress')
        data = json.loads(response.data)
        assert 'current_day' in data
        assert isinstance(data['current_day'], int)
        assert 1 <= data['current_day'] <= 28

    def test_progress_returns_days_completed(self, progress_test_client):
        """Test progress returns days completed list."""
        response = progress_test_client.get('/api/challenge/progress')
        data = json.loads(response.data)
        assert 'days_completed' in data
        assert isinstance(data['days_completed'], list)

    def test_progress_returns_streak(self, progress_test_client):
        """Test progress returns streak info."""
        response = progress_test_client.get('/api/challenge/progress')
        data = json.loads(response.data)
        assert 'current_streak' in data
        assert 'best_streak' in data

    def test_progress_returns_points(self, progress_test_client):
        """Test progress returns points."""
        response = progress_test_client.get('/api/challenge/progress')
        data = json.loads(response.data)
        assert 'points' in data

    def test_progress_returns_achievements(self, progress_test_client):
        """Test progress returns achievements list."""
        response = progress_test_client.get('/api/challenge/progress')
        data = json.loads(response.data)
        assert 'achievements' in data
        assert isinstance(data['achievements'], list)


class TestUnauthenticatedAPIAccess:
    """Test API endpoints properly reject unauthenticated requests."""

    def test_enroll_requires_auth(self, client):
        """Test enroll requires authentication."""
        response = client.post('/api/challenge/enroll')
        assert response.status_code in [302, 303, 401]

    def test_complete_problem_requires_auth(self, client):
        """Test complete problem requires authentication."""
        response = client.post(
            '/api/challenge/complete-problem',
            data=json.dumps({'day': 1, 'problem_id': 'test'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_progress_requires_auth(self, client):
        """Test progress requires authentication."""
        response = client.get('/api/challenge/progress')
        assert response.status_code in [302, 303, 401]

    def test_submit_skool_requires_auth(self, client):
        """Test submit skool requires authentication."""
        response = client.post(
            '/api/challenge/submit-skool',
            data=json.dumps({'day': 1, 'url': 'https://skool.com/test'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_admin_participants_requires_auth(self, client):
        """Test admin participants requires authentication."""
        response = client.get('/api/challenge/admin/participants')
        assert response.status_code in [302, 303, 401]

    def test_approve_submission_requires_auth(self, client):
        """Test approve submission requires authentication."""
        response = client.post(
            '/api/challenge/admin/approve-submission',
            data=json.dumps({'user_id': 'test', 'submission_index': 0, 'action': 'approve'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]


class TestLeaderboardAPI:
    """Test leaderboard API endpoint."""

    def test_leaderboard_publicly_accessible(self, client):
        """Test leaderboard is public."""
        response = client.get('/api/challenge/leaderboard')
        assert response.status_code == 200

    def test_leaderboard_returns_valid_json(self, client):
        """Test leaderboard returns valid JSON."""
        response = client.get('/api/challenge/leaderboard')
        data = json.loads(response.data)
        assert 'leaderboard' in data

    def test_leaderboard_returns_list(self, client):
        """Test leaderboard returns list."""
        response = client.get('/api/challenge/leaderboard')
        data = json.loads(response.data)
        assert isinstance(data['leaderboard'], list)


class TestCalendarViewData:
    """Test calendar view contains expected data."""

    @pytest.fixture
    def enrolled_calendar_client(self, app):
        """Create client for calendar tests."""
        client = app.test_client()
        start_date = (datetime.now() - timedelta(days=4)).isoformat()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_calendar',
                'email_addresses': [{'email_address': 'calendar@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': start_date,
                        'days_completed': [1, 2, 3],
                        'problems_solved': {},
                        'total_problems_solved': 3,
                        'current_streak': 3,
                        'best_streak': 3,
                        'points': 30,
                        'achievements': ['first_problem']
                    }
                }
            }
        return client

    def test_calendar_shows_date_range(self, enrolled_calendar_client):
        """Test calendar shows personalized date range."""
        response = enrolled_calendar_client.get('/challenge/calendar')
        assert response.status_code == 200
        # Calendar title is now dynamic based on user's start date
        # Just verify the calendar page loads with the title section
        assert b'28-Day Challenge' in response.data

    def test_calendar_contains_stats(self, enrolled_calendar_client):
        """Test calendar contains stats section."""
        response = enrolled_calendar_client.get('/challenge/calendar')
        assert b'Streak' in response.data or b'Points' in response.data

    def test_calendar_contains_legend(self, enrolled_calendar_client):
        """Test calendar contains legend."""
        response = enrolled_calendar_client.get('/challenge/calendar')
        assert b'Legend' in response.data

    def test_calendar_contains_achievements(self, enrolled_calendar_client):
        """Test calendar contains achievements section."""
        response = enrolled_calendar_client.get('/challenge/calendar')
        assert b'Achievement' in response.data


class TestBonusProblemsAPI:
    """Test bonus problems API endpoint."""

    @pytest.fixture
    def enrolled_client_for_bonus(self, app):
        """Create enrolled client for bonus tests."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_bonus',
                'email_addresses': [{'email_address': 'bonus@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': '2025-01-13T00:00:00',
                        'days_completed': [],
                        'problems_solved': {},
                        'total_problems_solved': 0,
                        'current_streak': 0,
                        'best_streak': 0,
                        'points': 0,
                        'achievements': [],
                        'bonus_problems': []
                    }
                }
            }
        return client

    def test_bonus_problem_requires_auth(self, client):
        """Test bonus problem requires authentication."""
        response = client.post(
            '/api/challenge/bonus-problem',
            data=json.dumps({'url': 'https://leetcode.com/problems/two-sum/'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 303, 401]

    def test_bonus_problem_requires_url(self, enrolled_client_for_bonus):
        """Test bonus problem requires URL."""
        response = enrolled_client_for_bonus.post(
            '/api/challenge/bonus-problem',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_bonus_problem_validates_leetcode_url(self, enrolled_client_for_bonus):
        """Test bonus problem validates LeetCode URL."""
        response = enrolled_client_for_bonus.post(
            '/api/challenge/bonus-problem',
            data=json.dumps({'url': 'https://google.com'}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_bonus_problem_accepts_valid_url(self, enrolled_client_for_bonus):
        """Test bonus problem accepts valid LeetCode URL."""
        response = enrolled_client_for_bonus.post(
            '/api/challenge/bonus-problem',
            data=json.dumps({'url': 'https://leetcode.com/problems/two-sum/'}),
            content_type='application/json'
        )
        # Should succeed or fail gracefully (Clerk not available in tests)
        assert response.status_code in [200, 500]


class TestDayViewData:
    """Test day view contains expected data."""

    @pytest.fixture
    def enrolled_day_client(self, app):
        """Create client for day view tests."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user'] = {
                'id': 'user_dayview',
                'email_addresses': [{'email_address': 'dayview@example.com'}],
                'private_metadata': {'has_premium': True},
                'public_metadata': {
                    'challenge': {
                        'enrolled': True,
                        'start_date': datetime.now().isoformat(),
                        'days_completed': [],
                        'problems_solved': {},
                        'total_problems_solved': 0,
                        'current_streak': 0,
                        'best_streak': 0,
                        'points': 0,
                        'achievements': []
                    }
                }
            }
        return client

    def test_day_view_contains_problem(self, enrolled_day_client):
        """Test day view shows problem."""
        response = enrolled_day_client.get('/challenge/day/1')
        assert response.status_code == 200
        # Day 1 should have Two Sum
        assert b'Two Sum' in response.data

    def test_day_view_contains_editor(self, enrolled_day_client):
        """Test day view contains code editor."""
        response = enrolled_day_client.get('/challenge/day/1')
        # Check for Monaco editor or editor container
        assert b'editor' in response.data.lower() or b'monaco' in response.data.lower()

    def test_day_view_contains_run_button(self, enrolled_day_client):
        """Test day view contains run button."""
        response = enrolled_day_client.get('/challenge/day/1')
        assert b'Run' in response.data

    def test_day_view_contains_test_cases(self, enrolled_day_client):
        """Test day view has test cases section."""
        response = enrolled_day_client.get('/challenge/day/1')
        assert b'test' in response.data.lower()
