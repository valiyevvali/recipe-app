"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .. import models


def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample title',
            description='Sample Description.',
            time_minutes=5,
            price=Decimal('5.50')
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
