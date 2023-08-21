from rest_framework.permissions import BasePermission


class LabPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.lab_user.is_admin)