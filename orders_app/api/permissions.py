from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.user_type == "customer"
        )


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.user_type == "business"
        )


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff