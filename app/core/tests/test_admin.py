"""
Test for Django admin modifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="pass1234"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            name="Test user",
            email="user@example.com",
            password="pass1234"
        )

    def test_users_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
