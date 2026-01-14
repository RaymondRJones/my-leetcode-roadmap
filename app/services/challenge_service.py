"""
Challenge service for 28-day LeetCode challenge.

Handles challenge data loading, progress calculations, streak tracking,
points calculation, and achievement checking.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ChallengeService:
    """Service class for 28-day challenge operations."""

    def __init__(self):
        """Initialize the challenge service."""
        self.challenge_data: Dict = {}
        self._load_challenge_data()

    def _load_challenge_data(self) -> None:
        """Load challenge problems from JSON file."""
        # Try multiple paths to find the JSON file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '../../challenge_problems.json'),
            'challenge_problems.json',
            os.path.join(os.path.dirname(__file__), '../../../challenge_problems.json'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.challenge_data = json.load(f)
                return

        # Default empty structure if file not found
        self.challenge_data = {'days': [], 'achievements': {}, 'point_values': {}}

    def get_challenge_days(self) -> List[Dict]:
        """Get all challenge days data."""
        return self.challenge_data.get('days', [])

    def get_day_problems(self, day: int) -> List[Dict]:
        """Get problems for a specific day."""
        for d in self.challenge_data.get('days', []):
            if d['day'] == day:
                return d.get('problems', [])
        return []

    def get_day_theme(self, day: int) -> str:
        """Get the theme for a specific day."""
        for d in self.challenge_data.get('days', []):
            if d['day'] == day:
                return d.get('theme', f'Day {day}')
        return f'Day {day}'

    def get_problem(self, day: int, problem_id: str) -> Optional[Dict]:
        """Get a specific problem by day and ID."""
        problems = self.get_day_problems(day)
        for p in problems:
            if p['id'] == problem_id:
                return p
        return None

    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """Find a problem by ID across all days."""
        for day in self.challenge_data.get('days', []):
            for problem in day.get('problems', []):
                if problem.get('id') == problem_id:
                    return problem
        return None

    def calculate_current_day(self, start_date: str) -> int:
        """Calculate which day of the challenge the user is on.

        Args:
            start_date: ISO format date string of when user enrolled

        Returns:
            Current challenge day (1-28)
        """
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            # Use date only to avoid timezone issues
            start_day = start.date()
            today = datetime.now().date()
            delta = (today - start_day).days + 1
            return min(max(delta, 1), 28)
        except (ValueError, AttributeError):
            return 1

    def calculate_streak(self, days_completed: List[int], current_day: int) -> int:
        """Calculate the current consecutive day streak.

        Args:
            days_completed: List of completed day numbers
            current_day: The current challenge day

        Returns:
            Current streak count
        """
        if not days_completed:
            return 0

        streak = 0
        # Count backwards from current day
        for day in range(current_day, 0, -1):
            if day in days_completed:
                streak += 1
            else:
                break
        return streak

    def calculate_points(self, challenge_data: Dict) -> int:
        """Calculate total points from completed problems and achievements.

        Args:
            challenge_data: User's challenge data from Clerk metadata

        Returns:
            Total points earned
        """
        points = 0
        point_values = self.challenge_data.get('point_values', {
            'easy': 10,
            'medium': 20,
            'hard': 40,
            'streak_7': 50,
            'streak_14': 100,
            'streak_28': 250
        })

        # Points from problems solved
        problems_solved = challenge_data.get('problems_solved', {})
        for day_key, problem_ids in problems_solved.items():
            try:
                day_num = int(day_key.split('_')[1])
            except (IndexError, ValueError):
                continue

            for pid in problem_ids:
                problem = self.get_problem(day_num, pid)
                if problem:
                    difficulty = problem.get('difficulty', 'Easy').lower()
                    points += point_values.get(difficulty, 10)

        # Points from streak bonuses (only best streak counts)
        best_streak = challenge_data.get('best_streak', 0)
        if best_streak >= 28:
            points += point_values.get('streak_28', 250)
        elif best_streak >= 14:
            points += point_values.get('streak_14', 100)
        elif best_streak >= 7:
            points += point_values.get('streak_7', 50)

        # Points from approved Skool submissions
        skool_submissions = challenge_data.get('skool_submissions', [])
        approved_count = sum(1 for s in skool_submissions if s.get('status') == 'approved')
        points += approved_count * point_values.get('skool_post_approved', 30)

        return points

    def check_achievements(self, challenge_data: Dict) -> List[str]:
        """Check and return newly unlocked achievements.

        Args:
            challenge_data: User's challenge data from Clerk metadata

        Returns:
            List of newly unlocked achievement IDs
        """
        current_achievements = set(challenge_data.get('achievements', []))
        new_achievements = []

        # First problem achievement
        if challenge_data.get('total_problems_solved', 0) >= 1:
            if 'first_problem' not in current_achievements:
                new_achievements.append('first_problem')

        # Streak achievements
        best_streak = challenge_data.get('best_streak', 0)
        if best_streak >= 7 and 'streak_7' not in current_achievements:
            new_achievements.append('streak_7')
        if best_streak >= 14 and 'streak_14' not in current_achievements:
            new_achievements.append('streak_14')
        if best_streak >= 28 and 'streak_28' not in current_achievements:
            new_achievements.append('streak_28')

        # Hard problem achievement
        problems_solved = challenge_data.get('problems_solved', {})
        for day_problems in problems_solved.values():
            for pid in day_problems:
                problem = self.get_problem_by_id(pid)
                if problem and problem.get('difficulty') == 'Hard':
                    if 'hard_problem' not in current_achievements:
                        new_achievements.append('hard_problem')
                        break
            if 'hard_problem' in new_achievements:
                break

        # Community star achievement (3 approved Skool posts)
        skool_submissions = challenge_data.get('skool_submissions', [])
        approved_count = sum(1 for s in skool_submissions if s.get('status') == 'approved')
        if approved_count >= 3 and 'community_star' not in current_achievements:
            new_achievements.append('community_star')

        return new_achievements

    def get_achievements_config(self) -> Dict:
        """Get achievement definitions."""
        return self.challenge_data.get('achievements', {
            'first_problem': {'name': 'First Steps', 'icon': 'school'},
            'streak_7': {'name': 'Week Warrior', 'icon': 'local_fire_department'},
            'streak_14': {'name': 'Fortnight Focus', 'icon': 'whatshot'},
            'streak_28': {'name': 'Challenge Champion', 'icon': 'emoji_events'},
            'hard_problem': {'name': 'Hard Mode', 'icon': 'psychology'},
            'community_star': {'name': 'Community Star', 'icon': 'groups'}
        })

    def get_point_values(self) -> Dict:
        """Get point value configuration."""
        return self.challenge_data.get('point_values', {
            'easy': 10,
            'medium': 20,
            'hard': 40,
            'streak_7': 50,
            'streak_14': 100,
            'streak_28': 250,
            'skool_post_approved': 30
        })

    def get_total_days(self) -> int:
        """Get the total number of days in the challenge."""
        return self.challenge_data.get('total_days', 28)

    def is_day_complete(self, day: int, problems_solved: Dict) -> bool:
        """Check if all problems for a day have been completed.

        Args:
            day: The day number to check
            problems_solved: Dict mapping day_N to list of problem IDs

        Returns:
            True if all problems for the day are solved
        """
        day_key = f'day_{day}'
        solved_ids = problems_solved.get(day_key, [])
        day_problems = self.get_day_problems(day)

        if not day_problems:
            return False

        day_problem_ids = [p['id'] for p in day_problems]
        return all(pid in solved_ids for pid in day_problem_ids)
