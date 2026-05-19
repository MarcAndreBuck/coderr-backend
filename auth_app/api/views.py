from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({})