from rest_framework.permissions import BasePermission

from user.models import User  # Importa el modelo User desde tu app users


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsNotAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_admin


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Permitir GET (listar/ver) a todos los usuarios, autenticados o no
        if request.method in ["GET"]:
            return True
        # Permitir POST, PUT, PATCH, DELETE solo a administradores autenticados
        return request.user.is_authenticated and request.user.is_admin


class IsOwnerOrReadOnly(BasePermission):
    """
    Permiso personalizado que solo permite a los propietarios de una interacción
    editarla o eliminarla. Cualquier usuario puede ver las interacciones.
    """

    def has_permission(self, request, view):
        # Permitir GET a cualquier usuario
        if request.method in ["GET"]:
            return True
        # Para otros métodos, el usuario debe estar autenticado
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permitir GET a cualquier usuario
        if request.method in ["GET"]:
            return True
        # Permitir modificación solo al propietario
        return obj.interaction_source_user == request.user


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso para métodos de pago:
    - Solo el propietario puede ver, crear, editar y eliminar sus métodos de pago
    - Los administradores pueden ver todos los métodos de pago pero no editarlos
    - Los usuarios no autenticados no tienen acceso
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # El propietario puede hacer cualquier acción con sus métodos de pago
        if obj.user == request.user:
            return True

        # Los administradores solo pueden ver (GET), no modificar
        if request.user.is_admin and request.method in ["GET"]:
            return True

        return False
