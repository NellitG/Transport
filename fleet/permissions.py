from rest_framework import permissions

def _in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return _in_group(request.user, 'Supervisor')

class IsTransportOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return _in_group(request.user, 'TransportOfficer')

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return _in_group(request.user, 'Driver')
