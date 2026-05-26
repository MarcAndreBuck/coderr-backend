from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from auth_app.api.permissions import IsProfileOwnerOrReadOnly
from auth_app.models import UserProfile
from auth_app.api.serializers import BusinessProfileListSerializer, CustomerProfileListSerializer, ProfileDetailSerializer, RegisterSerializer


class RegistrationView(APIView):
    """
    API view for user registration.
    Handles POST requests to create a new user and profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user and return authentication token.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response({"token": token.key,
                             "username": user.username,
                             "email": user.email,
                             "user_id": user.id, }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user login.
    Handles POST requests to authenticate and return a token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and return authentication token.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key,
                             "username": user.username,
                             "email": user.email,
                             "user_id": user.id, }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    API view for retrieving and updating user profiles.
    GET returns profile data, PATCH updates own profile.
    """
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]

    def get(self, request, pk):
        """
        Retrieve profile details for a given user id.
        """
        profile = get_object_or_404(UserProfile, user_id=pk)
        serializer = ProfileDetailSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Update profile details for the authenticated user.
        """
        profile = get_object_or_404(UserProfile, user_id=pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileDetailSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(APIView):
    """
    API view to list all business user profiles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all business profiles.
        """
        profiles = UserProfile.objects.filter(user_type="business")
        serializer = BusinessProfileListSerializer(profiles, many=True)
        return Response(serializer.data)


class CustomerProfileListView(APIView):
    """
    API view to list all customer user profiles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all customer profiles.
        """
        profiles = UserProfile.objects.filter(user_type="customer")
        serializer = CustomerProfileListSerializer(profiles, many=True)
        return Response(serializer.data)
