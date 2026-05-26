from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from offers_app.api.permissions import IsBusinessUserOrReadOnly
from offers_app.api.serializers import OfferDetailSerializer, OfferSerializer
from offers_app.models import Offer, OfferDetail


class OfferListView(APIView):
    """
    API view for listing and creating offers.
    GET returns offers, POST creates a new offer.
    """
    permission_classes = [IsBusinessUserOrReadOnly]

    def get(self, request):
        """
        Return a paginated list of offers, optionally filtered.
        """
        offers = self.get_filtered_offers(request)
        page = self.paginate_offers(request, offers)

        serializer = OfferSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return self.get_paginated_response(request, offers, serializer.data)

    def post(self, request):
        """
        Create a new offer for the authenticated business user.
        """
        serializer = OfferSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_filtered_offers(self, request):
        """
        Return offers filtered by creator, search, ordering, min price, and max delivery time.
        """
        offers = Offer.objects.all()

        creator_id = request.query_params.get("creator_id")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")

        if creator_id:
            offers = offers.filter(user_id=creator_id)

        if search:
            offers = offers.filter(
                title__icontains=search,
            ) | offers.filter(
                description__icontains=search,
            )

        offers = self.filter_by_min_price(request, offers)
        offers = self.filter_by_max_delivery_time(request, offers)

        if ordering == "updated_at":
            offers = offers.order_by("updated_at")

        if ordering == "-updated_at":
            offers = offers.order_by("-updated_at")

        return offers.distinct()

    def filter_by_min_price(self, request, offers):
        """
        Filter offers by minimum price if provided in query params.
        """
        min_price = request.query_params.get("min_price")

        if not min_price:
            return offers

        return offers.filter(details__price__gte=min_price)

    def filter_by_max_delivery_time(self, request, offers):
        """
        Filter offers by maximum delivery time if provided in query params.
        """
        max_delivery_time = request.query_params.get("max_delivery_time")

        if not max_delivery_time:
            return offers

        return offers.filter(
            details__delivery_time_in_days__lte=max_delivery_time,
        )

    def paginate_offers(self, request, offers):
        page_size = int(request.query_params.get("page_size", 6))
        page_number = int(request.query_params.get("page", 1))
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        return offers[start_index:end_index]

    def get_paginated_response(self, request, offers, results):
        page_size = int(request.query_params.get("page_size", 6))
        page_number = int(request.query_params.get("page", 1))
        total_count = offers.count()

        return Response(
            {
                "count": total_count,
                "next": self.get_next_url(request, page_number, page_size, total_count),
                "previous": self.get_previous_url(request, page_number),
                "results": results,
            }
        )

    def get_next_url(self, request, page_number, page_size, total_count):
        if page_number * page_size >= total_count:
            return None

        next_page = page_number + 1
        return self.build_page_url(request, next_page)

    def get_previous_url(self, request, page_number):
        if page_number <= 1:
            return None

        previous_page = page_number - 1
        return self.build_page_url(request, previous_page)

    def build_page_url(self, request, page_number):
        query_params = request.query_params.copy()
        query_params["page"] = page_number

        return f"{request.build_absolute_uri(request.path)}?{query_params.urlencode()}"


class OfferDetailView(APIView):
    permission_classes = [IsBusinessUserOrReadOnly]

    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        serializer = OfferSerializer(offer)

        return Response(serializer.data)

    def patch(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        if offer.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = OfferSerializer(
            offer,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        if offer.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        offer.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetailItemView(APIView):
    def get(self, request, pk):
        detail = get_object_or_404(OfferDetail, pk=pk)
        serializer = OfferDetailSerializer(detail)

        return Response(serializer.data)
