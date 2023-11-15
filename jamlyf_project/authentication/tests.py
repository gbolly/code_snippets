from urllib.parse import urlparse, parse_qs

from django.core import mail
from django.urls import reverse

from rest_framework.test import APITestCase

from .factory import UserFactory
from .constants import JAMLYF_INCORRECT_CREDENTIALS_MESSAGE

from social.tests.strategy import TestStrategy
from social.storage.base import BaseStorage
from social.tests.models import User

from .pipelines import exchange_token


class UserSignupTests(APITestCase):
    def setUp(self):
        self.user_data_sample = {
            "first_name": "Test",
            "last_name": "User",
            "password": "a1b2c3d4e5f6",
            "phone_no": "08010007822",
            "email": "test_user@sample.com",
            "country": "Canada"
        }
        self.url = reverse("user-signup")

    def test_user_signup_ok(self):
        response = self.client.post(
            self.url, self.user_data_sample, format='json'
        )
        self.assertEqual(response.status_code, 201)

        response_data = response.data
        self.assertIsNotNone(response_data["access_token"])
        self.assertIsNotNone(response_data["user"])

    def test_user_signup_existing_email_returns_error(self):
        self.test_user_signup_ok()
        response = self.client.post(
            self.url, self.user_data_sample, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_user_signup_short_password_returns_error(self):
        user_data_sample = {
            **self.user_data_sample,
            "password": "a1b2",
        }
        response = self.client.post(
            self.url, user_data_sample, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["password"])

    def test_user_signup_numeric_password_returns_error(self):
        user_data_sample = {
            **self.user_data_sample,
            "password": "123456",
        }
        response = self.client.post(
            self.url, user_data_sample, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["password"])


class CustomPipeLineTest(APITestCase):
    def setUp(self):
        self.strategy = TestStrategy(BaseStorage)
        self.user = User(username='testing')

    def test_exchange_token_active_user(self):
        result = exchange_token(self.strategy, self.user)
        q = parse_qs(urlparse(result.url).query)
        self.assertIsNotNone(q["access_token"])
        self.assertIsNotNone(q["refresh_token"])

    def test_exchange_token_inactive_user(self):
        self.user.set_active(False)
        result = exchange_token(self.strategy, self.user)
        q = parse_qs(urlparse(result.url).query)
        self.assertEqual(q, {})


class UserLoginTests(APITestCase):
    def setUp(self):
        self.url = reverse("user-login")

    def test_user_login_ok(self):
        user = UserFactory()
        response = self.client.post(
            self.url,
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.data
        self.assertIsNotNone(response_data["access_token"])
        self.assertIsNotNone(response_data["user"])
        self.assertEqual(response_data["user"]["email"], user.email)

    def test_user_login_incorrect_password_returns_error(self):
        user = UserFactory()

        response = self.client.post(
            self.url,
            {"email": user.email, "password": "a1b2c3"},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data.get("detail"), JAMLYF_INCORRECT_CREDENTIALS_MESSAGE
        )

    def test_user_login_nonexisting_email_returns_error(self):
        response = self.client.post(
            self.url,
            {"email": "random@sample.com", "password": "a1b2c3d4e5f6"},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data.get("detail"), JAMLYF_INCORRECT_CREDENTIALS_MESSAGE
        )


class UserUpdateTests(APITestCase):
    def setUp(self):
        self.url = reverse("user-update")

    def test_user_update_success(self):
        user = UserFactory()
        login_response = self.client.post(
            reverse("user-login"),
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )
        access_token = login_response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(
            self.url, {"first_name": "test-update"}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.data
        self.assertIsNotNone(response_data["user"])
        self.assertEqual(response_data["user"]["first_name"], "test-update")

    def test_user_update_password_error(self):
        user = UserFactory()
        login_response = self.client.post(
            reverse("user-login"),
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )
        access_token = login_response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(
            self.url, {"password": "test-update"}, format='json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data.get("detail"), "Password field cannot be modified"
        )


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.reset_url = reverse("reset-password")

    def test_reset_non_existing_email(self):
        response = self.client.post(
            self.reset_url,
            {"email": "does_not_exist@test.com"},
            format='json'
        )
        self.assertIsNotNone(response.data["message"])
        self.assertEqual(response.status_code, 200)

    def test_reset_existing_email(self):
        user = UserFactory()
        self.client.post(
            reverse("user-login"),
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )

        response = self.client.post(
            self.reset_url, {"email": user.email}, format='json'
        )
        self.assertIsNotNone(response.data["message"])
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "JamLfy Account Password Reset")
        self.assertEqual(mail.outbox[0].from_email, "info@jamlyf.com")
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertIsNotNone(mail.outbox[0].body)


class PasswordModifyTests(APITestCase):
    def setUp(self):
        self.url = reverse("password-change")

    def test_password_modify_success(self):
        user = UserFactory()
        login_response = self.client.post(
            reverse("user-login"),
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )

        access_token = login_response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.put(
            self.url,
            {"current_password": "a1b2c3d4e5f6", "new_password": "new-password"},
            format='json'
        )
        self.assertEqual(response.status_code, 204)

    def test_password_modify_failure(self):
        user = UserFactory()
        login_response = self.client.post(
            reverse("user-login"),
            {"email": user.email, "password": "a1b2c3d4e5f6"},
            format='json'
        )

        access_token = login_response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.put(
            self.url,
            {"current_password": "wrong-current", "new_password": "new-password"},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["current_password"])
