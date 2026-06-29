from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountRenderTests(TestCase):
    def test_register_and_login_pages_render(self):
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)

    def test_login_redirects_staff_to_dashboard(self):
        User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="strong-pass-123",
            is_staff=True,
        )

        response = self.client.post(reverse("login"), {
            "username": "manager",
            "password": "strong-pass-123",
        })

        self.assertRedirects(response, reverse("manager_dashboard"))
