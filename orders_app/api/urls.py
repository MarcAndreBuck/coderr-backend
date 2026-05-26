from django.urls import path

from orders_app.api.views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderDetailView,
    OrderListView,
)

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]