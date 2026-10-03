from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class RegisterTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        url = reverse("accounts:register")
        payload = {
            "email": "user@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="user@example.com").exists())
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(email="dupe@example.com", password="StrongPass123!")
        url = reverse("accounts:register")
        payload = {
            "email": "dupe@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_mismatched_passwords(self):
        url = reverse("accounts:register")
        payload = {
            "email": "user2@example.com",
            "password": "StrongPass123!",
            "password_confirm": "Different123!",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com", password="StrongPass123!"
        )

    def test_login_with_correct_credentials(self):
        url = reverse("accounts:login")
        response = self.client.post(
            url, {"email": "login@example.com", "password": "StrongPass123!"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["tokens"])

    def test_login_with_wrong_password(self):
        url = reverse("accounts:login")
        response = self.client.post(
            url, {"email": "login@example.com", "password": "WrongPassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save()
        url = reverse("accounts:login")
        response = self.client.post(
            url, {"email": "login@example.com", "password": "StrongPass123!"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="me@example.com", password="StrongPass123!", first_name="Grace"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_me_returns_current_user(self):
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")

    def test_patch_me_updates_profile(self):
        response = self.client.patch(reverse("accounts:me"), {"first_name": "Hopper"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Hopper")

    def test_me_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAndRefreshTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="logout@example.com", password="StrongPass123!"
        )
        login = self.client.post(
            reverse("accounts:login"),
            {"email": "logout@example.com", "password": "StrongPass123!"},
        )
        self.tokens = login.data["tokens"]

    def test_refresh_returns_new_access_token(self):
        response = self.client.post(
            reverse("accounts:refresh"), {"refresh": self.tokens["refresh"]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_blacklists_refresh_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("accounts:logout"), {"refresh": self.tokens["refresh"]}
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # the same refresh token can no longer be used
        retry = self.client.post(
            reverse("accounts:refresh"), {"refresh": self.tokens["refresh"]}
        )
        self.assertEqual(retry.status_code, status.HTTP_401_UNAUTHORIZED)