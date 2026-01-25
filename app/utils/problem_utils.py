"""
Utility functions for problem processing.
"""
import re
from typing import Tuple, List


def estimate_difficulty_and_topics(problem_name: str) -> Tuple[str, List[str], int]:
    """
    Estimate difficulty and topics based on problem name.

    Args:
        problem_name: The name of the problem

    Returns:
        Tuple of (difficulty, topics, estimated_time_minutes)
    """
    name_lower = problem_name.lower()

    # Difficulty estimation based on common patterns
    difficulty = 'Medium'
    if any(keyword in name_lower for keyword in ['two sum', 'valid', 'merge', 'reverse', 'palindrome', 'anagram', 'binary search']):
        difficulty = 'Easy'
    elif any(keyword in name_lower for keyword in ['median', 'serialize', 'sliding window', 'minimum window', 'trapping', 'word ladder']):
        difficulty = 'Hard'

    # Topic estimation based on problem name patterns
    topics = []

    topic_patterns = {
        'Array': ['array', 'sum', 'product', 'subarray', 'rotate'],
        'String': ['string', 'palindrome', 'anagram', 'word', 'character'],
        'Binary Tree': ['tree', 'binary tree', 'bst', 'node'],
        'Linked List': ['linked list', 'list cycle', 'merge'],
        'Graph': ['graph', 'dfs', 'bfs', 'island', 'clone'],
        'Dynamic Programming': ['dynamic programming', 'dp', 'coin', 'climb', 'house robber'],
        'Binary Search': ['binary search', 'search', 'find'],
        'Stack': ['stack', 'queue', 'parentheses', 'calculator'],
        'Heap': ['heap', 'priority', 'kth', 'median'],
        'Hash Table': ['hash', 'map', 'set'],
        'Sorting': ['sort', 'merge'],
        'Matrix': ['matrix', 'grid', '2d'],
        'Backtracking': ['backtrack', 'permutation', 'combination'],
        'Trie': ['trie', 'prefix'],
        'Bit Manipulation': ['bit', 'xor', 'and', 'or'],
    }

    for topic, keywords in topic_patterns.items():
        if any(keyword in name_lower for keyword in keywords):
            topics.append(topic)

    # Default topics if none detected
    if not topics:
        topics = ['Algorithm']

    # Time estimation based on difficulty
    time_estimates = {'Easy': 20, 'Medium': 30, 'Hard': 45}
    time = time_estimates.get(difficulty, 30)

    return difficulty, topics, time


def generate_leetcode_url(problem_name: str) -> str:
    """
    Generate LeetCode URL from problem name.

    Args:
        problem_name: The name of the problem

    Returns:
        The LeetCode URL for the problem
    """
    # Convert problem name to URL format
    # Example: "Two Sum" -> "two-sum"
    url_slug = problem_name.lower()
    url_slug = re.sub(r'[^\w\s-]', '', url_slug)  # Remove special chars
    url_slug = re.sub(r'[-\s]+', '-', url_slug)   # Replace spaces/hyphens with single hyphen
    url_slug = url_slug.strip('-')                # Remove leading/trailing hyphens

    return f"https://leetcode.com/problems/{url_slug}/"
