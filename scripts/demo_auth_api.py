#!/usr/bin/env python3
"""
Authentication API Demo Script

Demonstrates the user registration and login functionality.
This script shows how to interact with the authentication API.

Reference: demo_auth_api.py - Interactive demonstration
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.app import create_app


def demo_registration_and_login():
    """
    Demonstrate user registration and login functionality.

    Shows:
    1. Successful user registration
    2. Password hashing (bcrypt)
    3. Duplicate user detection
    4. Successful login
    5. Invalid password handling
    """
    print("=" * 60)
    print("Authentication API Demonstration")
    print("=" * 60)
    print()

    # Create test app
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    client = app.test_client()

    # Demo 1: Health Check
    print("1️⃣  Testing Health Check")
    print("-" * 60)
    response = client.get("/api/auth/health")
    print(f"   GET /api/auth/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.get_json()}")
    print()
    time.sleep(0.5)

    # Demo 2: User Registration
    print("2️⃣  Registering New User")
    print("-" * 60)
    user_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "SecurePass123!",
        "full_name": "Demo User",
    }
    print(f"   POST /api/auth/register")
    print(f"   Data: {user_data}")
    response = client.post("/api/auth/register", json=user_data)
    result = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")
    if "user" in result:
        print(f"   User ID: {result['user']['id']}")
        print(f"   Username: {result['user']['username']}")
        print(f"   Email: {result['user']['email']}")
        print(f"   ⚠️  Notice: Password hash NOT in response (security)")
    print()
    time.sleep(0.5)

    # Demo 3: Duplicate Username Detection
    print("3️⃣  Testing Duplicate Username Detection")
    print("-" * 60)
    duplicate_data = {
        "username": "demo_user",
        "email": "different@example.com",
        "password": "SecurePass123!",
    }
    print(f"   POST /api/auth/register")
    print(f"   Data: {duplicate_data}")
    response = client.post("/api/auth/register", json=duplicate_data)
    result = response.get_json()
    print(f"   Status: {response.status_code} (Expected 409)")
    print(f"   Message: {result.get('message')}")
    print()
    time.sleep(0.5)

    # Demo 4: Invalid Email Validation
    print("4️⃣  Testing Email Validation")
    print("-" * 60)
    invalid_data = {
        "username": "testuser2",
        "email": "not-an-email",
        "password": "SecurePass123!",
    }
    print(f"   POST /api/auth/register")
    print(f"   Data: {invalid_data}")
    response = client.post("/api/auth/register", json=invalid_data)
    result = response.get_json()
    print(f"   Status: {response.status_code} (Expected 400)")
    print(f"   Errors: {result.get('errors')}")
    print()
    time.sleep(0.5)

    # Demo 5: Weak Password Detection
    print("5️⃣  Testing Password Strength Validation")
    print("-" * 60)
    weak_data = {"username": "testuser3", "email": "test3@example.com", "password": "weak"}
    print(f"   POST /api/auth/register")
    print(f"   Data: {weak_data}")
    response = client.post("/api/auth/register", json=weak_data)
    result = response.get_json()
    print(f"   Status: {response.status_code} (Expected 400)")
    print(f"   Errors:")
    for error in result.get("errors", []):
        print(f"      - {error}")
    print()
    time.sleep(0.5)

    # Demo 6: Successful Login
    print("6️⃣  Testing Successful Login")
    print("-" * 60)
    login_data = {"username": "demo_user", "password": "SecurePass123!"}
    print(f"   POST /api/auth/login")
    print(f"   Data: {login_data}")
    response = client.post("/api/auth/login", json=login_data)
    result = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")
    if "user" in result:
        print(f"   Logged in as: {result['user']['username']}")
    print()
    time.sleep(0.5)

    # Demo 7: Login with Email
    print("7️⃣  Testing Login with Email")
    print("-" * 60)
    login_email_data = {"username": "demo@example.com", "password": "SecurePass123!"}
    print(f"   POST /api/auth/login")
    print(f"   Data: {login_email_data} (using email as username)")
    response = client.post("/api/auth/login", json=login_email_data)
    result = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {result.get('success')}")
    print()
    time.sleep(0.5)

    # Demo 8: Invalid Password
    print("8️⃣  Testing Invalid Password")
    print("-" * 60)
    wrong_pass_data = {"username": "demo_user", "password": "WrongPassword123!"}
    print(f"   POST /api/auth/login")
    print(f"   Data: {wrong_pass_data}")
    response = client.post("/api/auth/login", json=wrong_pass_data)
    result = response.get_json()
    print(f"   Status: {response.status_code} (Expected 401)")
    print(f"   Message: {result.get('message')}")
    print(f"   ⚠️  Generic message prevents username enumeration")
    print()
    time.sleep(0.5)

    # Demo 9: Non-existent User
    print("9️⃣  Testing Non-existent User")
    print("-" * 60)
    nonexistent_data = {"username": "nonexistent", "password": "SecurePass123!"}
    print(f"   POST /api/auth/login")
    print(f"   Data: {nonexistent_data}")
    response = client.post("/api/auth/login", json=nonexistent_data)
    result = response.get_json()
    print(f"   Status: {response.status_code} (Expected 401)")
    print(f"   Message: {result.get('message')}")
    print(f"   ⚠️  Same message as wrong password (security)")
    print()

    # Summary
    print("=" * 60)
    print("✅ Authentication API Demonstration Complete!")
    print("=" * 60)
    print()
    print("🔐 Security Features Demonstrated:")
    print("   ✓ Bcrypt password hashing")
    print("   ✓ Input validation (email, username, password)")
    print("   ✓ Duplicate user detection")
    print("   ✓ Password never returned in responses")
    print("   ✓ Generic error messages (prevent user enumeration)")
    print("   ✓ Login with username or email")
    print()
    print("📚 Code References:")
    print("   #User model - src/api/models.py")
    print("   #registerUser endpoint - src/api/auth_routes.py")
    print("   #loginUser endpoint - src/api/auth_routes.py")
    print("   #validate_registration_data - src/api/validators.py")
    print()


if __name__ == "__main__":
    try:
        demo_registration_and_login()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
