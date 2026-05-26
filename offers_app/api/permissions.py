from rest_framework.permissions import BasePermission


class IsBusinessUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True

        return self.is_business_user(request)

    def is_business_user(self, request):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.user_type == "business"
        )