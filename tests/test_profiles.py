from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


class ProfileTests(APITestCase):
    def test_user_can_get_profile(self):
        user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="TestPassword123!",
        )
        UserProfile.objects.create(
            user=user,
            user_type="customer",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(f"/api/profile/{user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], user.id)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["type"], "customer")

    def test_unauthenticated_user_cannot_get_profile(self):
        pass

    def test_user_can_update_own_profile(self):
        payload = {
            "first_name": "Marc",
            "last_name": "Buck",
            "location": "Hoort",
            "tel": "123456789",
            "description": "Updated profile",
            "working_hours": "9-17",
        }
        user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="TestPassword123!",
        )
        profile = UserProfile.objects.create(
            user=user,
            user_type="customer",
        )

        self.client.force_authenticate(user=user)

        response = self.client.patch(f"/api/profile/{user.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertEqual(response.data["last_name"], payload["last_name"])
        self.assertEqual(response.data["location"], payload["location"])
        self.assertEqual(response.data["tel"], payload["tel"])
        self.assertEqual(response.data["description"], payload["description"])
        self.assertEqual(
            response.data["working_hours"], payload["working_hours"])

        profile.refresh_from_db()

        self.assertEqual(profile.first_name, payload["first_name"])
        self.assertEqual(profile.last_name, payload["last_name"])
        self.assertEqual(profile.location, payload["location"])


    def test_user_cannot_update_other_profile(self):
        pass

    def test_user_can_list_business_profiles(self):
        pass

    def test_user_can_list_customer_profiles(self):
        pass
