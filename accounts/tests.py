from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="StrongPass123!",
            first_name="User",
            last_name="Test",
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@test.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_login_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@test.com",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertIn(response.status_code, [400, 401])