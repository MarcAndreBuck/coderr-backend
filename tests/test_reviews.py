from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from orders_app.models import Order


class ReviewTests(APITestCase):

    def create_completed_order(self, customer, business):
        return Order.objects.create(
            customer_user=customer,
            business_user=business,
            title="Website Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design"],
            offer_type="basic",
            status="completed",
        )

    def create_user_with_profile(self, user_type="customer"):
        user_count = User.objects.count()
        user = User.objects.create_user(
            username=f"{user_type}_user_{user_count}",
            email=f"{user_type}_{user_count}@example.com",
            password="TestPassword123!",
        )
        UserProfile.objects.create(user=user, user_type=user_type)
        return user

    def get_review_payload(self, business_user):
        return {
            "business_user": business_user.id,
            "rating": 5,
            "description": "Great work!",
        }

    def test_authenticated_user_can_list_reviews(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/reviews/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_create_review(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")
        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Great work!")

    def test_business_cannot_create_review(self):
        business = self.create_user_with_profile("business")
        other_business = self.create_user_with_profile("business")
        self.client.force_authenticate(user=business)

        response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(other_business),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_review_same_business_twice(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviewer_can_update_own_review(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        create_response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        review_id = create_response.data["id"]

        response = self.client.patch(
            f"/api/reviews/{review_id}/",
            {"rating": 4, "description": "Updated review"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)

    def test_non_reviewer_cannot_update_review(self):
        customer = self.create_user_with_profile("customer")
        other_customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        create_response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        review_id = create_response.data["id"]

        self.client.force_authenticate(user=other_customer)

        response = self.client.patch(
            f"/api/reviews/{review_id}/",
            {"rating": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_can_delete_own_review(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        create_response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        review_id = create_response.data["id"]

        response = self.client.delete(
            f"/api/reviews/{review_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_customer_cannot_review_without_completed_order(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.client.force_authenticate(user=customer)

        response = self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews_can_be_filtered_by_business_user(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        response = self.client.get(
            f"/api/reviews/?business_user_id={business.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviews_can_be_filtered_by_reviewer(self):
        customer = self.create_user_with_profile("customer")
        business = self.create_user_with_profile("business")

        self.create_completed_order(customer, business)

        self.client.force_authenticate(user=customer)

        self.client.post(
            "/api/reviews/",
            self.get_review_payload(business),
            format="json",
        )

        response = self.client.get(
            f"/api/reviews/?reviewer_id={customer.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviews_can_be_ordered_by_rating(self):
        user = self.create_user_with_profile("customer")
        self.client.force_authenticate(user=user)

        response = self.client.get(
            "/api/reviews/?ordering=rating"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
