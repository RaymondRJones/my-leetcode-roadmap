"""
Tests for models module.
"""
import pytest
from app.models.course import Course, COURSES, get_sorted_courses


class TestCourse:
    """Tests for Course dataclass."""

    def test_course_creation(self):
        """Test creating a Course instance."""
        course = Course(
            title='Test Course',
            description='A test course',
            route='/test',
            icon='test_icon',
            label='TEST',
            is_premium=False,
            course_type='course-free',
            duration='1 week',
            problem_count='10 problems',
            level='Beginner',
            order=1
        )
        assert course.title == 'Test Course'
        assert course.route == '/test'
        assert course.is_premium is False
        assert course.order == 1

    def test_course_to_dict(self):
        """Test converting Course to dictionary."""
        course = Course(
            title='Test Course',
            description='A test course',
            route='/test',
            icon='test_icon',
            label='TEST',
            is_premium=True,
            course_type='course-premium',
            duration='2 weeks',
            problem_count='20 problems',
            level='Intermediate',
            order=2
        )
        course_dict = course.to_dict()

        assert isinstance(course_dict, dict)
        assert course_dict['title'] == 'Test Course'
        assert course_dict['is_premium'] is True
        assert course_dict['order'] == 2

    def test_course_default_image_url(self):
        """Test that image_url has default value."""
        course = Course(
            title='Test',
            description='Test',
            route='/test',
            icon='icon',
            label='LABEL',
            is_premium=False,
            course_type='course-free',
            duration='1 week',
            problem_count='5',
            level='Beginner',
            order=1
        )
        assert course.image_url == ''


class TestCourses:
    """Tests for COURSES list."""

    def test_courses_not_empty(self):
        """Test that COURSES list is not empty."""
        assert len(COURSES) > 0

    def test_all_courses_are_course_instances(self):
        """Test that all items in COURSES are Course instances."""
        for course in COURSES:
            assert isinstance(course, Course)

    def test_courses_have_unique_orders(self):
        """Test that all courses have unique order values."""
        orders = [course.order for course in COURSES]
        assert len(orders) == len(set(orders)), "Course orders should be unique"

    def test_courses_have_required_fields(self):
        """Test that all courses have required fields populated."""
        for course in COURSES:
            assert course.title, "Course should have a title"
            assert course.description, "Course should have a description"
            assert course.route, "Course should have a route"
            assert course.icon, "Course should have an icon"
            assert course.label, "Course should have a label"
            assert course.duration, "Course should have a duration"
            assert course.level, "Course should have a level"


class TestGetSortedCourses:
    """Tests for get_sorted_courses function."""

    def test_returns_list(self):
        """Test that get_sorted_courses returns a list."""
        courses = get_sorted_courses()
        assert isinstance(courses, list)

    def test_returns_dictionaries(self):
        """Test that get_sorted_courses returns list of dictionaries."""
        courses = get_sorted_courses()
        for course in courses:
            assert isinstance(course, dict)

    def test_sorted_by_order(self):
        """Test that courses are sorted by order."""
        courses = get_sorted_courses()
        orders = [course['order'] for course in courses]
        assert orders == sorted(orders), "Courses should be sorted by order"

    def test_contains_expected_fields(self):
        """Test that course dictionaries contain expected fields."""
        courses = get_sorted_courses()
        expected_fields = ['title', 'description', 'route', 'icon', 'label',
                          'is_premium', 'course_type', 'duration', 'problem_count',
                          'level', 'order']

        for course in courses:
            for field in expected_fields:
                assert field in course, f"Course should have field: {field}"
