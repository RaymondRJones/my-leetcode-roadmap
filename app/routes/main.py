"""
Main routes blueprint for pages.
"""
from flask import Blueprint, render_template, redirect, current_app

from ..auth.access import get_current_user, has_premium_access, is_allowed_user
from ..auth.decorators import login_required, premium_required, ai_access_required
from ..models.course import get_sorted_courses

main_bp = Blueprint('main', __name__)


# Behavioral questions data
BEHAVIORAL_QUESTIONS = {
    "General": [
        "Why do you want to work for [our company]? / Why are you leaving your job?",
        "What are your goals for the future?",
        "What are your strengths / weaknesses?",
        "Do you have experience working with cross-functional teams?",
        "Tell me about a project you're proud of"
    ],
    "Customer Obsession": [
        "Tell me about a time you went above and beyond for a customer.",
        "How do you prioritize customer needs in your work?"
    ],
    "Ownership": [
        "Describe a time when you took on a task beyond your responsibilities.",
        "Tell me about a time you made a mistake at work. How did you handle it?",
        "Tell me about a time you received feedback from your manager and what did you do?"
    ],
    "Invent and Simplify": [
        "Describe a time you created a simple solution to a complex problem.",
        "Tell me about a process you improved. What was your approach?"
    ],
    "Are Right, A Lot": [
        "Tell me about a decision you made that was wrong. What did you learn?",
        "Describe a time when you had to make a difficult judgment call."
    ],
    "Learn and Be Curious": [
        "Tell me about a time you picked up a new skill to solve a problem.",
        "What's the most recent thing you learned on your own?"
    ],
    "Think Big": [
        "Tell me about a time you proposed a bold idea. What happened?",
        "Describe a situation where you took a long-term view to solve a problem."
    ],
    "Bias for Action": [
        "Give me an example of a time when you made a decision quickly.",
        "Tell me about a time you took initiative to start a project."
    ],
    "Earn Trust": [
        "Tell me about a time you had a conflict with a colleague. How did you handle it?",
        "Describe how you build relationships in a team."
    ],
    "Dive Deep": [
        "Tell me about a technical problem you had to dig into to understand.",
        "How do you identify root causes when something goes wrong?"
    ],
    "Have Backbone; Disagree and Commit": [
        "Tell me about a time you strongly disagreed with your manager or team.",
        "Describe a situation where you advocated for a different approach."
    ],
    "Deliver Results": [
        "Tell me about a time you had to deliver a project under a tight deadline.",
        "Describe how you stay focused and productive."
    ]
}


@main_bp.route('/')
def index():
    """Classroom homepage - Central hub for all courses."""
    courses = get_sorted_courses()
    return render_template('classroom.html', courses=courses)


@main_bp.route('/classroom')
def classroom():
    """Redirect to classroom homepage."""
    return redirect('/')


@main_bp.route('/landing')
def sales_page():
    """Sales page showing all available premium roadmaps."""
    return render_template('sales_homepage.html')


@main_bp.route('/intermediate')
def intermediate_view():
    """Intermediate roadmap (Fortune500) - Free for all users."""
    roadmap_service = current_app.roadmap
    return render_template('intermediate.html', roadmap=roadmap_service.get_ordered_intermediate_roadmap_data())


@main_bp.route('/advanced')
@premium_required
def advanced_view():
    """Advanced roadmap page - Premium content."""
    roadmap_service = current_app.roadmap
    return render_template('index.html', roadmap=roadmap_service.get_ordered_roadmap_data())


@main_bp.route('/advanced/month/<month_name>')
@premium_required
def advanced_month_view(month_name):
    """View for a specific advanced month - Premium content."""
    roadmap_service = current_app.roadmap
    original_month = roadmap_service.get_original_month_name(month_name)
    month_data = roadmap_service.get_month_data(original_month)
    return render_template('month.html', month=month_name, days=month_data)


@main_bp.route('/month/<month_name>')
def intermediate_month_redirect(month_name):
    """Redirect old intermediate month URLs to new structure."""
    return redirect(f'/intermediate/month/{month_name}')


@main_bp.route('/intermediate/month/<month_name>')
def intermediate_month_view(month_name):
    """View for a specific intermediate month - Month 1 is free, Month 2+ requires premium."""
    # Allow Month 1 for everyone, require premium for Month 2 and 3
    if month_name != 'Month 1':
        user = get_current_user()
        if not user:
            return redirect('/landing')
        if not has_premium_access(user) and not is_allowed_user(user):
            return redirect('/landing')

    roadmap_service = current_app.roadmap
    ordered_data = roadmap_service.get_ordered_intermediate_roadmap_data()
    month_data = ordered_data.get(month_name, [])
    return render_template('month.html', month=f"Intermediate {month_name}", days=month_data, is_intermediate=True)


@main_bp.route('/beginner')
def beginner_view():
    """View for beginner AtCoder problems."""
    roadmap_service = current_app.roadmap
    return render_template('beginner.html', atcoder_data=roadmap_service.get_atcoder_problems())


@main_bp.route('/beginner/problem/<int:problem_id>')
def beginner_problem_editor(problem_id):
    """Interactive problem editor for beginner problems."""
    roadmap_service = current_app.roadmap
    problems = roadmap_service.get_atcoder_problems().get('problems', [])

    if 0 <= problem_id < len(problems):
        problem = problems[problem_id]
        total_problems = len(problems)
        return render_template(
            'beginner/problem.html',
            problem=problem,
            problem_id=problem_id,
            total_problems=total_problems,
            prev_id=problem_id - 1 if problem_id > 0 else None,
            next_id=problem_id + 1 if problem_id < total_problems - 1 else None
        )
    return "Problem not found", 404


@main_bp.route('/roadmap')
def software_roadmap():
    """Raymond's Path to Software Engineer at Fortune 1."""
    return render_template('roadmap.html')


@main_bp.route('/about')
def about():
    """About Raymond and his journey."""
    return render_template('about.html')


@main_bp.route('/python-assessment')
def python_assessment():
    """Python programming assessment quiz."""
    return render_template('python_assessment.html')


@main_bp.route('/java-assessment')
def java_assessment():
    """Java programming assessment quiz."""
    return render_template('java_assessment.html')


@main_bp.route('/guides')
@premium_required
def guides():
    """Guides landing page with all available guides."""
    return render_template('guides.html')


@main_bp.route('/behavioral-guide')
@ai_access_required
def behavioral_guide():
    """Behavioral Interview Guide with AI Helper - AI Access Required."""
    return render_template('behavioral_guide.html', questions=BEHAVIORAL_QUESTIONS)


@main_bp.route('/complete-list')
@premium_required
def complete_list():
    """Complete question list with customizable time sliders."""
    roadmap_service = current_app.roadmap
    all_questions = roadmap_service.get_all_problems()
    return render_template('complete_list.html', questions_data=all_questions)


@main_bp.route('/privacy')
def privacy_policy():
    """Privacy Policy page."""
    return render_template('privacy_policy.html')


@main_bp.route('/terms')
def terms_of_service():
    """Terms of Service page."""
    return render_template('terms_of_service.html')


@main_bp.route('/coaching')
def coaching():
    """Coaching page with Skool community and 1-1 coaching offerings."""
    return render_template('coaching.html')
