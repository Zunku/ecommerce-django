# Module for custom permissions
from rest_framework import permissions

# Custom permission to limit not SAFE_METHODS to staff only
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # SAFE_METHODS are GET, HEAD and OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)