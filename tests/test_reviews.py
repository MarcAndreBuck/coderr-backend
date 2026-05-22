from rest_framework.test import APITestCase


class ReviewTests(APITestCase):
    def test_authenticated_user_can_list_reviews(self):
        pass

    def test_customer_can_create_review(self):
        pass

    def test_business_cannot_create_review(self):
        pass

    def test_customer_cannot_review_same_business_twice(self):
        pass

    def test_reviewer_can_update_own_review(self):
        pass

    def test_non_reviewer_cannot_update_review(self):
        pass

    def test_reviewer_can_delete_own_review(self):
        pass