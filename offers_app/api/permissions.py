from rest_framework.permissions import BasePermission


class IsBusinessUserOrReadOnly(BasePermission):
    """
    Permission: Allow read for anyone, write only for business users.
    """
    def has_permission(self, request, view):
        """
        Grant access if read or user is a business user.
        """
        if request.method == "GET":
            return True

        return self.is_business_user(request)

    def is_business_user(self, request):
        """
        Return True if the user is authenticated and a business user.
        """
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.user_type == "business"
        )