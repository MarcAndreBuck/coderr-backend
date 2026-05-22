from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=["customer", "business"],
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user     