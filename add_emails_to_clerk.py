#!/usr/bin/env python3
import csv
import os
import requests

# Load Clerk API credentials (must be set in environment variables for security)
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
if not CLERK_SECRET_KEY:
    raise RuntimeError("❌ Please set the CLERK_SECRET_KEY environment variable.")

CLERK_API_URL = "https://api.clerk.com/v1"

# Metadata you want to assign
DEFAULT_METADATA = {
    "has_premium": True,
    "has_ai_access": True,
    "has_system_design_access": True,
}

HEADERS = {
    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
    "Content-Type": "application/json",
}


def find_clerk_user_by_email(email: str):
    """Find an existing Clerk user by email address."""
    resp = requests.get(
        f"{CLERK_API_URL}/users", headers=HEADERS, params={"email_address": email}
    )
    if resp.status_code != 200:
        print(f"⚠️ Error searching for user {email}: {resp.text}")
        return None

    data = resp.json().get("data", [])
    for user in data:
        for e in user.get("email_addresses", []):
            if e.get("email_address") == email:
                return user
    return None


def create_clerk_user(email: str, metadata: dict):
    """Create a new Clerk user with default metadata."""
    payload = {
        "email_address": [email],
        "public_metadata": metadata,
        "skip_password_requirements": True,
    }
    resp = requests.post(f"{CLERK_API_URL}/users", headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"⚠️ Failed to create user {email}: {resp.text}")
        return None
    print(f"✅ Created new user {email}")
    return resp.json()


def update_clerk_user_metadata(user_id: str, metadata: dict):
    """Update an existing Clerk user's metadata (merge instead of overwrite)."""
    payload = {"public_metadata": metadata}
    resp = requests.patch(
        f"{CLERK_API_URL}/users/{user_id}", headers=HEADERS, json=payload
    )
    if resp.status_code != 200:
        print(f"⚠️ Failed to update user {user_id}: {resp.text}")
        return None
    print(f"✅ Updated user {user_id}")
    return resp.json()


def provision_user(email: str, metadata: dict):
    """Ensure a user exists and has the correct metadata."""
    user = find_clerk_user_by_email(email)
    if user:
        user_id = user["id"]
        # Merge metadata with existing
        current_md = user.get("public_metadata", {})
        current_md.update(metadata)
        return update_clerk_user_metadata(user_id, current_md)
    else:
        return create_clerk_user(email, metadata)


def process_csv(csv_file: str):
    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            email = row[0].strip()
            if not email or "@" not in email:
                print(f"Skipping invalid row: {row}")
                continue
            provision_user(email, DEFAULT_METADATA)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch provision Clerk users from CSV of emails"
    )
    parser.add_argument("csv_file", help="Path to CSV file of email addresses")
    args = parser.parse_args()

    process_csv(args.csv_file)
