"""
Configuration classes for the LeetCode Roadmap Generator application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

    # Clerk
    CLERK_SECRET_KEY = os.environ.get('CLERK_SECRET_KEY')
    CLERK_PUBLISHABLE_KEY = os.environ.get('CLERK_PUBLISHABLE_KEY')

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # Server
    PORT = int(os.environ.get('PORT', 5002))

    # Stripe Product Metadata Mapping
    STRIPE_PRODUCT_METADATA = {
        'prod_SvD9M0caNlgkfo': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': False,
            'description': 'Premium Only'
        },
        'prod_SzSqbijjdXdg2a': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': True,
            'description': 'Premium + System Design'
        },
        'prod_SxymCQ9tLRKY3u': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': True,
            'description': 'Premium + System Design (Alternate)'
        }
    }

    # Allowed emails with special access
    ALLOWED_EMAILS = [
        'admin@example.com',
        'raymond@example.com',
    ]

    # Month mapping for roadmap display
    MONTH_ORDER = ['April', 'May', 'June', 'July', 'August']
    MONTH_MAPPING = {
        'April': 'Month 1',
        'May': 'Month 2',
        'June': 'Month 3',
        'July': 'Month 4',
        'August': 'Month 5'
    }
    INTERMEDIATE_MONTH_ORDER = ['Month 1', 'Month 2', 'Month 3']


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig
