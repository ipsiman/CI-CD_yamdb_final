from rest_framework.permissions import SAFE_METHODS, BasePermission

from api.models import UserRole


class ReadOnlyPermission(BasePermission):
    """Класс для разрешения доступа только для чтения."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ObjectAuthorPermission(BasePermission):
    """Класс для разрешения доступа только для чтения или автору."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author


class AdminPermission(BasePermission):
    """Класс для разрешения доступа только администратору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.role == UserRole.ADMIN or
                request.user.is_staff or
                request.user.is_superuser
            )

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
                    request.user.role == UserRole.ADMIN or
                    request.user.is_staff or
                    request.user.is_superuser
        )


class ModeratorPermission(BasePermission):
    """Класс для разрешения доступа только модератору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == UserRole.MODERATOR

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
                request.user.role == UserRole.MODERATOR
        )
