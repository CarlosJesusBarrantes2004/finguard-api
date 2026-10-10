from rest_framework import permissions


class EsTitularDeCuenta(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user
