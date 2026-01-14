"""
Challenge routes for 28-day LeetCode challenge.

Provides routes for:
- Challenge landing/enrollment page
- Daily problem view with code editor
- Calendar view showing progress
- Leaderboard
- Admin dashboard and submission management
"""
from datetime import datetime, timedelta
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
    heatmap_data = []

    if user:
        public_metadata = user.get('public_metadata', {})
        challenge_data = public_metadata.get('challenge', {})
        enrolled = challenge_data.get('enrolled', False)

        # Generate heatmap data for the past year
        if enrolled:
            from datetime import date
            today = date.today()
            year_ago = today - timedelta(days=365)
            activity_log = challenge_data.get('activity_log', {})

            # Build heatmap data structure
            current = year_ago
            while current <= today:
                date_str = current.isoformat()
                count = activity_log.get(date_str, {}).get('count', 0)
                heatmap_data.append({
                    'date': date_str,
                    'count': count,
                    'weekday': current.weekday()
                })
                current += timedelta(days=1)

    service = current_app.challenge_service
    achievements_config = service.get_achievements_config()
    point_values = service.get_point_values()

    return render_template(
        'challenge/index.html',
        enrolled=enrolled,
        challenge_data=challenge_data,
        achievements_config=achievements_config,
        point_values=point_values,
        total_days=service.get_total_days(),
        heatmap_data=heatmap_data
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

    # Parse start date
    start_date_str = challenge_data.get('start_date', '')
    try:
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
    except (ValueError, AttributeError):
        start_date = datetime.now().date()

    # Calculate end date (28 days from start)
    end_date = start_date + timedelta(days=27)

    # Determine which months are shown
    start_month = start_date.strftime('%B %Y')
    end_month = end_date.strftime('%B %Y')
    if start_month == end_month:
        calendar_title = start_month
    else:
        calendar_title = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    # Calculate the weekday of the start date (0=Monday, 6=Sunday)
    # For display: Sunday=0, Monday=1, ..., Saturday=6
    start_weekday = (start_date.weekday() + 1) % 7  # Convert to Sunday=0 format

    # Build day data for template with actual dates
    # Admins can access all days (not locked)
    calendar_days = []
    for day_num in range(1, 29):
        day_date = start_date + timedelta(days=day_num - 1)
        day_problems = service.get_day_problems(day_num)
        calendar_days.append({
            'day': day_num,
            'date': day_date,
            'date_display': day_date.day,  # Just the day number
            'month_short': day_date.strftime('%b'),  # Month abbreviation
            'is_new_month': day_date.day == 1,  # Flag if this is first of month
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
        is_admin=user_is_admin,
        start_date=start_date,
        start_weekday=start_weekday,
        calendar_title=calendar_title
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
