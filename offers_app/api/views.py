from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from offers_app.api.permissions import IsBusinessUserOrReadOnly
from offers_app.api.serializers import OfferSerializer
from offers_app.models import Offer


class OfferListView(APIView):
    permission_classes = [IsBusinessUserOrReadOnly]

    def get(self, request):
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers, many=True)

        return Response(serializer.data)

    def post(self, request):
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
