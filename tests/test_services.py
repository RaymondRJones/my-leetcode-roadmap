"""
Tests for services module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.clerk_service import ClerkService
from app.services.stripe_service import StripeService
from app.services.openai_service import OpenAIService


class TestClerkService:
    """Tests for ClerkService."""

    def test_init_with_secret_key(self):
        """Test initialization with secret key."""
        service = ClerkService(secret_key='test_key')
        assert service.secret_key == 'test_key'

    def test_init_without_secret_key(self):
        """Test initialization without secret key."""
        service = ClerkService()
        assert service.secret_key is None

    def test_is_configured_with_key(self):
        """Test is_configured returns True when key is set."""
        service = ClerkService(secret_key='test_key')
        assert service.is_configured() is True

    def test_is_configured_without_key(self):
        """Test is_configured returns False when key is not set."""
        service = ClerkService()
        assert service.is_configured() is False

    def test_headers_property(self):
        """Test headers property returns correct format."""
        service = ClerkService(secret_key='test_key')
        headers = service.headers
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test_key'
        assert headers['Content-Type'] == 'application/json'

    def test_get_user_by_email_returns_none_when_not_configured(self):
        """Test get_user_by_email returns None when not configured."""
        service = ClerkService()
        result = service.get_user_by_email('test@example.com')
        assert result is None

    @patch('app.services.clerk_service.requests.get')
    def test_get_user_by_email_success(self, mock_get):
        """Test successful user lookup."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 'user_123',
                'email_addresses': [{'email_address': 'test@example.com'}]
            }
        ]
        mock_get.return_value = mock_response

        service = ClerkService(secret_key='test_key')
        result = service.get_user_by_email('test@example.com')

        assert result is not None
        assert result['id'] == 'user_123'

    @patch('app.services.clerk_service.requests.get')
    def test_get_user_by_email_not_found(self, mock_get):
        """Test user lookup when user not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        service = ClerkService(secret_key='test_key')
        result = service.get_user_by_email('notfound@example.com')

        assert result is None


class TestStripeService:
    """Tests for StripeService."""

    def test_init(self):
        """Test initialization."""
        product_config = {'prod_123': {'has_premium': True}}
        service = StripeService(
            secret_key='sk_test',
            webhook_secret='whsec_test',
            product_config=product_config
        )
        assert service.secret_key == 'sk_test'
        assert service.webhook_secret == 'whsec_test'
        assert service.product_config == product_config

    def test_is_configured(self):
        """Test is_configured."""
        service = StripeService('sk_test', 'whsec_test', {})
        assert service.is_configured() is True

        service = StripeService(None, 'whsec_test', {})
        assert service.is_configured() is False

    def test_is_webhook_configured(self):
        """Test is_webhook_configured."""
        service = StripeService('sk_test', 'whsec_test', {})
        assert service.is_webhook_configured() is True

        service = StripeService('sk_test', None, {})
        assert service.is_webhook_configured() is False

    def test_is_supported_event(self):
        """Test is_supported_event."""
        service = StripeService('sk_test', 'whsec_test', {})

        assert service.is_supported_event('checkout.session.completed') is True
        assert service.is_supported_event('invoice.payment_succeeded') is True
        assert service.is_supported_event('customer.subscription.deleted') is True
        assert service.is_supported_event('random.event') is False

    def test_get_product_metadata_known_product(self):
        """Test get_product_metadata for known product."""
        product_config = {
            'prod_123': {
                'has_premium': True,
                'has_ai_access': False,
                'description': 'Premium'
            }
        }
        service = StripeService('sk_test', 'whsec_test', product_config)

        metadata = service.get_product_metadata('prod_123')
        assert metadata['has_premium'] is True
        assert metadata['description'] == 'Premium'

    def test_get_product_metadata_unknown_product(self):
        """Test get_product_metadata for unknown product."""
        service = StripeService('sk_test', 'whsec_test', {})

        metadata = service.get_product_metadata('unknown_prod')
        assert metadata['has_premium'] is True  # Default access
        assert 'Unknown Product' in metadata['description']

    def test_extract_customer_email_from_customer_email_field(self):
        """Test extracting customer email from customer_email field."""
        service = StripeService('sk_test', 'whsec_test', {})

        event = {
            'data': {
                'object': {
                    'customer_email': 'test@example.com'
                }
            }
        }

        email = service.extract_customer_email(event)
        assert email == 'test@example.com'

    def test_extract_customer_email_from_customer_details(self):
        """Test extracting customer email from customer_details."""
        service = StripeService('sk_test', 'whsec_test', {})

        event = {
            'data': {
                'object': {
                    'customer_details': {
                        'email': 'details@example.com'
                    }
                }
            }
        }

        email = service.extract_customer_email(event)
        assert email == 'details@example.com'


class TestOpenAIService:
    """Tests for OpenAIService."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        service = OpenAIService(api_key='sk-test')
        assert service.api_key == 'sk-test'

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        service = OpenAIService()
        assert service.api_key is None

    def test_is_configured_with_key(self):
        """Test is_configured returns True when key is set."""
        service = OpenAIService(api_key='sk-test')
        assert service.is_configured() is True

    def test_is_configured_without_key(self):
        """Test is_configured returns False when key is not set."""
        service = OpenAIService()
        assert service.is_configured() is False

    def test_client_raises_without_api_key(self):
        """Test that accessing client raises error without API key."""
        service = OpenAIService()
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            _ = service.client

    def test_behavioral_system_prompt_exists(self):
        """Test that behavioral system prompt is defined."""
        assert OpenAIService.BEHAVIORAL_SYSTEM_PROMPT is not None
        assert len(OpenAIService.BEHAVIORAL_SYSTEM_PROMPT) > 0
        assert 'STAR' in OpenAIService.BEHAVIORAL_SYSTEM_PROMPT
