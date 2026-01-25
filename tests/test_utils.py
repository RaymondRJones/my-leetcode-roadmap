"""
Tests for utils module.
"""
import pytest
from app.utils.problem_utils import estimate_difficulty_and_topics, generate_leetcode_url


class TestEstimateDifficultyAndTopics:
    """Tests for estimate_difficulty_and_topics function."""

    def test_returns_tuple_of_three(self):
        """Test that function returns tuple with 3 elements."""
        result = estimate_difficulty_and_topics("Two Sum")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_difficulty_string(self):
        """Test that difficulty is a string."""
        difficulty, _, _ = estimate_difficulty_and_topics("Random Problem")
        assert isinstance(difficulty, str)
        assert difficulty in ['Easy', 'Medium', 'Hard']

    def test_returns_topics_list(self):
        """Test that topics is a list."""
        _, topics, _ = estimate_difficulty_and_topics("Random Problem")
        assert isinstance(topics, list)
        assert len(topics) > 0

    def test_returns_time_integer(self):
        """Test that time is an integer."""
        _, _, time = estimate_difficulty_and_topics("Random Problem")
        assert isinstance(time, int)
        assert time > 0

    def test_easy_problem_detection(self):
        """Test that easy problems are detected correctly."""
        difficulty, _, _ = estimate_difficulty_and_topics("Two Sum")
        assert difficulty == 'Easy'

        difficulty, _, _ = estimate_difficulty_and_topics("Valid Palindrome")
        assert difficulty == 'Easy'

    def test_hard_problem_detection(self):
        """Test that hard problems are detected correctly."""
        difficulty, _, _ = estimate_difficulty_and_topics("Median of Two Sorted Arrays")
        assert difficulty == 'Hard'

        difficulty, _, _ = estimate_difficulty_and_topics("Minimum Window Substring")
        assert difficulty == 'Hard'

    def test_array_topic_detection(self):
        """Test that array problems are detected correctly."""
        _, topics, _ = estimate_difficulty_and_topics("Maximum Subarray")
        assert 'Array' in topics

    def test_string_topic_detection(self):
        """Test that string problems are detected correctly."""
        _, topics, _ = estimate_difficulty_and_topics("Valid Palindrome")
        assert 'String' in topics

    def test_tree_topic_detection(self):
        """Test that tree problems are detected correctly."""
        _, topics, _ = estimate_difficulty_and_topics("Binary Tree Inorder Traversal")
        assert 'Binary Tree' in topics

    def test_graph_topic_detection(self):
        """Test that graph problems are detected correctly."""
        _, topics, _ = estimate_difficulty_and_topics("Number of Islands")
        assert 'Graph' in topics

    def test_dp_topic_detection(self):
        """Test that dynamic programming problems are detected correctly."""
        _, topics, _ = estimate_difficulty_and_topics("Climbing Stairs Dynamic Programming")
        assert 'Dynamic Programming' in topics

    def test_default_topic_when_no_match(self):
        """Test that Algorithm is default when no topic matches."""
        # Use a name that won't match any pattern keywords
        _, topics, _ = estimate_difficulty_and_topics("Puzzle Challenge")
        assert 'Algorithm' in topics

    def test_time_estimates_by_difficulty(self):
        """Test that time estimates match difficulty."""
        _, _, easy_time = estimate_difficulty_and_topics("Two Sum")
        assert easy_time == 20

        _, _, hard_time = estimate_difficulty_and_topics("Median of Two Sorted Arrays")
        assert hard_time == 45


class TestGenerateLeetcodeUrl:
    """Tests for generate_leetcode_url function."""

    def test_basic_url_generation(self):
        """Test basic URL generation."""
        url = generate_leetcode_url("Two Sum")
        assert url == "https://leetcode.com/problems/two-sum/"

    def test_lowercase_conversion(self):
        """Test that problem names are lowercased."""
        url = generate_leetcode_url("VALID PALINDROME")
        assert "valid-palindrome" in url

    def test_special_chars_removed(self):
        """Test that special characters are removed."""
        url = generate_leetcode_url("Problem's Name!")
        assert "'" not in url
        assert "!" not in url

    def test_spaces_replaced_with_hyphens(self):
        """Test that spaces are replaced with hyphens."""
        url = generate_leetcode_url("Maximum Subarray Sum")
        assert "maximum-subarray-sum" in url

    def test_multiple_hyphens_collapsed(self):
        """Test that multiple hyphens are collapsed."""
        url = generate_leetcode_url("Test   Problem")
        assert "---" not in url

    def test_url_format(self):
        """Test that URL has correct format."""
        url = generate_leetcode_url("Any Problem")
        assert url.startswith("https://leetcode.com/problems/")
        assert url.endswith("/")

    def test_no_leading_trailing_hyphens(self):
        """Test that URL doesn't have leading/trailing hyphens."""
        url = generate_leetcode_url(" Problem Name ")
        slug = url.replace("https://leetcode.com/problems/", "").rstrip("/")
        assert not slug.startswith("-")
        assert not slug.endswith("-")
