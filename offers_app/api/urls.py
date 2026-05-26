from django.urls import path

from offers_app.api.views import OfferDetailView, OfferListView

urlpatterns = [
    path("offers/", OfferListView.as_view(), name="offers"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
]
