from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


class OrderTests(APITestCase):
    def create_user_with_profile(self, user_type="customer"):
        user_count = User.objects.count()
        user = User.objects.create_user(
            username=f"{user_type}_user_{user_count}",
            email=f"{user_type}_{user_count}@example.com",
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
                    "features": ["Logo Design", "Business Card"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Business Card", "Flyer"],
                    "offer_type": "premium",
                },
            ],
        }

    def create_offer_detail(self):
        business_user = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business_user)

        response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        return response.data["details"][0]["id"]

    def test_user_can_list_own_orders(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_create_order(self):
        offer_detail_id = self.create_offer_detail()
        customer_user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=customer_user)

        response = self.client.post(
            "/api/orders/",
            {"offer_detail_id": offer_detail_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer_user"], customer_user.id)

    def test_business_cannot_create_order(self):
        offer_detail_id = self.create_offer_detail()
        business_user = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business_user)

        response = self.client.post(
            "/api/orders/",
            {"offer_detail_id": offer_detail_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_can_update_order_status(self):
        order_id = self.create_order_for_business()

        response = self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_customer_cannot_update_order_status(self):
        order_id = self.create_order_for_business()
        customer_user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=customer_user)

        response = self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_delete_order(self):
        order_id = self.create_order_for_business()
        staff_user = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="TestPassword123!",
            is_staff=True,
        )
        self.client.force_authenticate(user=staff_user)

        response = self.client.delete(f"/api/orders/{order_id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cannot_delete_order(self):
        order_id = self.create_order_for_business()
        business_user = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business_user)

        response = self.client.delete(f"/api/orders/{order_id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_get_order_count(self):
        business_user = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business_user)

        response = self.client.get(f"/api/order-count/{business_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("order_count", response.data)

    def test_authenticated_user_can_get_completed_order_count(self):
        business_user = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business_user)

        response = self.client.get(
            f"/api/completed-order-count/{business_user.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("completed_order_count", response.data)


    def create_order_for_business(self):
        business_user = self.create_user_with_profile("business")

        self.client.force_authenticate(user=business_user)

        offer_response = self.client.post(
            "/api/offers/",
            self.get_offer_payload(),
            format="json",
        )

        offer_detail_id = offer_response.data["details"][0]["id"]

        customer_user = self.create_user_with_profile("customer")

        self.client.force_authenticate(user=customer_user)

        order_response = self.client.post(
            "/api/orders/",
            {"offer_detail_id": offer_detail_id},
            format="json",
        )

        self.client.force_authenticate(user=business_user)

        return order_response.data["id"]