from rest_framework import status
from rest_framework.test import APITestCase


class BaseInfoTests(APITestCase):
    def test_anyone_can_get_base_info(self):
        response = self.client.get("/api/base-info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("review_count", response.data)
        self.assertIn("average_rating", response.data)
        self.assertIn("business_profile_count", response.data)
        self.assertIn("offer_count", response.data)