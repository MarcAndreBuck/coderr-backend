from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for review objects.
    """
    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer",
            "business_user",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "reviewer",
        ]