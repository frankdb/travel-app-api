from rest_framework import permissions


class IsEmployerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow employers to create or edit jobs.
    """

    def has_permission(self, request, view):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to employers
        return hasattr(request.user, "employer")

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the employer who owns the job
        return obj.employer == request.user.employer
