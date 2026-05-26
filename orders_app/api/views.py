from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import OfferDetail
from orders_app.api.serializers import OrderSerializer
from orders_app.models import Order


class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.filter(
            customer_user=request.user,
        ) | Order.objects.filter(
            business_user=request.user,
        )

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

    def post(self, request):
        if request.user.profile.user_type != "customer":
            return Response(status=status.HTTP_403_FORBIDDEN)

        offer_detail = get_object_or_404(
            OfferDetail,
            pk=request.data.get("offer_detail_id"),
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
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if request.user != order.business_user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(
            order,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    def get(self, request, business_user_id):
        order_count = Order.objects.filter(
            business_user_id=business_user_id,
            status="in_progress",
        ).count()

        return Response({"order_count": order_count})


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        completed_order_count = Order.objects.filter(
            business_user_id=business_user_id,
            status="completed",
        ).count()

        return Response(
            {"completed_order_count": completed_order_count}
        )
