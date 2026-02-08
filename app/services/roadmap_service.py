"""
Roadmap service for loading and processing roadmap data.
"""
import json
import os
from typing import Dict, List, Any

from pdf_analyzer import LeetCodeRoadmapAnalyzer
from ..utils.problem_utils import estimate_difficulty_and_topics


class RoadmapService:
    """Service class for roadmap data operations."""

    def __init__(self, month_order: List[str], month_mapping: Dict[str, str],
                 intermediate_month_order: List[str]):
        """Initialize the roadmap service."""
        self.roadmap_data: Dict = {}
        self.intermediate_roadmap_data: Dict = {}
        self.atcoder_problems: Dict = {}
        self.month_order = month_order
        self.month_mapping = month_mapping
        self.intermediate_month_order = intermediate_month_order
        self._load_all_data()

    def _load_all_data(self):
        """Load all data from JSON files."""
        self._load_roadmap_data()
        self._load_intermediate_roadmap_data()
        self._load_atcoder_problems()

    def _load_roadmap_data(self):
        """Load roadmap data from JSON file."""
        if os.path.exists('roadmap_data.json'):
            with open('roadmap_data.json', 'r', encoding='utf-8') as f:
                self.roadmap_data = json.load(f)
        else:
            print("No roadmap data found. Run pdf_analyzer.py first.")

    def _load_intermediate_roadmap_data(self):
        """Load intermediate roadmap data from JSON file."""
        if os.path.exists('intermediate_roadmap_data_v2.json'):
            with open('intermediate_roadmap_data_v2.json', 'r', encoding='utf-8') as f:
                self.intermediate_roadmap_data = json.load(f)
        else:
            print("No intermediate roadmap data found. Run pdf analyzer for intermediate PDFs first.")

    def _load_atcoder_problems(self):
        """Load AtCoder beginner problems from JSON file."""
        if os.path.exists('atcoder_beginner_problems.json'):
            with open('atcoder_beginner_problems.json', 'r', encoding='utf-8') as f:
                self.atcoder_problems = json.load(f)
        else:
            print("No AtCoder problems found. Run scripts/atcoder_scraper.py first.")

    def _process_month_data(self, month_data: List[Dict]) -> List[Dict]:
        """Process month data to separate bonus problems."""
        processed_month = []
        bonus_problems = []

        for day in month_data:
            if day['day'] == 30:
                # Day 30 problems become bonus problems
                bonus_problems.extend(day['problems'])
            else:
                # Regular days - limit to 3 problems, rest go to bonus
                regular_problems = day['problems'][:3]
                if len(day['problems']) > 3:
                    bonus_problems.extend(day['problems'][3:])

                processed_month.append({
                    'day': day['day'],
                    'problems': regular_problems
                })

        # Add bonus section if there are bonus problems
        if bonus_problems:
            processed_month.append({
                'day': 'bonus',
                'problems': bonus_problems
            })

        return processed_month

    def get_ordered_roadmap_data(self) -> Dict:
        """Get roadmap data ordered properly and with renamed months."""
        ordered_data = {}
        for original_month in self.month_order:
            if original_month in self.roadmap_data:
                display_month = self.month_mapping.get(original_month, original_month)
                month_data = self.roadmap_data[original_month].copy()
                ordered_data[display_month] = self._process_month_data(month_data)
        return ordered_data

    def get_ordered_intermediate_roadmap_data(self) -> Dict:
        """Get intermediate roadmap data ordered properly."""
        ordered_data = {}
        for month in self.intermediate_month_order:
            if month in self.intermediate_roadmap_data:
                month_data = self.intermediate_roadmap_data[month].copy()
                ordered_data[month] = self._process_month_data(month_data)
        return ordered_data

    def get_original_month_name(self, display_month: str) -> str:
        """Get original month name from display name."""
        for original, display in self.month_mapping.items():
            if display == display_month:
                return original
        return display_month

    def get_month_data(self, original_month: str) -> List[Dict]:
        """Get data for a specific month."""
        return self.roadmap_data.get(original_month, [])

    def get_atcoder_problems(self) -> Dict:
        """Get AtCoder problems data."""
        return self.atcoder_problems

    def get_all_problems(self) -> List[Dict]:
        """Get all problems from all sources for the complete list."""
        all_questions = []
        seen_urls = set()

        # Add questions from regular roadmap
        for month_name, month_data in self.roadmap_data.items():
            for day_data in month_data:
                for problem in day_data.get('problems', []):
                    url = problem.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        problem_name = problem.get('name', 'Unknown Problem')
                        difficulty, topics, time = estimate_difficulty_and_topics(problem_name)

                        all_questions.append({
                            'id': len(all_questions) + 1,
                            'title': problem_name,
                            'url': url,
                            'difficulty': difficulty,
                            'time': time,
                            'topics': topics,
                            'source': f'advanced-{month_name}'
                        })

        # Add questions from intermediate roadmap
        for month_name, month_data in self.intermediate_roadmap_data.items():
            for day_data in month_data:
                for problem in day_data.get('problems', []):
                    url = problem.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        problem_name = problem.get('name', 'Unknown Problem')
                        difficulty, topics, time = estimate_difficulty_and_topics(problem_name)

                        all_questions.append({
                            'id': len(all_questions) + 1,
                            'title': problem_name,
                            'url': url,
                            'difficulty': difficulty,
                            'time': time,
                            'topics': topics,
                            'source': f'intermediate-{month_name}'
                        })

        # Add questions from AtCoder beginner problems
        for problem in self.atcoder_problems.get('problems', []):
            url = problem.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                problem_name = problem.get('title', 'Unknown Problem')

                all_questions.append({
                    'id': len(all_questions) + 1,
                    'title': problem_name,
                    'url': url,
                    'difficulty': 'Easy',
                    'time': 15,
                    'topics': ['Algorithm', 'Implementation'],
                    'source': 'atcoder-beginner'
                })

        # Add additional popular LeetCode problems
        all_questions.extend(self._get_additional_problems(seen_urls, len(all_questions)))

        return all_questions

    def _get_additional_problems(self, seen_urls: set, start_id: int) -> List[Dict]:
        """Get additional popular LeetCode problems."""
        additional_problems = [
            {'title': 'Two Sum', 'url': 'https://leetcode.com/problems/two-sum/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Hash Table']},
            {'title': 'Add Two Numbers', 'url': 'https://leetcode.com/problems/add-two-numbers/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Linked List', 'Math']},
            {'title': 'Longest Substring Without Repeating Characters', 'url': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/', 'difficulty': 'Medium', 'time': 30, 'topics': ['String', 'Sliding Window']},
            {'title': 'Median of Two Sorted Arrays', 'url': 'https://leetcode.com/problems/median-of-two-sorted-arrays/', 'difficulty': 'Hard', 'time': 45, 'topics': ['Array', 'Binary Search']},
            {'title': 'Valid Parentheses', 'url': 'https://leetcode.com/problems/valid-parentheses/', 'difficulty': 'Easy', 'time': 20, 'topics': ['String', 'Stack']},
            {'title': 'Merge Two Sorted Lists', 'url': 'https://leetcode.com/problems/merge-two-sorted-lists/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Linked List', 'Recursion']},
            {'title': 'Remove Duplicates from Sorted Array', 'url': 'https://leetcode.com/problems/remove-duplicates-from-sorted-array/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Two Pointers']},
            {'title': 'Best Time to Buy and Sell Stock', 'url': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
            {'title': 'Valid Palindrome', 'url': 'https://leetcode.com/problems/valid-palindrome/', 'difficulty': 'Easy', 'time': 15, 'topics': ['String', 'Two Pointers']},
            {'title': 'Invert Binary Tree', 'url': 'https://leetcode.com/problems/invert-binary-tree/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Binary Tree', 'DFS']},
            {'title': 'Maximum Subarray', 'url': 'https://leetcode.com/problems/maximum-subarray/', 'difficulty': 'Medium', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
            {'title': 'Climbing Stairs', 'url': 'https://leetcode.com/problems/climbing-stairs/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Math', 'Dynamic Programming']},
            {'title': 'Binary Search', 'url': 'https://leetcode.com/problems/binary-search/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Binary Search']},
            {'title': 'Flood Fill', 'url': 'https://leetcode.com/problems/flood-fill/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'DFS', 'BFS']},
            {'title': 'Number of Islands', 'url': 'https://leetcode.com/problems/number-of-islands/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Array', 'DFS', 'BFS']},
        ]

        result = []
        current_id = start_id
        for problem in additional_problems:
            if problem['url'] not in seen_urls:
                seen_urls.add(problem['url'])
                current_id += 1
                result.append({
                    'id': current_id,
                    'title': problem['title'],
                    'url': problem['url'],
                    'difficulty': problem['difficulty'],
                    'time': problem['time'],
                    'topics': problem['topics'],
                    'source': 'popular'
                })

        return result

    def refresh_data(self):
        """Refresh data by re-analyzing PDFs. Refuses to overwrite with empty data."""
        analyzer = LeetCodeRoadmapAnalyzer()

        # Regular roadmap
        monthly_problems = analyzer.analyze_all_pdfs()
        if not monthly_problems:
            raise ValueError("PDF analysis produced no roadmap data. Aborting to prevent overwriting existing data.")
        roadmap = analyzer.create_daily_roadmap(monthly_problems)
        analyzer.save_roadmap_json(roadmap)

        # Intermediate roadmap
        intermediate_problems = analyzer.analyze_intermediate_pdfs()
        if not intermediate_problems:
            raise ValueError("PDF analysis produced no intermediate data. Aborting to prevent overwriting existing data.")
        intermediate_roadmap = analyzer.create_daily_roadmap(intermediate_problems)
        analyzer.save_intermediate_roadmap_json(intermediate_roadmap)

        self._load_all_data()
