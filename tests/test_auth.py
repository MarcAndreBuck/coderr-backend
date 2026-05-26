from auth_app.models import UserProfile
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    """
    Test cases for authentication endpoints.
    """
    def get_registration_payload(self, user_type="customer"):
        """
        Return registration payload for given user type.
        """
        return {
            "username": f"{user_type}_user",
            "email": f"{user_type}@example.com",
            "password": "TestPassword123!",
            "repeated_password": "TestPassword123!",
            "type": user_type,
        }

    def register_user(self, payload=None):
        """
        Register a user via API and return response.
        """
        return self.client.post(
            "/api/registration/",
            payload or self.get_registration_payload(),
            format="json",
        )

    def test_customer_can_register(self):
        response = self.register_user()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "customer_user")
        self.assertEqual(response.data["email"], "customer@example.com")
        self.assertIn("user_id", response.data)

    def test_business_can_register(self):
        response = self.register_user(
            self.get_registration_payload("business"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "business_user")
        self.assertEqual(response.data["email"], "business@example.com")
        self.assertIn("user_id", response.data)

    def test_user_can_login(self):
        self.register_user()
        response = self.client.post(
            "/api/login/",
            {"username": "customer_user", "password": "TestPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "customer_user")
        self.assertEqual(response.data["email"], "customer@example.com")
        self.assertIn("user_id", response.data)

    def test_user_cannot_register_with_different_passwords(self):
        payload = self.get_registration_payload()
        payload["repeated_password"] = "DifferentPassword123!"

        response = self.register_user(payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_login_with_wrong_password(self):
        self.register_user()
        response = self.client.post(
            "/api/login/",
            {"username": "customer_user", "password": "WrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_creates_user_profile(self):
        response = self.register_user()
        user_id = response.data["user_id"]

        profile = UserProfile.objects.get(user_id=user_id)

        self.assertEqual(profile.user_type, "customer")
