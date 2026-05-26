from rest_framework.permissions import BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    Allow read requests for authenticated users and write requests only for profile owners.
    """

    def has_object_permission(self, request, view, obj):
        """
        Grant access if read or user owns the profile.
        """
        if self.is_read_request(request):
            return True

        return self.is_profile_owner(request, obj)

    def is_read_request(self, request):
        """
        Return True if request is a read (GET) request.
        """
        return request.method == "GET"

    def is_profile_owner(self, request, obj):
        """
        Return True if the user owns the profile.
        """
        return obj.user == request.user
