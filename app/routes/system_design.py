"""
System design routes blueprint.
"""
from flask import Blueprint, render_template

from ..auth.decorators import system_design_access_required

system_design_bp = Blueprint('system_design', __name__, url_prefix='/system-design')


@system_design_bp.route('/')
@system_design_access_required
def index():
    """System Design Roadmap homepage - System Design Access Required."""
    return render_template('system_design/index.html')


@system_design_bp.route('/real-life-problems')
@system_design_access_required
def real_life_problems():
    """System Design Real Life Problems page - System Design Access Required."""
    return render_template('system_design/real_life_problems.html')


@system_design_bp.route('/trivia')
@system_design_access_required
def trivia():
    """System Design Trivia and Knowledge Checks page - System Design Access Required."""
    return render_template('system_design/trivia.html')


@system_design_bp.route('/low-level-design')
@system_design_access_required
def low_level_design():
    """System Design Low Level Design page - System Design Access Required."""
    return render_template('system_design/low_level_design.html')
