"""
Stripe service for payment processing and webhook handling.
"""
import stripe
from typing import Optional


class StripeService:
    """Service class for Stripe operations."""

    SUPPORTED_EVENTS = [
        'checkout.session.completed',
        'invoice.payment_succeeded',
        'customer.subscription.updated',
        'customer.subscription.deleted'
    ]

    def __init__(self, secret_key: Optional[str], webhook_secret: Optional[str], product_config: dict):
        """Initialize the Stripe service."""
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        self.product_config = product_config

        if secret_key:
            stripe.api_key = secret_key

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.secret_key)

    def is_webhook_configured(self) -> bool:
        """Check if webhook is properly configured."""
        return bool(self.webhook_secret)

    def verify_webhook(self, payload: bytes, signature: str) -> Optional[dict]:
        """Verify and construct webhook event."""
        if not self.is_webhook_configured():
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError as e:
            print(f"Invalid webhook payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid webhook signature: {e}")
            return None

    def is_supported_event(self, event_type: str) -> bool:
        """Check if event type is supported."""
        return event_type in self.SUPPORTED_EVENTS

    def extract_customer_email(self, event: dict) -> Optional[str]:
        """Extract customer email from Stripe event."""
        data = event.get('data', {}).get('object', {})

        # Try customer_email field
        if 'customer_email' in data and data['customer_email']:
            return data['customer_email']

        # Try customer_details
        if 'customer_details' in data:
            email = data['customer_details'].get('email')
            if email:
                return email

        # Fetch customer object
        customer_id = data.get('customer')
        if customer_id and self.is_configured():
            try:
                customer = stripe.Customer.retrieve(customer_id)
                return customer.email
            except Exception as e:
                print(f"Error fetching customer {customer_id}: {e}")
                return None

        return None

    def extract_product_id(self, event: dict) -> Optional[str]:
        """Extract product ID from Stripe event."""
        event_type = event.get('type', '')
        data = event.get('data', {}).get('object', {})

        # For checkout.session.completed
        if event_type == 'checkout.session.completed':
            line_items = data.get('line_items', {}).get('data', [])

            # If line_items not in event, fetch the session with expanded line_items
            if not line_items and self.is_configured():
                session_id = data.get('id')
                if session_id:
                    try:
                        print(f"Fetching session {session_id} with line items...")
                        session = stripe.checkout.Session.retrieve(
                            session_id,
                            expand=['line_items']
                        )
                        line_items = session.get('line_items', {}).get('data', [])
                        print(f"Retrieved {len(line_items)} line items")
                    except Exception as e:
                        print(f"Error fetching session: {e}")

            # Extract product from line items
            if line_items:
                price = line_items[0].get('price', {})
                product_id = price.get('product')
                print(f"Found product ID from line items: {product_id}")
                return product_id

        # For subscription/invoice events
        if 'subscription' in event_type or event_type == 'invoice.payment_succeeded':
            if 'items' in data:
                items = data['items'].get('data', [])
                if items:
                    price = items[0].get('price', {})
                    return price.get('product')

            if 'lines' in data:
                lines = data['lines'].get('data', [])
                if lines:
                    price = lines[0].get('price', {})
                    return price.get('product')

        return None

    def get_product_metadata(self, product_id: str) -> dict:
        """Get product metadata from configuration."""
        metadata = self.product_config.get(product_id)

        if not metadata:
            print(f"Unknown product ID: {product_id}, using default premium access")
            return {
                'has_premium': True,
                'has_ai_access': False,
                'has_system_design_access': False,
                'description': 'Default Premium (Unknown Product)'
            }

        return metadata

    def get_product_description(self, product_id: str) -> str:
        """Get human-readable product description."""
        metadata = self.get_product_metadata(product_id)
        return metadata.get('description', product_id)
