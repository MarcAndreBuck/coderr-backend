from django.urls import path

from reviews_app.api.views import (
    ReviewDetailView,
    ReviewListView,
)

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="reviews"),
    path(
        "reviews/<int:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail",
    ),
]