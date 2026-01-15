"""
Course model and data definitions.
"""
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Course:
    """Represents a course/learning path in the application."""
    title: str
    description: str
    route: str
    icon: str
    label: str
    is_premium: bool
    course_type: str
    duration: str
    problem_count: str
    level: str
    order: int
    image_url: str = ''

    def to_dict(self) -> dict:
        """Convert course to dictionary for template rendering."""
        return asdict(self)


# All course definitions
COURSES: List[Course] = [
    Course(
        title='Complete Beginner Roadmap',
        description='Master programming fundamentals with 200+ beginner-friendly problems. Perfect for absolute beginners starting from zero.',
        route='/beginner',
        icon='school',
        label='LEVEL 1',
        image_url='/static/images/course-beginner.jpg',
        is_premium=False,
        course_type='course-free',
        duration='4-8 weeks',
        problem_count='50 problems',
        level='Beginner',
        order=1
    ),
    Course(
        title='Fortune500 Roadmap',
        description='Intermediate preparation for mid-tier companies. Month 1 is free, complete all 3 months to master mid-level interviews.',
        route='/intermediate',
        icon='rocket_launch',
        label='LEVEL 2',
        image_url='/static/images/course-intermediate.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='3 months',
        problem_count='80 problems',
        level='Intermediate',
        order=2
    ),
    Course(
        title='The Software Engineering Journey',
        description="Follow Raymond's complete path from bootcamp to Fortune 1 software engineer. Learn the strategies that work in 2025.",
        route='/roadmap',
        icon='trending_up',
        label='CAREER GUIDE',
        image_url='/static/images/course-journey.jpg',
        is_premium=False,
        course_type='course-free',
        duration='6-18 months',
        problem_count='Career guide',
        level='All Levels',
        order=3
    ),
    Course(
        title='FAANG+ Roadmap',
        description="Raymond's exact path to top 2% on LeetCode. Advanced problems for FAANG and top-tier company preparation.",
        route='/advanced',
        icon='star',
        label='LEVEL 3',
        image_url='/static/images/course-advanced.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='6+ months',
        problem_count='790+ problems',
        level='Advanced',
        order=4
    ),
    Course(
        title='Ray700 Complete List',
        description='Custom study plan generator with 700+ curated problems. Filter by difficulty, topics, and create your personalized roadmap.',
        route='/complete-list',
        icon='tune',
        label='MASTER COLLECTION',
        image_url='/static/images/course-ray700.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='Flexible',
        problem_count='700+ problems',
        level='All Levels',
        order=5
    ),
    Course(
        title='Resume + LinkedIn Guide',
        description='My exact resume and LinkedIn profile that landed me offers at Fortune 1 companies. Step-by-step templates and strategies.',
        route='/guides',
        icon='description',
        label='CAREER DOCS',
        image_url='/static/images/course-resume.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='2-4 hours',
        problem_count='Templates',
        level='All Levels',
        order=6
    ),
    Course(
        title='System Design Guide',
        description='Master system design interviews with real-world examples, architecture patterns, and scalability principles.',
        route='/guides',
        icon='account_tree',
        label='ARCHITECTURE',
        image_url='/static/images/course-system-design.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='4-8 weeks',
        problem_count='Design patterns',
        level='Advanced',
        order=7
    ),
    Course(
        title='28-Day LeetCode Challenge',
        description='Transform your coding skills in 28 days. Solve curated problems, track progress, earn achievements, and compete on the leaderboard.',
        route='/challenge',
        icon='emoji_events',
        label='CHALLENGE',
        image_url='/static/images/course-challenge.jpg',
        is_premium=False,
        course_type='course-free',
        duration='28 days',
        problem_count='28 problems',
        level='All Levels',
        order=8
    ),
    Course(
        title='Python Assessment',
        description='Test your Python knowledge with 20 multiple-choice questions. Evaluate your skills in syntax, data structures, and OOP concepts.',
        route='/python-assessment',
        icon='quiz',
        label='PYTHON TEST',
        image_url='/static/images/course-python.jpg',
        is_premium=False,
        course_type='course-free',
        duration='15-20 min',
        problem_count='20 questions',
        level='All Levels',
        order=9
    ),
    Course(
        title='Java Assessment',
        description='Evaluate your Java proficiency with 20 multiple-choice questions covering fundamentals, OOP, collections, and best practices.',
        route='/java-assessment',
        icon='quiz',
        label='JAVA TEST',
        image_url='/static/images/course-java.jpg',
        is_premium=False,
        course_type='course-free',
        duration='15-20 min',
        problem_count='20 questions',
        level='All Levels',
        order=10
    ),
]


def get_sorted_courses() -> List[dict]:
    """Get all courses sorted by order, as dictionaries."""
    sorted_courses = sorted(COURSES, key=lambda x: x.order)
    return [course.to_dict() for course in sorted_courses]
