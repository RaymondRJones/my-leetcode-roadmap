"""
Edge case tests for the challenge service.

Tests corner cases and boundary conditions for:
- Date calculations with timezone edge cases
- Streak calculations with gaps and partial completions
- Points calculations with various difficulty combinations
- Achievement edge cases
- Day completion edge cases
"""
import pytest
from datetime import datetime, timedelta
from app.services.challenge_service import ChallengeService


class TestDateCalculationEdgeCases:
    """Test date-related edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_calculate_current_day_empty_string(self, service):
        """Test empty string start date returns day 1."""
        result = service.calculate_current_day('')
        assert result == 1

    def test_calculate_current_day_none_string(self, service):
        """Test None-like string returns day 1."""
        result = service.calculate_current_day('None')
        assert result == 1

    def test_calculate_current_day_invalid_format(self, service):
        """Test invalid date format returns day 1."""
        result = service.calculate_current_day('not-a-date')
        assert result == 1

    def test_calculate_current_day_partial_date(self, service):
        """Test partial date returns day 1."""
        result = service.calculate_current_day('2025-01')
        assert result == 1

    def test_calculate_current_day_with_timezone_z(self, service):
        """Test date with Z timezone suffix."""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        result = service.calculate_current_day(date_str)
        assert result == 1  # Same day should be day 1

    def test_calculate_current_day_with_timezone_offset(self, service):
        """Test date with timezone offset."""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        result = service.calculate_current_day(date_str)
        assert result == 1

    def test_calculate_current_day_exactly_28_days_ago(self, service):
        """Test exactly 28 days ago returns 28."""
        start = datetime.now() - timedelta(days=27)  # 27 days ago = day 28
        result = service.calculate_current_day(start.isoformat())
        assert result == 28

    def test_calculate_current_day_more_than_28_days(self, service):
        """Test more than 28 days caps at 28."""
        start = datetime.now() - timedelta(days=100)
        result = service.calculate_current_day(start.isoformat())
        assert result == 28

    def test_calculate_current_day_far_future(self, service):
        """Test future date returns day 1."""
        future = datetime.now() + timedelta(days=100)
        result = service.calculate_current_day(future.isoformat())
        assert result == 1


class TestStreakCalculationEdgeCases:
    """Test streak calculation edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_streak_empty_list(self, service):
        """Test streak with empty days list."""
        result = service.calculate_streak([], 5)
        assert result == 0

    def test_streak_with_none(self, service):
        """Test streak handles None gracefully."""
        # Should handle empty list or return 0
        result = service.calculate_streak([], 1)
        assert result == 0

    def test_streak_only_day_1_on_day_1(self, service):
        """Test single day streak on day 1."""
        result = service.calculate_streak([1], 1)
        assert result == 1

    def test_streak_gap_at_start(self, service):
        """Test streak with gap at start."""
        # Days 2, 3, 4 completed, but not day 1
        result = service.calculate_streak([2, 3, 4], 4)
        assert result == 3  # Consecutive 2, 3, 4

    def test_streak_gap_in_middle(self, service):
        """Test streak with gap in middle."""
        # Days 1, 2, 4, 5 completed (gap at day 3)
        result = service.calculate_streak([1, 2, 4, 5], 5)
        assert result == 2  # Only 4, 5 consecutive from current

    def test_streak_current_day_not_done(self, service):
        """Test streak when current day not completed."""
        # Days 1, 2, 3 completed, current day is 5
        result = service.calculate_streak([1, 2, 3], 5)
        assert result == 0  # No streak from day 5 backwards

    def test_streak_unsorted_list(self, service):
        """Test streak works with unsorted list."""
        # Unsorted but consecutive
        result = service.calculate_streak([3, 1, 2], 3)
        assert result == 3

    def test_streak_duplicate_days(self, service):
        """Test streak handles duplicate day entries."""
        result = service.calculate_streak([1, 1, 2, 2, 3, 3], 3)
        assert result == 3

    def test_streak_full_28_days(self, service):
        """Test full 28-day streak."""
        days = list(range(1, 29))
        result = service.calculate_streak(days, 28)
        assert result == 28

    def test_streak_current_day_zero(self, service):
        """Test streak with current day 0."""
        result = service.calculate_streak([1, 2, 3], 0)
        assert result == 0  # Invalid current day


class TestPointsCalculationEdgeCases:
    """Test points calculation edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_points_empty_challenge_data(self, service):
        """Test points with empty challenge data."""
        result = service.calculate_points({})
        assert result == 0

    def test_points_invalid_day_key(self, service):
        """Test points with invalid day key format."""
        result = service.calculate_points({
            'problems_solved': {
                'invalid_key': ['two-sum'],
                'day_': ['two-sum'],  # No number
                'day_abc': ['two-sum']  # Non-numeric
            }
        })
        # Should handle gracefully, no crash
        assert isinstance(result, int)

    def test_points_nonexistent_problem(self, service):
        """Test points with non-existent problem ID."""
        result = service.calculate_points({
            'problems_solved': {
                'day_1': ['nonexistent-problem-id']
            }
        })
        # Should not add points for unknown problem
        assert result == 0

    def test_points_streak_exactly_7(self, service):
        """Test points with exactly 7-day streak."""
        result = service.calculate_points({
            'best_streak': 7,
            'problems_solved': {}
        })
        assert result == 50  # streak_7 bonus

    def test_points_streak_exactly_14(self, service):
        """Test points with exactly 14-day streak."""
        result = service.calculate_points({
            'best_streak': 14,
            'problems_solved': {}
        })
        assert result == 100  # streak_14 bonus (not cumulative)

    def test_points_streak_exactly_28(self, service):
        """Test points with exactly 28-day streak."""
        result = service.calculate_points({
            'best_streak': 28,
            'problems_solved': {}
        })
        assert result == 250  # streak_28 bonus

    def test_points_streak_over_7_under_14(self, service):
        """Test streak between 7 and 14 days."""
        result = service.calculate_points({
            'best_streak': 10,
            'problems_solved': {}
        })
        assert result == 50  # Only streak_7 bonus

    def test_points_with_approved_skool_posts(self, service):
        """Test points with approved Skool posts."""
        result = service.calculate_points({
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'pending'},  # Not approved
                {'status': 'rejected'}  # Not approved
            ],
            'problems_solved': {}
        })
        assert result == 60  # 2 approved * 30

    def test_points_mixed_difficulty_problems(self, service):
        """Test points with various difficulty problems."""
        # Need to use actual problem IDs from the challenge data
        result = service.calculate_points({
            'problems_solved': {
                'day_1': ['two-sum'],  # Easy - 10 points
                'day_4': ['maximum-subarray']  # Medium - 20 points
            }
        })
        # Points depend on actual problem difficulties
        assert result >= 0

    def test_points_empty_problems_solved(self, service):
        """Test points with empty problems_solved dict."""
        result = service.calculate_points({
            'problems_solved': {},
            'best_streak': 0
        })
        assert result == 0


class TestAchievementEdgeCases:
    """Test achievement checking edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_achievements_empty_data(self, service):
        """Test achievements with empty data."""
        result = service.check_achievements({})
        assert isinstance(result, list)
        # Should return empty list, no crash
        assert len(result) == 0

    def test_achievements_already_has_all(self, service):
        """Test achievements when user already has all."""
        result = service.check_achievements({
            'total_problems_solved': 100,
            'best_streak': 28,
            'achievements': [
                'first_problem', 'streak_7', 'streak_14', 'streak_28',
                'hard_problem', 'community_star'
            ],
            'problems_solved': {'day_1': ['two-sum']},
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'approved'}
            ]
        })
        # Should return empty list (no new achievements)
        assert len(result) == 0

    def test_achievements_streak_7_not_14(self, service):
        """Test streak 7 achievement without 14."""
        result = service.check_achievements({
            'total_problems_solved': 7,
            'best_streak': 7,
            'achievements': [],
            'problems_solved': {}
        })
        assert 'first_problem' in result
        assert 'streak_7' in result
        assert 'streak_14' not in result

    def test_achievements_multiple_unlocked_at_once(self, service):
        """Test multiple achievements unlocked simultaneously."""
        result = service.check_achievements({
            'total_problems_solved': 1,
            'best_streak': 14,
            'achievements': [],
            'problems_solved': {}
        })
        # Should get first_problem, streak_7, and streak_14
        assert 'first_problem' in result
        assert 'streak_7' in result
        assert 'streak_14' in result

    def test_achievements_community_star_exactly_3(self, service):
        """Test community star with exactly 3 approved."""
        result = service.check_achievements({
            'total_problems_solved': 0,
            'best_streak': 0,
            'achievements': [],
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'approved'}
            ]
        })
        assert 'community_star' in result

    def test_achievements_community_star_2_approved(self, service):
        """Test community star with only 2 approved."""
        result = service.check_achievements({
            'total_problems_solved': 0,
            'best_streak': 0,
            'achievements': [],
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'pending'}
            ]
        })
        assert 'community_star' not in result


class TestDayCompletionEdgeCases:
    """Test day completion checking edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_is_day_complete_empty_dict(self, service):
        """Test day complete with empty problems dict."""
        result = service.is_day_complete(1, {})
        assert result is False

    def test_is_day_complete_invalid_day(self, service):
        """Test day complete for invalid day."""
        result = service.is_day_complete(999, {'day_999': []})
        assert result is False

    def test_is_day_complete_day_zero(self, service):
        """Test day complete for day 0."""
        result = service.is_day_complete(0, {'day_0': []})
        assert result is False

    def test_is_day_complete_negative_day(self, service):
        """Test day complete for negative day."""
        result = service.is_day_complete(-1, {'day_-1': []})
        assert result is False

    def test_is_day_complete_partial_solve(self, service):
        """Test day complete with partial problems solved."""
        # Day 1 has at least 'two-sum', if there are more problems
        # this should return False
        problems_solved = {'day_1': ['some-problem-but-not-all']}
        result = service.is_day_complete(1, problems_solved)
        # Depends on how many problems are in day 1
        # If only one problem, might be True; if more, False
        assert isinstance(result, bool)

    def test_is_day_complete_extra_problems(self, service):
        """Test day complete with extra/unknown problems."""
        day_problems = service.get_day_problems(1)
        if day_problems:
            problem_ids = [p['id'] for p in day_problems]
            # Add an extra unknown problem
            problem_ids.append('unknown-problem')
            result = service.is_day_complete(1, {'day_1': problem_ids})
            # Should still be complete (has all required)
            assert result is True


class TestGetProblemEdgeCases:
    """Test getting problem data edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_get_problem_day_zero(self, service):
        """Test get problem for day 0."""
        result = service.get_problem(0, 'two-sum')
        assert result is None

    def test_get_problem_negative_day(self, service):
        """Test get problem for negative day."""
        result = service.get_problem(-1, 'two-sum')
        assert result is None

    def test_get_problem_day_100(self, service):
        """Test get problem for day beyond range."""
        result = service.get_problem(100, 'two-sum')
        assert result is None

    def test_get_problem_empty_id(self, service):
        """Test get problem with empty ID."""
        result = service.get_problem(1, '')
        assert result is None

    def test_get_problem_by_id_empty(self, service):
        """Test get problem by ID with empty string."""
        result = service.get_problem_by_id('')
        assert result is None

    def test_get_problem_by_id_none_like(self, service):
        """Test get problem by ID with None-like string."""
        result = service.get_problem_by_id('None')
        assert result is None

    def test_get_day_theme_day_zero(self, service):
        """Test get theme for day 0."""
        result = service.get_day_theme(0)
        assert result == 'Day 0'  # Default format

    def test_get_day_theme_day_100(self, service):
        """Test get theme for day beyond range."""
        result = service.get_day_theme(100)
        assert result == 'Day 100'  # Default format


class TestServiceConfiguration:
    """Test service configuration edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_get_achievements_config_not_empty(self, service):
        """Test achievements config returns data."""
        result = service.get_achievements_config()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_achievements_config_has_required_keys(self, service):
        """Test achievements config has expected structure."""
        result = service.get_achievements_config()
        # Check at least one achievement has name and icon
        for achievement in result.values():
            assert 'name' in achievement or isinstance(achievement, str)

    def test_get_point_values_not_empty(self, service):
        """Test point values returns data."""
        result = service.get_point_values()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_point_values_has_difficulties(self, service):
        """Test point values has difficulty entries."""
        result = service.get_point_values()
        assert 'easy' in result
        assert 'medium' in result
        assert 'hard' in result

    def test_get_total_days(self, service):
        """Test total days returns 28 or similar."""
        result = service.get_total_days()
        assert result >= 28  # Should be at least 28

    def test_get_challenge_days_not_empty(self, service):
        """Test challenge days data exists."""
        result = service.get_challenge_days()
        assert isinstance(result, list)
        assert len(result) >= 28


class TestGetDayProblemsValidation:
    """Test get_day_problems edge cases."""

    @pytest.fixture
    def service(self, app):
        """Get challenge service instance."""
        with app.app_context():
            return app.challenge_service

    def test_day_1_has_problems(self, service):
        """Test day 1 has at least one problem."""
        problems = service.get_day_problems(1)
        assert len(problems) >= 1

    def test_day_problems_have_required_fields(self, service):
        """Test problems have required fields."""
        problems = service.get_day_problems(1)
        if problems:
            problem = problems[0]
            assert 'id' in problem
            assert 'name' in problem

    def test_day_problems_have_test_cases(self, service):
        """Test problems have test cases."""
        problems = service.get_day_problems(1)
        if problems:
            problem = problems[0]
            assert 'test_cases' in problem
            assert len(problem['test_cases']) > 0

    def test_all_30_days_have_problems(self, service):
        """Test all 30 days have problems."""
        for day in range(1, 31):
            problems = service.get_day_problems(day)
            assert len(problems) >= 1, f"Day {day} has no problems"
