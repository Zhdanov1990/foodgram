#backend/api/permissions.py
from rest_framework import permissions

class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Редактировать объект может его автор или суперпользователь.
    Все остальные — только SAFE_METHODS.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Все методы, кроме SAFE_METHODS, доступны только staff-пользователям.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )
