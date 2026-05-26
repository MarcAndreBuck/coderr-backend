from django.urls import path

from offers_app.api.views import OfferDetailItemView, OfferDetailView, OfferListView

urlpatterns = [
    path("offers/", OfferListView.as_view(), name="offers"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailItemView.as_view(),
        name="offer-detail-item",
    ),
]
