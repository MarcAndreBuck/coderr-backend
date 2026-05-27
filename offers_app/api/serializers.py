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
        """
        Create a new Offer instance along with its related OfferDetails.
        """
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data,
            )
        return offer

    def update(self, instance, validated_data):
        """
        Update an existing Offer instance and its related OfferDetails.
        """
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)
        if details_data:
            self.update_offer_details(instance, details_data)
        return instance

    def update_offer_details(self, offer, details_data):
        """
        Update the OfferDetails for a given Offer instance.
        """
        for detail_data in details_data:
            offer_type = detail_data.get("offer_type")
            detail = offer.details.filter(
                offer_type=offer_type,
            ).first()
            if detail:
                self.update_single_detail(detail, detail_data)

    def update_single_detail(self, detail, detail_data):
        """
        Update a single OfferDetail instance with new data.
        """
        for field, value in detail_data.items():
            setattr(detail, field, value)
        detail.save()

    def validate_details(self, details):
        """
        Validate that each detail has a valid offer_type.
        """
        valid_types = ["basic", "standard", "premium"]
        for detail in details:
            offer_type = detail.get("offer_type")
            if not offer_type:
                raise serializers.ValidationError(
                    "offer_type is required for each detail."
                )
            if offer_type not in valid_types:
                raise serializers.ValidationError(
                    "Invalid offer_type."
                )
        return details
