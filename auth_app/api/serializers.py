from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response


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
        UserProfile.objects.create(
            user=user,
            user_type=validated_data["type"],
        )
        return user


class ProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    type = serializers.CharField(source="user_type", read_only=True)
    created_at = serializers.DateTimeField(
        source="user.date_joined",
        read_only=True,)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "email",
            "type",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "created_at",
        ]


class BusinessProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    type = serializers.CharField(source="user_type", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    type = serializers.CharField(source="user_type", read_only=True)
    uploaded_at = serializers.DateTimeField(
        source="user.date_joined",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
