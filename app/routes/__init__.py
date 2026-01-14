"""
Routes package for the LeetCode Roadmap Generator.
"""
from .auth import auth_bp
from .main import main_bp
from .api import api_bp
from .system_design import system_design_bp

__all__ = ['auth_bp', 'main_bp', 'api_bp', 'system_design_bp']
