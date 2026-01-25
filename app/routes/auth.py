"""
Authentication routes blueprint.
"""
import os
from flask import Blueprint, render_template, jsonify, request, redirect, session, current_app

from ..auth.access import (
    get_current_user,
    has_premium_access,
    has_ai_access,
    has_system_design_access,
    is_allowed_user
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_themed_template(base_name):
    """Return the themed template name based on user preference.

    Args:
        base_name: Base template name without extension (e.g., 'auth/login')

    Returns:
        Template filename with appropriate suffix based on theme cookie
    """
    theme = request.cookies.get('theme', 'dark')

    if theme == 'dark':
        tw_template = f'{base_name}_tw.html'
        # Check if TailwindCSS template exists using absolute path
        template_path = os.path.join(current_app.root_path, current_app.template_folder, tw_template)
        if os.path.exists(template_path):
            return tw_template

    # Fall back to legacy template
    return f'{base_name}.html'


@auth_bp.route('/login')
def login():
    """Login page - handled by Clerk on frontend."""
    return render_template(get_themed_template('auth/login'))


@auth_bp.route('/callback', methods=['POST'])
def callback():
    """Handle Clerk auth callback."""
    try:
        data = request.get_json()
        user_data = data.get('user')

        if user_data:
            # Store user data in Flask session
            session['user'] = user_data
            return jsonify({'status': 'success'})

        return jsonify({'status': 'error', 'message': 'No user data provided'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@auth_bp.route('/logout')
def logout():
    """Logout user."""
    session.pop('user', None)
    return redirect('/')


@auth_bp.route('/status')
def status():
    """Show authentication status page."""
    return render_template(get_themed_template('auth_status'))


@auth_bp.route('/debug')
def debug():
    """Debug authentication state (for development)."""
    user = get_current_user()
    return jsonify({
        'authenticated': user is not None,
        'user_data': user,
        'has_premium': has_premium_access(user),
        'has_ai_access': has_ai_access(user),
        'has_system_design_access': has_system_design_access(user),
        'is_allowed': is_allowed_user(user),
        'session_data': dict(session)
    })
