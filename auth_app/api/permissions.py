from rest_framework.permissions import BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if self.is_read_request(request):
            return True

        return self.is_profile_owner(request, obj)

    def is_read_request(self, request):
        return request.method == "GET"

    def is_profile_owner(self, request, obj):
        return obj.user == request.user
