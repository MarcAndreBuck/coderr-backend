from django.urls import path

from auth_app.api.views import LoginView, ProfileView, RegistrationView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile-detail",),
]
