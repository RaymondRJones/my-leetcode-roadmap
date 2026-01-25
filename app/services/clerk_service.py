"""
Clerk API service for user management operations.
"""
import os
import requests
from typing import Optional


class ClerkService:
    """Service class for Clerk API operations."""

    BASE_URL = 'https://api.clerk.com/v1'

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize the Clerk service with API key."""
        self.secret_key = secret_key
        self._headers = None

    @property
    def headers(self) -> dict:
        """Get authorization headers for API requests."""
        if self._headers is None:
            self._headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
        return self._headers

    def is_configured(self) -> bool:
        """Check if Clerk is properly configured."""
        return bool(self.secret_key)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Find Clerk user by email address."""
        if not self.is_configured():
            return None

        try:
            resp = requests.get(
                f'{self.BASE_URL}/users',
                headers=self.headers,
                params={'email_address': email}
            )

            if resp.status_code != 200:
                return None

            response_data = resp.json()
            if isinstance(response_data, dict):
                data = response_data.get('data', [])
            else:
                data = response_data

            for user in data:
                for e in user.get('email_addresses', []):
                    if e.get('email_address') == email:
                        return user
            return None

        except Exception as e:
            print(f"Error finding Clerk user {email}: {e}")
            return None

    def create_user(self, email: str, metadata: dict) -> Optional[dict]:
        """Create new Clerk user with both private and public metadata."""
        if not self.is_configured():
            return None

        payload = {
            'email_address': [email],
            'private_metadata': metadata,
            'public_metadata': metadata,
            'skip_password_checks': True,
            'skip_password_requirement': True,
            'password': f'TempStripe{os.urandom(8).hex()}!',
        }

        try:
            resp = requests.post(
                f'{self.BASE_URL}/users',
                headers=self.headers,
                json=payload
            )

            if resp.status_code != 200:
                print(f"Failed to create Clerk user {email}: {resp.text}")
                return None

            print(f"Created Clerk user {email} from Stripe purchase")
            return resp.json()

        except Exception as e:
            print(f"Error creating Clerk user {email}: {e}")
            return None

    def update_user_metadata(self, user_id: str, metadata: dict) -> Optional[dict]:
        """Update Clerk user's private and public metadata."""
        if not self.is_configured():
            return None

        payload = {
            'private_metadata': metadata,
            'public_metadata': metadata
        }

        try:
            resp = requests.patch(
                f'{self.BASE_URL}/users/{user_id}',
                headers=self.headers,
                json=payload
            )

            if resp.status_code != 200:
                print(f"Failed to update Clerk user {user_id}: {resp.text}")
                return None

            print(f"Updated Clerk user {user_id} metadata")
            return resp.json()

        except Exception as e:
            print(f"Error updating Clerk user {user_id}: {e}")
            return None

    def provision_user(self, email: str, product_metadata: dict) -> bool:
        """Provision or update Clerk user based on product purchase."""
        # Remove description from metadata before applying
        user_metadata = {k: v for k, v in product_metadata.items() if k != 'description'}

        # Check if user exists
        user = self.get_user_by_email(email)

        if user:
            # User exists - merge metadata
            user_id = user['id']
            current_metadata = user.get('private_metadata', {})

            # Merge: new metadata takes precedence
            merged_metadata = current_metadata.copy()
            for key, value in user_metadata.items():
                if value or key not in merged_metadata:
                    merged_metadata[key] = value

            result = self.update_user_metadata(user_id, merged_metadata)
            return result is not None
        else:
            # Create new user
            result = self.create_user(email, user_metadata)
            return result is not None

    def revoke_user_access(self, email: str) -> bool:
        """Revoke all access for a user."""
        user = self.get_user_by_email(email)
        if user:
            revoked_metadata = {
                'has_premium': False,
                'has_ai_access': False,
                'has_system_design_access': False,
                'has_guides_access': False
            }
            result = self.update_user_metadata(user['id'], revoked_metadata)
            if result:
                print(f"Revoked access for {email}")
            return result is not None
        return False
