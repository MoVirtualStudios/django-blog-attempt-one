from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Profile


User = get_user_model()


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ]
)
class AccountPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass12345",
        )

        Profile.objects.get_or_create(
            user=self.user,
        )

    def test_login_page_loads(self):
        response = self.client.get(
            reverse("accounts:login"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_register_page_loads(self):
        response = self.client.get(
            reverse("accounts:register"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_password_reset_page_loads(self):
        response = self.client.get(
            reverse("accounts:password_reset"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse("accounts:dashboard"),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "/accounts/login/",
            response["Location"],
        )

    def test_dashboard_loads_for_logged_in_user(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            reverse("accounts:dashboard"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )