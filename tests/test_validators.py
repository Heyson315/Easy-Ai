"""
Unit Tests for Input Validators

Tests email validation, username validation, and password strength requirements.

Reference: test_validators.py - Validation logic tests
"""

import unittest

from src.api.validators import (
    validate_email,
    validate_password,
    validate_registration_data,
    validate_username,
)


class TestValidators(unittest.TestCase):
    """
    Test suite for input validation functions.

    Reference: #TestValidators - Validation utilities test class
    """

    def test_validate_email_valid(self):
        """Test valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user_name@example-domain.com",
        ]

        for email in valid_emails:
            valid, error = validate_email(email)
            self.assertTrue(valid, f"Email '{email}' should be valid")
            self.assertIsNone(error)

    def test_validate_email_invalid(self):
        """Test invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            "",
        ]

        for email in invalid_emails:
            valid, error = validate_email(email)
            self.assertFalse(valid, f"Email '{email}' should be invalid")
            self.assertIsNotNone(error)

    def test_validate_email_too_long(self):
        """Test email length validation."""
        long_email = "a" * 110 + "@example.com"
        valid, error = validate_email(long_email)
        self.assertFalse(valid)
        self.assertIn("less than 120 characters", error)

    def test_validate_username_valid(self):
        """Test valid username formats."""
        valid_usernames = [
            "user123",
            "test_user",
            "user-name",
            "abc",
            "Username123",
            "a1b2c3",
        ]

        for username in valid_usernames:
            valid, error = validate_username(username)
            self.assertTrue(valid, f"Username '{username}' should be valid")
            self.assertIsNone(error)

    def test_validate_username_invalid(self):
        """Test invalid username formats."""
        invalid_usernames = [
            "",
            "ab",  # Too short
            "_underscore",  # Cannot start with underscore
            "-hyphen",  # Cannot start with hyphen
            "user name",  # Contains space
            "user@name",  # Invalid character
        ]

        for username in invalid_usernames:
            valid, error = validate_username(username)
            self.assertFalse(valid, f"Username '{username}' should be invalid")
            self.assertIsNotNone(error)

    def test_validate_username_length(self):
        """Test username length validation."""
        # Too short
        valid, error = validate_username("ab")
        self.assertFalse(valid)
        self.assertIn("at least 3 characters", error)

        # Too long
        long_username = "a" * 51
        valid, error = validate_username(long_username)
        self.assertFalse(valid)
        self.assertIn("less than 50 characters", error)

    def test_validate_password_valid(self):
        """Test valid password formats."""
        valid_passwords = [
            "SecurePass123!",
            "Abcd1234!@#$",
            "P@ssw0rd123",
            "MyP@ss123word",
        ]

        for password in valid_passwords:
            valid, error = validate_password(password)
            self.assertTrue(valid, f"Password '{password}' should be valid")
            self.assertIsNone(error)

    def test_validate_password_too_short(self):
        """Test password minimum length."""
        short_password = "Abc1!"
        valid, error = validate_password(short_password)
        self.assertFalse(valid)
        self.assertIn("at least 8 characters", error)

    def test_validate_password_no_uppercase(self):
        """Test password uppercase requirement."""
        password = "lowercase123!"
        valid, error = validate_password(password)
        self.assertFalse(valid)
        self.assertIn("uppercase letter", error)

    def test_validate_password_no_lowercase(self):
        """Test password lowercase requirement."""
        password = "UPPERCASE123!"
        valid, error = validate_password(password)
        self.assertFalse(valid)
        self.assertIn("lowercase letter", error)

    def test_validate_password_no_digit(self):
        """Test password digit requirement."""
        password = "NoDigitsHere!"
        valid, error = validate_password(password)
        self.assertFalse(valid)
        self.assertIn("digit", error)

    def test_validate_password_no_special_char(self):
        """Test password special character requirement."""
        password = "NoSpecialChar123"
        valid, error = validate_password(password)
        self.assertFalse(valid)
        self.assertIn("special character", error)

    def test_validate_password_too_long(self):
        """Test password maximum length."""
        long_password = "A1!" + "a" * 130
        valid, error = validate_password(long_password)
        self.assertFalse(valid)
        self.assertIn("less than 128 characters", error)

    def test_validate_registration_data_success(self):
        """Test complete registration validation with valid data."""
        result = validate_registration_data(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User",
        )

        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_registration_data_multiple_errors(self):
        """Test registration validation with multiple errors."""
        result = validate_registration_data(
            username="ab",  # Too short
            email="invalid-email",  # Invalid format
            password="weak",  # Weak password
            full_name="A" * 101,  # Too long
        )

        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 3)  # Should have multiple errors

    def test_validate_registration_data_optional_fullname(self):
        """Test registration validation with optional full_name."""
        # Without full_name
        result = validate_registration_data(
            username="testuser", email="test@example.com", password="SecurePass123!", full_name=None
        )

        self.assertTrue(result["valid"])

        # With empty full_name
        result = validate_registration_data(
            username="testuser", email="test@example.com", password="SecurePass123!", full_name=""
        )

        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
