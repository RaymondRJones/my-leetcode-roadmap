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

    # Resend (Email)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    # Server
    PORT = int(os.environ.get('PORT', 5002))

    # Stripe Product Metadata Mapping
    STRIPE_PRODUCT_METADATA = {
        'prod_SvD9M0caNlgkfo': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': False,
            'has_guides_access': False,
            'description': 'Premium Only'
        },
        'prod_SzSs6oMiUWlWAn': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': True,
            'has_guides_access': False,
            'description': 'Premium + System Design'
        },
        'prod_SzSqbijjdXdg2a': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': True,
            'has_guides_access': True,
            'description': 'Premium + System Design + Guides'
        },
        'prod_ToxWA5I9pXccTZ': {
            'has_premium': False,
            'has_ai_access': True,
            'has_system_design_access': False,
            'has_guides_access': False,
            'description': 'Behavioral Guide + AI'
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

    # Course wrapper video configuration
    COURSE_VIDEOS = {
        'beginner': {
            'title': 'Complete Beginner Roadmap',
            'description': 'Master programming fundamentals with 50+ beginner-friendly problems',
            'practice_url': '/beginner',
            'practice_label': 'Start Practicing',
            'icon': 'school',
            'videos': [
                {'part': 1, 'title': 'Part 1: Introduction', 'loom_id': '6cf2fa695427462eada1d08cc1d4df51'},
                {'part': 2, 'title': 'Part 2: Getting Started', 'loom_id': '64638a1b088e473e80b6005ab556562d'},
                {'part': 3, 'title': 'Part 3: Core Concepts', 'loom_id': '31a7f53db88b45c889d1e7aaf04cedbb'},
                {'part': 4, 'title': 'Part 4: Practice Strategy', 'loom_id': 'e6cab940c3844ff09f45a5f16c64a3f1'},
            ]
        },
        'intermediate': {
            'title': 'Fortune 500 Roadmap',
            'description': 'Intermediate preparation for mid-tier company interviews',
            'practice_url': '/intermediate',
            'practice_label': 'Start Practicing',
            'icon': 'rocket_launch',
            'videos': [
                {'part': 1, 'title': 'Part 1: Introduction', 'loom_id': '6cf2fa695427462eada1d08cc1d4df51'},
                {'part': 2, 'title': 'Part 2: Getting Started', 'loom_id': '64638a1b088e473e80b6005ab556562d'},
                {'part': 3, 'title': 'Part 3: Core Concepts', 'loom_id': '31a7f53db88b45c889d1e7aaf04cedbb'},
                {'part': 4, 'title': 'Part 4: Practice Strategy', 'loom_id': 'e6cab940c3844ff09f45a5f16c64a3f1'},
            ]
        }
    }

    # Guide wrapper configuration for individual guide pages
    GUIDE_VIDEOS = {
        'resume': {
            'title': 'Resume + LinkedIn Guide',
            'description': 'My exact resume and LinkedIn profile that landed me offers at Fortune 1 companies.',
            'icon': 'description',
            'embed_type': 'youtube',
            'embed_id': 'xX3riyhZEdk',
            'embed_start': 1171,
            'external_links': [
                {
                    'label': 'View Resume Template',
                    'url': 'https://docs.google.com/document/d/1pxdEyiefpXsZ2NdIYDQ13W5nt21Gt2La4JL7goEh8SQ/edit',
                    'icon': 'description'
                }
            ],
            'features': [
                'My exact resume template',
                'Video breakdown & analysis',
                'LinkedIn optimization tips',
                'ATS-friendly formatting'
            ]
        },
        'job-search': {
            'title': 'Complete Job Search Guide 2026',
            'description': 'Everything I learned landing multiple job offers at top tech companies.',
            'icon': 'work',
            'embed_type': 'loom',
            'embed_id': 'afc5bcb3e0e34977ad93ceb17848fcee',
            'features': [
                'Job search strategy',
                'Resume and LinkedIn optimization',
                'Technical interview prep',
                'System Design strategies'
            ]
        },
        'leetcode': {
            'title': '100+ Hours of LeetCode Solutions',
            'description': 'Live coding sessions solving LeetCode problems before I got my Walmart offer.',
            'icon': 'code',
            'embed_type': 'youtube_playlist',
            'playlist_id': 'PL6Gg1ReZX6gU7tyZPiZF8AlsSpKSumRcK',
            'features': [
                'Detailed problem explanations',
                'Multiple solution approaches',
                'Time & space complexity analysis'
            ],
            'stats': {
                'videos': '100+',
                'difficulty': 'All Levels',
                'style': 'Live Problem Solving'
            }
        },
        'behavioral': {
            'title': 'Behavioral Interview Guide',
            'description': 'AI-powered STAR story practice and feedback.',
            'icon': 'psychology',
            'embed_type': 'external_app',
            'app_url': 'https://behavioral-ai.vercel.app/',
            'features': [
                '50+ behavioral questions',
                'AI feedback system',
                'STAR method framework',
                'Amazon Leadership Principles'
            ]
        }
    }


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
