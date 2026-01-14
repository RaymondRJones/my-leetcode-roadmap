"""
Unit tests for ChallengeService.

Tests cover:
- Loading challenge data
- Getting problems by day
- Streak calculations
- Points calculations
- Achievement checking
- Day completion checks
"""
import pytest
from datetime import datetime, timedelta
from app.services.challenge_service import ChallengeService


class TestChallengeServiceInit:
    """Test ChallengeService initialization."""

    def test_service_initializes(self):
        """Test that service initializes without error."""
        service = ChallengeService()
        assert service is not None
        assert hasattr(service, 'challenge_data')

    def test_service_loads_challenge_data(self):
        """Test that challenge data is loaded."""
        service = ChallengeService()
        assert 'days' in service.challenge_data
        assert len(service.challenge_data['days']) > 0

    def test_service_has_point_values(self):
        """Test that point values are loaded."""
        service = ChallengeService()
        point_values = service.get_point_values()
        assert 'easy' in point_values
        assert 'medium' in point_values
        assert 'hard' in point_values
        assert point_values['easy'] == 10
        assert point_values['medium'] == 20
        assert point_values['hard'] == 40


class TestGetDayProblems:
    """Test getting problems for a specific day."""

    def test_get_day_1_problems(self):
        """Test getting Day 1 problems."""
        service = ChallengeService()
        problems = service.get_day_problems(1)
        assert len(problems) > 0
        assert problems[0]['id'] == 'two-sum'
        assert problems[0]['difficulty'] == 'Easy'

    def test_get_day_problems_has_test_cases(self):
        """Test that problems have test cases."""
        service = ChallengeService()
        problems = service.get_day_problems(1)
        assert 'test_cases' in problems[0]
        assert len(problems[0]['test_cases']) >= 10

    def test_get_day_problems_invalid_day(self):
        """Test getting problems for invalid day returns empty list."""
        service = ChallengeService()
        problems = service.get_day_problems(99)
        assert problems == []

    def test_get_day_problems_day_zero(self):
        """Test getting problems for day 0 returns empty list."""
        service = ChallengeService()
        problems = service.get_day_problems(0)
        assert problems == []

    def test_get_day_problems_negative_day(self):
        """Test getting problems for negative day returns empty list."""
        service = ChallengeService()
        problems = service.get_day_problems(-1)
        assert problems == []


class TestGetProblem:
    """Test getting specific problems."""

    def test_get_problem_by_day_and_id(self):
        """Test getting a specific problem."""
        service = ChallengeService()
        problem = service.get_problem(1, 'two-sum')
        assert problem is not None
        assert problem['name'] == 'Two Sum'

    def test_get_problem_invalid_id(self):
        """Test getting problem with invalid ID returns None."""
        service = ChallengeService()
        problem = service.get_problem(1, 'invalid-id')
        assert problem is None

    def test_get_problem_invalid_day(self):
        """Test getting problem with invalid day returns None."""
        service = ChallengeService()
        problem = service.get_problem(99, 'two-sum')
        assert problem is None

    def test_get_problem_by_id_only(self):
        """Test finding problem by ID across all days."""
        service = ChallengeService()
        problem = service.get_problem_by_id('two-sum')
        assert problem is not None
        assert problem['name'] == 'Two Sum'

    def test_get_problem_by_id_not_found(self):
        """Test finding non-existent problem returns None."""
        service = ChallengeService()
        problem = service.get_problem_by_id('does-not-exist')
        assert problem is None


class TestGetDayTheme:
    """Test getting day themes."""

    def test_get_day_1_theme(self):
        """Test getting Day 1 theme."""
        service = ChallengeService()
        theme = service.get_day_theme(1)
        assert theme == 'Arrays & Hash Tables'

    def test_get_day_theme_invalid_day(self):
        """Test getting theme for invalid day returns default."""
        service = ChallengeService()
        theme = service.get_day_theme(99)
        assert theme == 'Day 99'


class TestCalculateCurrentDay:
    """Test current day calculations."""

    def test_calculate_current_day_today(self):
        """Test calculation when enrolled today."""
        service = ChallengeService()
        today = datetime.now().isoformat()
        current_day = service.calculate_current_day(today)
        assert current_day == 1

    def test_calculate_current_day_yesterday(self):
        """Test calculation when enrolled yesterday."""
        service = ChallengeService()
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        current_day = service.calculate_current_day(yesterday)
        assert current_day == 2

    def test_calculate_current_day_week_ago(self):
        """Test calculation when enrolled a week ago."""
        service = ChallengeService()
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        current_day = service.calculate_current_day(week_ago)
        assert current_day == 8

    def test_calculate_current_day_caps_at_28(self):
        """Test that current day is capped at 28."""
        service = ChallengeService()
        month_ago = (datetime.now() - timedelta(days=60)).isoformat()
        current_day = service.calculate_current_day(month_ago)
        assert current_day == 28

    def test_calculate_current_day_invalid_date(self):
        """Test with invalid date string returns day 1."""
        service = ChallengeService()
        current_day = service.calculate_current_day('invalid-date')
        assert current_day == 1

    def test_calculate_current_day_future_date(self):
        """Test with future date returns day 1 (minimum)."""
        service = ChallengeService()
        future = (datetime.now() + timedelta(days=5)).isoformat()
        current_day = service.calculate_current_day(future)
        # Future date should result in negative delta, capped at 1
        assert current_day == 1


class TestCalculateStreak:
    """Test streak calculations."""

    def test_calculate_streak_no_days_completed(self):
        """Test streak with no completed days."""
        service = ChallengeService()
        streak = service.calculate_streak([], 1)
        assert streak == 0

    def test_calculate_streak_one_day(self):
        """Test streak with one day completed."""
        service = ChallengeService()
        streak = service.calculate_streak([1], 1)
        assert streak == 1

    def test_calculate_streak_consecutive(self):
        """Test streak with consecutive days."""
        service = ChallengeService()
        streak = service.calculate_streak([1, 2, 3, 4, 5], 5)
        assert streak == 5

    def test_calculate_streak_with_gap(self):
        """Test streak breaks at gap."""
        service = ChallengeService()
        # Completed days 1, 2, 4, 5 (gap at 3), current day is 5
        streak = service.calculate_streak([1, 2, 4, 5], 5)
        assert streak == 2  # Only 4 and 5 are consecutive from current

    def test_calculate_streak_current_day_not_completed(self):
        """Test streak when current day is not completed."""
        service = ChallengeService()
        # Completed 1, 2, 3 but current day is 4 (not completed)
        streak = service.calculate_streak([1, 2, 3], 4)
        assert streak == 0  # Day 4 not in list, so streak is 0

    def test_calculate_streak_only_past_days(self):
        """Test streak with only past days completed."""
        service = ChallengeService()
        # Completed 1, 2, 3, current is 5 (day 4 missing)
        streak = service.calculate_streak([1, 2, 3], 5)
        assert streak == 0  # Gap at day 4

    def test_calculate_streak_full_28_days(self):
        """Test streak with all 28 days completed."""
        service = ChallengeService()
        all_days = list(range(1, 29))
        streak = service.calculate_streak(all_days, 28)
        assert streak == 28


class TestCalculatePoints:
    """Test points calculations."""

    def test_calculate_points_no_problems(self):
        """Test points with no problems solved."""
        service = ChallengeService()
        challenge_data = {'problems_solved': {}}
        points = service.calculate_points(challenge_data)
        assert points == 0

    def test_calculate_points_easy_problem(self):
        """Test points for easy problem."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {'day_1': ['two-sum']},
            'best_streak': 0
        }
        points = service.calculate_points(challenge_data)
        assert points == 10

    def test_calculate_points_medium_problem(self):
        """Test points for medium problem."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {'day_6': ['maximum-subarray']},
            'best_streak': 0
        }
        points = service.calculate_points(challenge_data)
        assert points == 20

    def test_calculate_points_multiple_problems(self):
        """Test points for multiple problems."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {
                'day_1': ['two-sum'],
                'day_2': ['valid-parentheses']
            },
            'best_streak': 0
        }
        points = service.calculate_points(challenge_data)
        assert points == 20  # 10 + 10

    def test_calculate_points_with_7_day_streak(self):
        """Test points with 7-day streak bonus."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {'day_1': ['two-sum']},
            'best_streak': 7
        }
        points = service.calculate_points(challenge_data)
        assert points == 60  # 10 + 50 streak bonus

    def test_calculate_points_with_14_day_streak(self):
        """Test points with 14-day streak bonus."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {},
            'best_streak': 14
        }
        points = service.calculate_points(challenge_data)
        assert points == 100  # Only streak bonus

    def test_calculate_points_with_28_day_streak(self):
        """Test points with 28-day streak bonus."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {},
            'best_streak': 28
        }
        points = service.calculate_points(challenge_data)
        assert points == 250  # Only streak bonus

    def test_calculate_points_with_approved_skool_posts(self):
        """Test points with approved Skool posts."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {},
            'best_streak': 0,
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'pending'}
            ]
        }
        points = service.calculate_points(challenge_data)
        assert points == 60  # 2 approved * 30

    def test_calculate_points_complex_scenario(self):
        """Test points with multiple factors."""
        service = ChallengeService()
        challenge_data = {
            'problems_solved': {
                'day_1': ['two-sum'],  # 10 pts
                'day_6': ['maximum-subarray']  # 20 pts
            },
            'best_streak': 7,  # 50 pts
            'skool_submissions': [{'status': 'approved'}]  # 30 pts
        }
        points = service.calculate_points(challenge_data)
        assert points == 110  # 10 + 20 + 50 + 30


class TestCheckAchievements:
    """Test achievement checking."""

    def test_check_achievements_empty(self):
        """Test no achievements with no progress."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 0,
            'achievements': []
        }
        new_achievements = service.check_achievements(challenge_data)
        assert new_achievements == []

    def test_check_achievements_first_problem(self):
        """Test first problem achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 1,
            'best_streak': 0,
            'achievements': []
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'first_problem' in new_achievements

    def test_check_achievements_already_has_first_problem(self):
        """Test no duplicate first problem achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 5,
            'best_streak': 0,
            'achievements': ['first_problem']
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'first_problem' not in new_achievements

    def test_check_achievements_streak_7(self):
        """Test 7-day streak achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 7,
            'achievements': []
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'streak_7' in new_achievements

    def test_check_achievements_streak_14(self):
        """Test 14-day streak achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 14,
            'achievements': []
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'streak_14' in new_achievements
        assert 'streak_7' in new_achievements  # Should also unlock 7

    def test_check_achievements_streak_28(self):
        """Test 28-day streak achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 28,
            'achievements': []
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'streak_28' in new_achievements
        assert 'streak_14' in new_achievements
        assert 'streak_7' in new_achievements

    def test_check_achievements_community_star(self):
        """Test community star achievement."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 0,
            'achievements': [],
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'approved'}
            ]
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'community_star' in new_achievements

    def test_check_achievements_community_star_not_enough(self):
        """Test community star not unlocked with less than 3 approved."""
        service = ChallengeService()
        challenge_data = {
            'total_problems_solved': 0,
            'best_streak': 0,
            'achievements': [],
            'skool_submissions': [
                {'status': 'approved'},
                {'status': 'approved'},
                {'status': 'pending'}
            ]
        }
        new_achievements = service.check_achievements(challenge_data)
        assert 'community_star' not in new_achievements


class TestIsDayComplete:
    """Test day completion checking."""

    def test_is_day_complete_no_problems_solved(self):
        """Test day not complete with no problems solved."""
        service = ChallengeService()
        is_complete = service.is_day_complete(1, {})
        assert is_complete is False

    def test_is_day_complete_partial(self):
        """Test day not complete with partial problems solved."""
        service = ChallengeService()
        # Day 1 has 1 problem (two-sum)
        is_complete = service.is_day_complete(1, {'day_1': []})
        assert is_complete is False

    def test_is_day_complete_all_solved(self):
        """Test day complete with all problems solved."""
        service = ChallengeService()
        # Day 1 has two-sum
        is_complete = service.is_day_complete(1, {'day_1': ['two-sum']})
        assert is_complete is True

    def test_is_day_complete_invalid_day(self):
        """Test day complete check for invalid day."""
        service = ChallengeService()
        is_complete = service.is_day_complete(99, {'day_99': ['some-problem']})
        assert is_complete is False


class TestGetAchievementsConfig:
    """Test achievements configuration."""

    def test_get_achievements_config(self):
        """Test getting achievements config."""
        service = ChallengeService()
        config = service.get_achievements_config()
        assert 'first_problem' in config
        assert 'streak_7' in config
        assert 'streak_14' in config
        assert 'streak_28' in config
        assert 'hard_problem' in config
        assert 'community_star' in config

    def test_achievements_have_name_and_icon(self):
        """Test that each achievement has name and icon."""
        service = ChallengeService()
        config = service.get_achievements_config()
        for achievement_id, achievement in config.items():
            assert 'name' in achievement
            assert 'icon' in achievement


class TestGetTotalDays:
    """Test total days configuration."""

    def test_get_total_days(self):
        """Test getting total days."""
        service = ChallengeService()
        total_days = service.get_total_days()
        assert total_days == 30  # Updated to 30 days


class TestGetChallengeDays:
    """Test getting all challenge days."""

    def test_get_challenge_days(self):
        """Test getting all challenge days."""
        service = ChallengeService()
        days = service.get_challenge_days()
        assert len(days) == 30  # Should have 30 days
        assert days[0]['day'] == 1
        assert days[-1]['day'] == 30
