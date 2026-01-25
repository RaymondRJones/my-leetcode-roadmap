"""
System design routes blueprint.
"""
import os
from flask import Blueprint, render_template, current_app, request

from ..auth.decorators import system_design_access_required


def get_themed_template(base_name):
    """
    Get the appropriate template based on user's theme preference.

    Args:
        base_name: Base template name without extension (e.g., 'system_design/index')

    Returns:
        Template path based on theme ('dark' = *_tw.html, 'legacy' = *.html)
    """
    theme = request.cookies.get('theme', 'dark')

    if theme == 'dark':
        tw_template = f"{base_name}_tw.html"
        # Check if TailwindCSS template exists using absolute path
        template_path = os.path.join(current_app.root_path, current_app.template_folder, tw_template)
        if os.path.exists(template_path):
            return tw_template

    # Fall back to legacy template
    return f"{base_name}.html"


system_design_bp = Blueprint('system_design', __name__, url_prefix='/system-design')


@system_design_bp.route('/')
@system_design_access_required
def index():
    """System Design Roadmap homepage - System Design Access Required."""
    return render_template(get_themed_template('system_design/index'))


@system_design_bp.route('/real-life-problems')
@system_design_access_required
def real_life_problems():
    """System Design Real Life Problems page - System Design Access Required."""
    return render_template(get_themed_template('system_design/real_life_problems'))


@system_design_bp.route('/trivia')
@system_design_access_required
def trivia():
    """System Design Trivia and Knowledge Checks page - System Design Access Required."""
    return render_template(get_themed_template('system_design/trivia'))


@system_design_bp.route('/low-level-design')
@system_design_access_required
def low_level_design():
    """System Design Low Level Design page - System Design Access Required."""
    return render_template(get_themed_template('system_design/low_level_design'))
