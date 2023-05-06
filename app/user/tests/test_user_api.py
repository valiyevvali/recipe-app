"""
Tests for user API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params) -> get_user_model():
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        """Test creating user successfully."""
        payload = {
            'email': 'test1@example.com',
            'password': 'test1234@',
            'name': 'test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        user_exists = get_user_model().objects.filter(email=payload['email'],
                                                      name=payload['name']).exists()
        self.assertTrue(user_exists)

    def test_user_with_email_exists(self) -> None:
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test1@example.com',
            'password': 'test1234@',
            'name': 'test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self) -> None:
        """Test an error is returned if password is less than 5 characters."""
        payload = {
            'email': 'test1@example.com',
            'password': '1234',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']). \
            exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self) -> None:
        """Test generate token for valid credentials."""
        user_details = {
            'email': 'test1@example.com',
            'password': 'test1234@',
            'name': 'test name'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_email(self) -> None:
        """Test an error is returned if email is invalid"""
        user_details = {
            'email': 'test1@example.com',
            'password': 'test1234@',
        }
        create_user(**user_details)
        payload = {
            'email': "bademmail@test.com",
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_wrong_password(self) -> None:
        """Test an error is returned if password is wrong"""
        user_details = {
            'email': 'test1@example.com',
            'password': 'test1234@',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_blank_password(self) -> None:
        payload = {
            'email': 'test@example.com',
            'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self) -> None:
        """Test authentication is required for profile info."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication."""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            name='Test user',
            password='test1234@'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_user_info_success(self) -> None:
        """Test retrieve profile info for authenticated user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self) -> None:
        """Test `POST` method not allowed for `me` endpoint."""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for the authenticated user."""
        payload = {
            'email': 'user2@example.com',
            'password': 'newpassword123',
            'name': 'new name'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['email'])
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
