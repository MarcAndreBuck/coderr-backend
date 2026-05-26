from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


class OfferTests(APITestCase):

    def create_user_with_profile(self, user_type="business"):
        user = User.objects.create_user(
            username=f"{user_type}_user_{User.objects.count()}",
            email=f"{user_type}_{User.objects.count()}@example.com",
            password="TestPassword123!",
        )

        UserProfile.objects.create(
            user=user,
            user_type=user_type,
        )

        return user

    def get_offer_payload(self):
        return {
            "title": "Website Design",
            "image": None,
            "description": "Professional website design.",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": [
                        "Logo Design",
                        "Business Card",
                    ],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": [
                        "Logo Design",
                        "Business Card",
                        "Flyer",
                    ],
                    "offer_type": "premium",
                },
            ],
        }

    def create_offer(self, user):
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        return response

    def test_anyone_can_list_offers(self):
        response = self.client.get("/api/offers/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_anyone_can_get_offer_detail(self):
        owner = self.create_user_with_profile("business")

        create_response = self.create_offer(owner)

        offer_id = create_response.data["id"]

        response = self.client.get(
            f"/api/offers/{offer_id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_business_user_can_create_offer(self):
        user = self.create_user_with_profile("business")

        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        print(response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_customer_cannot_create_offer(self):
        user = self.create_user_with_profile("customer")

        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_update_offer(self):
        owner = self.create_user_with_profile("business")

        create_response = self.create_offer(owner)

        offer_id = create_response.data["id"]

        payload = {
            "title": "Updated Website Design",
        }

        response = self.client.patch(
            f"/api/offers/{offer_id}/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["title"],
            payload["title"],
        )

    def test_owner_can_delete_offer(self):
        owner = self.create_user_with_profile("business")

        create_response = self.create_offer(owner)

        offer_id = create_response.data["id"]

        response = self.client.delete(
            f"/api/offers/{offer_id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_user_cannot_update_other_offer(self):
        owner = self.create_user_with_profile("business")

        create_response = self.create_offer(owner)

        offer_id = create_response.data["id"]

        other_user = self.create_user_with_profile("business")

        self.client.force_authenticate(user=other_user)

        response = self.client.patch(
            f"/api/offers/{offer_id}/",
            {"title": "Hacked Offer"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_cannot_delete_other_offer(self):
        owner = self.create_user_with_profile("business")

        create_response = self.create_offer(owner)

        offer_id = create_response.data["id"]

        other_user = self.create_user_with_profile("business")

        self.client.force_authenticate(user=other_user)

        response = self.client.delete(
            f"/api/offers/{offer_id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_create_offer(self):
        response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
