"""
Input Validation Utilities for User Authentication

Provides validation functions for user registration data including
email format validation and password strength requirements.

Reference: #validators.py - Input validation and security checks
"""

import re
from typing import Dict, List, Optional


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])

    Reference: #validate_email - Email format validation
    """
    if not email:
        return False, "Email is required"

    # RFC 5322 compliant email regex (simplified but secure)
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    if len(email) > 120:
        return False, "Email must be less than 120 characters"

    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format and length.

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])

    Requirements:
        - 3-50 characters
        - Alphanumeric, underscore, hyphen only
        - Must start with letter or number

    Reference: #validate_username - Username format validation
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 50:
        return False, "Username must be less than 50 characters"

    # Username must start with alphanumeric and contain only alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", username):
        return False, "Username must start with letter/number and contain only letters, numbers, underscores, and hyphens"

    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength and requirements.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])

    Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Reference: #validate_password - Password strength validation
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Check for uppercase
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    # Check for lowercase
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    # Check for digit
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    # Check for special character
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_registration_data(username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict:
    """
    Validate all registration data fields.

    Args:
        username: Username to register
        email: Email address
        password: Password
        full_name: Optional full name

    Returns:
        Dictionary with:
            - valid: bool (True if all validations pass)
            - errors: List[str] (list of error messages)

    Reference: #validate_registration_data - Complete registration validation
    """
    errors = []

    # Validate username
    username_valid, username_error = validate_username(username)
    if not username_valid:
        errors.append(username_error)

    # Validate email
    email_valid, email_error = validate_email(email)
    if not email_valid:
        errors.append(email_error)

    # Validate password
    password_valid, password_error = validate_password(password)
    if not password_valid:
        errors.append(password_error)

    # Validate optional full_name
    if full_name and len(full_name) > 100:
        errors.append("Full name must be less than 100 characters")

    return {"valid": len(errors) == 0, "errors": errors}
