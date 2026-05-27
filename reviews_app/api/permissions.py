from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Permission: Only allow access for authenticated customer users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.user_type == "customer"
        )


class IsReviewerOrReadOnly(BasePermission):
    """
    Permission: Allow read access for anyone, write access only for the reviewer.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True

        return obj.reviewer == request.user