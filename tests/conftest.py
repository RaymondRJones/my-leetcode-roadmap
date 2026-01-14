"""
Pytest configuration and fixtures for testing.
"""
import pytest
from flask import session
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield


@pytest.fixture
def mock_user_data():
    """Create mock user data for testing."""
    return {
        'id': 'user_123',
        'email_addresses': [
            {'email_address': 'test@example.com'}
        ],
        'private_metadata': {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': True
        },
        'public_metadata': {
            'has_premium': True
        }
    }


@pytest.fixture
def mock_allowed_user_data():
    """Create mock data for an allowed user."""
    return {
        'id': 'user_456',
        'email_addresses': [
            {'email_address': 'admin@example.com'}
        ],
        'private_metadata': {},
        'public_metadata': {}
    }


@pytest.fixture
def mock_non_premium_user_data():
    """Create mock data for a non-premium user."""
    return {
        'id': 'user_789',
        'email_addresses': [
            {'email_address': 'free@example.com'}
        ],
        'private_metadata': {
            'has_premium': False,
            'has_ai_access': False,
            'has_system_design_access': False
        },
        'public_metadata': {}
    }


@pytest.fixture
def mock_ai_user_data():
    """Create mock data for a user with AI access."""
    return {
        'id': 'user_ai',
        'email_addresses': [
            {'email_address': 'ai_user@example.com'}
        ],
        'private_metadata': {
            'has_premium': True,
            'has_ai_access': True,
            'has_system_design_access': False
        },
        'public_metadata': {}
    }


@pytest.fixture
def mock_full_access_user_data():
    """Create mock data for a user with full access."""
    return {
        'id': 'user_full',
        'email_addresses': [
            {'email_address': 'full@example.com'}
        ],
        'private_metadata': {
            'has_premium': True,
            'has_ai_access': True,
            'has_system_design_access': True
        },
        'public_metadata': {
            'has_premium': True
        }
    }


@pytest.fixture
def authenticated_client(app, mock_user_data):
    """Create test client with authenticated premium user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = mock_user_data
    return client


@pytest.fixture
def non_premium_client(app, mock_non_premium_user_data):
    """Create test client with authenticated non-premium user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = mock_non_premium_user_data
    return client


@pytest.fixture
def allowed_user_client(app, mock_allowed_user_data):
    """Create test client with allowed user (admin)."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = mock_allowed_user_data
    return client


@pytest.fixture
def full_access_client(app, mock_full_access_user_data):
    """Create test client with full access user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = mock_full_access_user_data
    return client
