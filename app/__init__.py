"""
LeetCode Roadmap Generator Application Factory.

This module contains the application factory for creating Flask app instances.
"""
import os
from flask import Flask, request

from .config import config, get_config
from .services import ClerkService, StripeService, OpenAIService, RoadmapService
from .services.challenge_service import ChallengeService
from .auth.access import (
    get_current_user,
    has_premium_access,
    has_ai_access,
    has_system_design_access,
    has_guides_access,
    is_allowed_user,
    is_admin
)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for creating Flask app instances.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        env = os.environ.get('FLASK_ENV', 'development')
        config_name = 'production' if env == 'production' else 'development'

    # Create Flask app
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Load configuration
    app.config.from_object(config[config_name])

    # Validate required configuration
    if not app.config.get('CLERK_PUBLISHABLE_KEY'):
        raise RuntimeError("Please set the CLERK_PUBLISHABLE_KEY in your .env file.")

    # Initialize services and attach to app
    _init_services(app)

    # Register blueprints
    _register_blueprints(app)

    # Register context processor
    _register_context_processor(app)

    return app


def _init_services(app: Flask):
    """Initialize and attach services to the Flask app."""
    # Clerk service
    app.clerk = ClerkService(
        secret_key=app.config.get('CLERK_SECRET_KEY')
    )

    # Stripe service
    app.stripe = StripeService(
        secret_key=app.config.get('STRIPE_SECRET_KEY'),
        webhook_secret=app.config.get('STRIPE_WEBHOOK_SECRET'),
        product_config=app.config.get('STRIPE_PRODUCT_METADATA', {})
    )

    # OpenAI service
    app.openai = OpenAIService(
        api_key=app.config.get('OPENAI_API_KEY')
    )

    # Roadmap service
    app.roadmap = RoadmapService(
        month_order=app.config.get('MONTH_ORDER', []),
        month_mapping=app.config.get('MONTH_MAPPING', {}),
        intermediate_month_order=app.config.get('INTERMEDIATE_MONTH_ORDER', [])
    )

    # Challenge service
    app.challenge_service = ChallengeService()


def _register_blueprints(app: Flask):
    """Register all blueprints with the Flask app."""
    from .routes import auth_bp, main_bp, api_bp, system_design_bp, challenge_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(system_design_bp)
    app.register_blueprint(challenge_bp)


def _register_context_processor(app: Flask):
    """Register the context processor for template variables."""

    @app.context_processor
    def inject_auth():
        """Inject authentication data into all templates."""
        user = get_current_user()

        # Get theme from cookie, default to 'dark' for new TailwindCSS theme
        theme_mode = request.cookies.get('theme', 'dark')
        if theme_mode not in ('dark', 'legacy'):
            theme_mode = 'dark'

        return {
            'current_user': user,
            'is_authenticated': user is not None,
            'has_premium': has_premium_access(user) if user else False,
            'has_ai_access': has_ai_access(user) if user else False,
            'has_system_design_access': has_system_design_access(user) if user else False,
            'has_guides_access': has_guides_access(user) if user else False,
            'is_allowed': is_allowed_user(user) if user else False,
            'is_admin': is_admin(user) if user else False,
            'clerk_publishable_key': app.config.get('CLERK_PUBLISHABLE_KEY'),
            'theme_mode': theme_mode
        }
