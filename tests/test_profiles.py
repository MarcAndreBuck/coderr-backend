from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class ProfileTests(APITestCase):
    def test_user_can_get_profile(self):
        user = User.objects.create_user(
            username="costumer_user",
            email="costumer_user@example.com",
            password="TestPassword123"
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(f"/api/profile/{user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_unauthenticated_user_cannot_get_profile(self):
        pass

    def test_user_can_update_own_profile(self):
        pass

    def test_user_cannot_update_other_profile(self):
        pass

    def test_user_can_list_business_profiles(self):
        pass

    def test_user_can_list_customer_profiles(self):
        pass