from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from offers_app.models import OfferDetail
from orders_app.api.serializers import OrderSerializer
from orders_app.models import Order


class OrderListView(APIView):
    """
    API view for listing and creating orders.
    """
    def get(self, request):
        """
        Return a list of orders for the current user (as customer or business user).
        """
        orders = Order.objects.filter(
            customer_user=request.user,
        ) | Order.objects.filter(
            business_user=request.user,
        )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new order for the authenticated customer user.
        """
        if request.user.profile.user_type != "customer":
            return Response(
                {"detail": "Only customers can create orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        offer_detail_id = request.data.get("offer_detail_id")

        if not offer_detail_id:
            return Response(
                {"detail": "offer_detail_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id)
        except (OfferDetail.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid offer_detail_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """
    API view for updating and deleting a specific order.
    """
    def patch(self, request, pk):
        """
        Update an order if the user is the business user.
        """
        order = get_object_or_404(Order, pk=pk)

        if request.user != order.business_user:
            return Response(
                {"detail": "You are not allowed to update this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderSerializer(
            order,
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
        Delete an order if the user is staff.
        """
        order = get_object_or_404(Order, pk=pk)

        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff users can delete orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    """
    API view for retrieving the count of orders for a business user.
    """
    def get(self, request, business_user_id):
        """
        Return the number of orders for the given business user.
        """
        profile = get_object_or_404(
            UserProfile,
            user_id=business_user_id,
            user_type="business",
        )

        order_count = Order.objects.filter(
            business_user=profile.user,
            status="in_progress",
        ).count()

        return Response({"order_count": order_count})


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        profile = get_object_or_404(
            UserProfile,
            user_id=business_user_id,
            user_type="business",
        )

        completed_order_count = Order.objects.filter(
            business_user=profile.user,
            status="completed",
        ).count()

        return Response(
            {"completed_order_count": completed_order_count}
        )
