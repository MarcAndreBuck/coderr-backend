from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

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
        Return a paginated list of offers (with filters and search).
        """
        try:
            offers = self.get_filtered_offers(request)
            page = self.paginate_offers(request, offers)
        except ValueError:
            return Response(
                {"detail": "Invalid query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OfferSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return self.get_paginated_response(
            request,
            offers,
            serializer.data,
        )

    def get_positive_int_param(
        self,
        request,
        name,
        default=None,
    ):
        """
        Extracts a positive integer query parameter from the request.
        Returns None if the parameter is missing.
        Raises ValueError if the value is invalid.
        """
        value = request.query_params.get(name, default)

        if value is None:
            return None

        try:
            value = int(value)

            if value < 1:
                raise ValueError

            return value

        except (TypeError, ValueError):
            raise ValueError(name)

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
        Filters offers by a minimum price if provided.
        Returns the filtered queryset.
        """
        min_price = request.query_params.get("min_price")

        if not min_price:
            return offers

        try:
            min_price = float(min_price)
        except ValueError:
            raise ValueError("Invalid min price")

        return offers.filter(details__price__gte=min_price)

    def filter_by_max_delivery_time(self, request, offers):
        """
        Filters offers by a maximum delivery time (in days) if provided.
        Returns the filtered queryset.
        """
        max_delivery_time = self.get_positive_int_param(
            request,
            "max_delivery_time",
        )

        if not max_delivery_time:
            return offers

        return offers.filter(
            details__delivery_time_in_days__lte=max_delivery_time,
        )

    def paginate_offers(self, request, offers):
        """
        Paginates offers based on page_size and page query parameters.
        Returns the corresponding page of the queryset.
        """
        page_size = self.get_positive_int_param(
            request,
            "page_size",
            6,
        )
        page_number = self.get_positive_int_param(
            request,
            "page",
            1,
        )

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        return offers[start_index:end_index]

    def get_paginated_response(self, request, offers, results):
        """
        Creates the paginated response for the offer list.
        Includes count, next, previous, and results.
        """
        page_size = self.get_positive_int_param(
            request,
            "page_size",
            6,
        )
        page_number = self.get_positive_int_param(
            request,
            "page",
            1,
        )
        total_count = offers.count()

        return Response(
            {
                "count": total_count,
                "next": self.get_next_url(
                    request,
                    page_number,
                    page_size,
                    total_count,
                ),
                "previous": self.get_previous_url(request, page_number),
                "results": results,
            }
        )

    def get_next_url(self, request, page_number, page_size, total_count):
        """
        Returns the URL for the next page or None if there is no next page.
        """
        if page_number * page_size >= total_count:
            return None

        next_page = page_number + 1
        return self.build_page_url(request, next_page)

    def get_previous_url(self, request, page_number):
        """
        Returns the URL for the previous page or None if there is no previous page.
        """
        if page_number <= 1:
            return None

        previous_page = page_number - 1
        return self.build_page_url(request, previous_page)

    def build_page_url(self, request, page_number):
        """
        Builds an absolute URL for the given page with the current query parameters.
        """
        query_params = request.query_params.copy()
        query_params["page"] = page_number

        return f"{request.build_absolute_uri(request.path)}?{query_params.urlencode()}"


class OfferDetailView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessUserOrReadOnly]

    def get(self, request, pk):
        """
        Returns the details of an offer with the given ID.
        """
        offer = get_object_or_404(Offer, pk=pk)
        serializer = OfferSerializer(offer)

        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Updates an offer if the user is the owner.
        """
        offer = get_object_or_404(Offer, pk=pk)

        if offer.user != request.user:
            return Response(
                {"detail": "You are not allowed to modify this offer."},
                status=status.HTTP_403_FORBIDDEN,
            )

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
        """
        Deletes an offer if the user is the owner.
        """
        offer = get_object_or_404(Offer, pk=pk)

        if offer.user != request.user:
            return Response(
                {"detail": "You are not allowed to modify this offer."},
                status=status.HTTP_403_FORBIDDEN,
            )

        offer.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetailItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Returns the details of an OfferDetail object with the given ID.
        """
        detail = get_object_or_404(OfferDetail, pk=pk)
        serializer = OfferDetailSerializer(detail)

        return Response(serializer.data)
