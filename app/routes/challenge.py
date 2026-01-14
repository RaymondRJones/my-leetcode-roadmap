"""
Challenge routes for 28-day LeetCode challenge.

Provides routes for:
- Challenge landing/enrollment page
- Daily problem view with code editor
- Calendar view showing progress
- Leaderboard
- Admin dashboard and submission management
"""
from flask import Blueprint, render_template, redirect, current_app

from ..auth.decorators import login_required, admin_required
from ..auth.access import get_current_user, is_admin

challenge_bp = Blueprint('challenge', __name__, url_prefix='/challenge')


@challenge_bp.route('/')
def challenge_home():
    """Challenge landing/enrollment page."""
    user = get_current_user()
    challenge_data = {}
    enrolled = False

    if user:
        public_metadata = user.get('public_metadata', {})
        challenge_data = public_metadata.get('challenge', {})
        enrolled = challenge_data.get('enrolled', False)

    service = current_app.challenge_service
    achievements_config = service.get_achievements_config()
    point_values = service.get_point_values()

    return render_template(
        'challenge/index.html',
        enrolled=enrolled,
        challenge_data=challenge_data,
        achievements_config=achievements_config,
        point_values=point_values,
        total_days=service.get_total_days()
    )


@challenge_bp.route('/day/<int:day>')
@login_required
def challenge_day(day: int):
    """View a specific challenge day with code editor."""
    user = get_current_user()
    user_is_admin = is_admin(user)

    # Admins can access days 1-30, regular users only 1-28
    max_day = 30 if user_is_admin else 28
    if day < 1 or day > max_day:
        return redirect('/challenge')

    public_metadata = user.get('public_metadata', {})
    challenge_data = public_metadata.get('challenge', {})

    # Must be enrolled to access
    if not challenge_data.get('enrolled'):
        return redirect('/challenge')

    service = current_app.challenge_service
    current_day = service.calculate_current_day(challenge_data.get('start_date', ''))

    # Can only access current day or earlier (admins can access any day)
    if day > current_day and not is_admin(user):
        return redirect(f'/challenge/day/{current_day}')

    problems = service.get_day_problems(day)
    theme = service.get_day_theme(day)

    # Check which problems are already solved
    problems_solved = challenge_data.get('problems_solved', {})
    day_key = f'day_{day}'
    solved_ids = problems_solved.get(day_key, [])
    achievements_config = service.get_achievements_config()

    return render_template(
        'challenge/day.html',
        day=day,
        theme=theme,
        problems=problems,
        problem=problems[0] if problems else None,
        current_day=current_day,
        challenge_data=challenge_data,
        solved_ids=solved_ids,
        is_day_complete=service.is_day_complete(day, problems_solved),
        achievements_config=achievements_config
    )


@challenge_bp.route('/calendar')
@login_required
def challenge_calendar():
    """28-day calendar view with progress."""
    user = get_current_user()
    public_metadata = user.get('public_metadata', {})
    challenge_data = public_metadata.get('challenge', {})

    # Must be enrolled to access
    if not challenge_data.get('enrolled'):
        return redirect('/challenge')

    service = current_app.challenge_service
    current_day = service.calculate_current_day(challenge_data.get('start_date', ''))
    days_completed = challenge_data.get('days_completed', [])
    achievements_config = service.get_achievements_config()
    user_is_admin = is_admin(user)

    # Build day data for template
    # Admins can access all days (not locked)
    calendar_days = []
    for day_num in range(1, 29):
        day_problems = service.get_day_problems(day_num)
        calendar_days.append({
            'day': day_num,
            'theme': service.get_day_theme(day_num),
            'problem_count': len(day_problems),
            'is_completed': day_num in days_completed,
            'is_current': day_num == current_day,
            'is_locked': day_num > current_day and not user_is_admin,
            'is_available': day_num <= current_day or user_is_admin
        })

    return render_template(
        'challenge/calendar.html',
        challenge_data=challenge_data,
        current_day=current_day,
        calendar_days=calendar_days,
        achievements_config=achievements_config,
        is_admin=user_is_admin
    )


@challenge_bp.route('/leaderboard')
def challenge_leaderboard():
    """Challenge leaderboard page."""
    user = get_current_user()
    challenge_data = {}

    if user:
        public_metadata = user.get('public_metadata', {})
        challenge_data = public_metadata.get('challenge', {})

    return render_template(
        'challenge/leaderboard.html',
        challenge_data=challenge_data,
        is_enrolled=challenge_data.get('enrolled', False)
    )


# Admin routes
@challenge_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard - view all participants."""
    return render_template('challenge/admin/dashboard.html')


@challenge_bp.route('/admin/submissions')
@admin_required
def admin_submissions():
    """View pending Skool submissions."""
    return render_template('challenge/admin/submissions.html')
