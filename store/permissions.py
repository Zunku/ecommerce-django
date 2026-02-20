from rest_framework import permissions

# Custom permission to limit not SAFE_METHODS to staff only
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
    
# DjangoModelPermissions validate is the user is authenticated and have the right model permission
class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    # Modifying constructor to change dictionary key 'GET' to enabling Get requests for users with view permission
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        
# Custom model permission
class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # has_perm validates if an user has a model permission
        return request.user.has_perm('store.view_history')