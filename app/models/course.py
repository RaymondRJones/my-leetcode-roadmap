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
    access_type: str = 'free'  # 'free', 'premium', 'ai_access', 'system_design'

    def to_dict(self) -> dict:
        """Convert course to dictionary for template rendering."""
        return asdict(self)


# All course definitions
COURSES: List[Course] = [
    Course(
        title='Complete Beginner Roadmap',
        description='Master programming fundamentals with 200+ beginner-friendly problems. Perfect for absolute beginners starting from zero.',
        route='/beginner/course',
        icon='school',
        label='LEVEL 1',
        image_url='/static/images/course-beginner.jpg',
        is_premium=False,
        course_type='course-free',
        duration='4-8 weeks',
        problem_count='50 problems',
        level='Beginner',
        order=1,
        access_type='free'
    ),
    Course(
        title='Fortune500 Roadmap',
        description='Intermediate preparation for mid-tier companies. Master 3 months of curated problems for mid-level interviews.',
        route='/intermediate/course',
        icon='rocket_launch',
        label='LEVEL 2',
        image_url='/static/images/course-intermediate.jpg',
        is_premium=False,
        course_type='course-free',
        duration='3 months',
        problem_count='80 problems',
        level='Intermediate',
        order=2,
        access_type='free'
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
        order=3,
        access_type='free'
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
        order=4,
        access_type='free'
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
        order=5,
        access_type='free'
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
        order=6,
        access_type='free'
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
        order=7,
        access_type='premium'
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
        order=8,
        access_type='premium'
    ),
    Course(
        title='Resume + LinkedIn Guide',
        description='My exact resume and LinkedIn profile that landed me offers at Fortune 1 companies. Step-by-step templates and strategies.',
        route='/guides/resume',
        icon='description',
        label='CAREER DOCS',
        image_url='/static/images/course-resume.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='30 min',
        problem_count='Templates',
        level='All Levels',
        order=9,
        access_type='premium'
    ),
    Course(
        title='Complete Job Search Guide 2026',
        description='Everything I learned landing multiple job offers at top tech companies. Job search strategy, resume optimization, and interview prep.',
        route='/guides/job-search',
        icon='work',
        label='JOB SEARCH',
        image_url='/static/images/course-job-search.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='2 hours',
        problem_count='Full Course',
        level='All Levels',
        order=10,
        access_type='premium'
    ),
    Course(
        title='100+ Hours of LeetCode Solutions',
        description='Live coding sessions solving LeetCode problems. Watch my exact thought process before I got my Walmart offer.',
        route='/guides/leetcode',
        icon='code',
        label='VIDEO SOLUTIONS',
        image_url='/static/images/course-leetcode-solutions.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='100+ hours',
        problem_count='100+ Videos',
        level='All Levels',
        order=11,
        access_type='premium'
    ),
    Course(
        title='Behavioral Interview Guide',
        description='AI-powered STAR story practice and feedback. Master behavioral interviews with 50+ common questions and instant AI feedback.',
        route='/guides/behavioral',
        icon='psychology',
        label='AI PRACTICE',
        image_url='/static/images/course-behavioral.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='5+ hours',
        problem_count='50+ Questions',
        level='All Levels',
        order=12,
        access_type='ai_access'
    ),
    Course(
        title='System Design Guide',
        description='Master system design interviews with real-world examples, architecture patterns, and scalability principles.',
        route='/system-design/',
        icon='account_tree',
        label='ARCHITECTURE',
        image_url='/static/images/course-system-design.jpg',
        is_premium=True,
        course_type='course-premium',
        duration='4-8 weeks',
        problem_count='Design patterns',
        level='Advanced',
        order=13,
        access_type='system_design'
    ),
]


def get_sorted_courses() -> List[dict]:
    """Get all courses sorted by order, as dictionaries."""
    sorted_courses = sorted(COURSES, key=lambda x: x.order)
    return [course.to_dict() for course in sorted_courses]
