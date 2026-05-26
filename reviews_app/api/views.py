from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from reviews_app.api.permissions import (
    IsCustomerUser,
    IsReviewerOrReadOnly,
)
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class ReviewListView(APIView):
    def get(self, request):
        reviews = Review.objects.all()

        serializer = ReviewSerializer(
            reviews,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.profile.user_type != "customer":
            return Response(status=status.HTTP_403_FORBIDDEN)

        business_user_id = request.data.get("business_user")

        has_completed_order = Order.objects.filter(
            customer_user=request.user,
            business_user_id=business_user_id,
            status="completed",
        ).exists()

        if not has_completed_order:
            return Response(status=status.HTTP_403_FORBIDDEN)

        already_reviewed = Review.objects.filter(
            reviewer=request.user,
            business_user_id=business_user_id,
        ).exists()

        if already_reviewed:
            return Response(
                {"error": "You already reviewed this business."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(reviewer=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReviewDetailView(APIView):
    def patch(self, request, pk):
        review = get_object_or_404(Review, pk=pk)

        if review.reviewer != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSerializer(
            review,
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
        review = get_object_or_404(Review, pk=pk)

        if review.reviewer != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        review.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
