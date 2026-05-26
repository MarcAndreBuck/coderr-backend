from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail (pricing tier).
    """
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for offers with nested details and user info.
    """
    details = OfferDetailSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        """
        Return the minimum price among offer details.
        """
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """
        Return the minimum delivery time among offer details.
        """
        delivery_times = obj.details.values_list(
            "delivery_time_in_days",
            flat=True,
        )
        return min(delivery_times) if delivery_times else None

    def get_user_details(self, obj):
        profile = obj.user.profile

        return {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "username": obj.user.username,
        }

    def create(self, validated_data):
        details_data = validated_data.pop("details")

        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data,
            )

        return offer