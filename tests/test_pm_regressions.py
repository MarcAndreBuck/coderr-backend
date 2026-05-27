from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail


class PMRegressionTests(APITestCase):
    def create_user_with_profile(self, user_type="customer"):
        user_count = User.objects.count()
        user = User.objects.create_user(
            username=f"{user_type}_user_{user_count}",
            email=f"{user_type}_{user_count}@example.com",
            password="TestPassword123!",
        )
        UserProfile.objects.create(user=user, user_type=user_type)

        return user

    def create_offer_with_detail(self):
        business_user = self.create_user_with_profile("business")
        offer = Offer.objects.create(
            user=business_user,
            title="Website Design",
            description="Professional website design.",
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design"],
            offer_type="basic",
        )

        return business_user, offer, detail

    def test_profile_patch_updates_email(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            f"/api/profile/{user.id}/",
            {"email": "updated@example.com"},
            format="json",
        )

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updated@example.com")
        self.assertEqual(user.email, "updated@example.com")

    def test_profile_get_requires_authentication(self):
        user = self.create_user_with_profile("customer")

        response = self.client.get(f"/api/profile/{user.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_detail_requires_authentication_before_404(self):
        response = self.client.get("/api/offers/999999/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_invalid_delivery_time_filter_returns_400(self):
        response = self.client.get(
            "/api/offers/?max_delivery_time=invalid"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_offer_invalid_min_price_filter_returns_400(self):
        response = self.client.get("/api/offers/?min_price=invalid")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_offer_patch_forbidden_returns_json(self):
        _, offer, _ = self.create_offer_with_detail()
        other_business = self.create_user_with_profile("business")

        self.client.force_authenticate(user=other_business)

        response = self.client.patch(
            f"/api/offers/{offer.id}/",
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_offer_patch_invalid_data_returns_json_400(self):
        business_user, offer, _ = self.create_offer_with_detail()

        self.client.force_authenticate(user=business_user)

        response = self.client.patch(
            f"/api/offers/{offer.id}/",
            {"details": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_order_post_missing_offer_detail_id_returns_json_400(self):
        customer = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=customer)

        response = self.client.post(
            "/api/orders/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_order_count_missing_business_user_returns_404(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/order-count/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_missing_business_user_returns_404(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.get(
            "/api/completed-order-count/999999/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
