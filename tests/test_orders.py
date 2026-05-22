from rest_framework.test import APITestCase


class OrderTests(APITestCase):
    def test_user_can_list_own_orders(self):
        pass

    def test_customer_can_create_order(self):
        pass

    def test_business_cannot_create_order(self):
        pass

    def test_business_can_update_order_status(self):
        pass

    def test_customer_cannot_update_order_status(self):
        pass

    def test_staff_can_delete_order(self):
        pass

    def test_non_staff_cannot_delete_order(self):
        pass

    def test_authenticated_user_can_get_order_count(self):
        pass

    def test_authenticated_user_can_get_completed_order_count(self):
        pass