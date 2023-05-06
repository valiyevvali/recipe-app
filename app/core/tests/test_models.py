"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModels(TestCase):
    """Testing models."""

    def test_create_user_with_email_successfully(self):
        """Test creating a user with email is successful. """
        email = "test@example.com"
        password = "test123"

        user = get_user_model().objects.create_user(email=email,
                                                    password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user."""
        sample_emails = [
            ["test@Example.com", "test@example.com"],
            ["Test1@example.com", "Test1@example.com"],
            ["test2@example.COM", "test2@example.com"]
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email,
                                                        password="sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Testing that creating a new user without email raises
           a ValueError.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="",
                                                 password="sample123")

    def test_create_superuser(self):
        """Testing creating superuser."""
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="sample123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)