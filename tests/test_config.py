"""
Tests for configuration module.
"""
import pytest
from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, get_config


class TestConfig:
    """Tests for Config class."""

    def test_config_has_required_attributes(self):
        """Test that Config has all required attributes."""
        assert hasattr(Config, 'SECRET_KEY')
        assert hasattr(Config, 'CLERK_SECRET_KEY')
        assert hasattr(Config, 'CLERK_PUBLISHABLE_KEY')
        assert hasattr(Config, 'STRIPE_SECRET_KEY')
        assert hasattr(Config, 'STRIPE_WEBHOOK_SECRET')
        assert hasattr(Config, 'OPENAI_API_KEY')
        assert hasattr(Config, 'PORT')

    def test_stripe_product_metadata_exists(self):
        """Test that Stripe product metadata is defined."""
        assert hasattr(Config, 'STRIPE_PRODUCT_METADATA')
        assert isinstance(Config.STRIPE_PRODUCT_METADATA, dict)
        assert len(Config.STRIPE_PRODUCT_METADATA) >= 1

    def test_allowed_emails_exists(self):
        """Test that allowed emails list is defined."""
        assert hasattr(Config, 'ALLOWED_EMAILS')
        assert isinstance(Config.ALLOWED_EMAILS, list)

    def test_month_mappings_exist(self):
        """Test that month mappings are defined."""
        assert hasattr(Config, 'MONTH_ORDER')
        assert hasattr(Config, 'MONTH_MAPPING')
        assert hasattr(Config, 'INTERMEDIATE_MONTH_ORDER')
        assert isinstance(Config.MONTH_ORDER, list)
        assert isinstance(Config.MONTH_MAPPING, dict)
        assert isinstance(Config.INTERMEDIATE_MONTH_ORDER, list)


class TestDevelopmentConfig:
    """Tests for DevelopmentConfig."""

    def test_debug_is_true(self):
        """Test that debug mode is enabled in development."""
        assert DevelopmentConfig.DEBUG is True

    def test_testing_is_false(self):
        """Test that testing mode is disabled in development."""
        assert DevelopmentConfig.TESTING is False


class TestProductionConfig:
    """Tests for ProductionConfig."""

    def test_debug_is_false(self):
        """Test that debug mode is disabled in production."""
        assert ProductionConfig.DEBUG is False

    def test_testing_is_false(self):
        """Test that testing mode is disabled in production."""
        assert ProductionConfig.TESTING is False


class TestTestingConfig:
    """Tests for TestingConfig."""

    def test_debug_is_true(self):
        """Test that debug mode is enabled in testing."""
        assert TestingConfig.DEBUG is True

    def test_testing_is_true(self):
        """Test that testing mode is enabled in testing."""
        assert TestingConfig.TESTING is True


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_config_class(self):
        """Test that get_config returns a config class."""
        config = get_config()
        assert config is not None
