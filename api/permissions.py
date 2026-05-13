from rest_framework import permissions

from config.choices import EstadoGeneral
from empleados.models import Empleado


class EsEmpleadoActivo(permissions.BasePermission):
    message = 'Se requiere un empleado activo o usuario administrador.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return Empleado.objects.filter(
            dni=request.user.username,
            estado=EstadoGeneral.ACTIVO,
        ).exists()


class EsPropietarioOAdmin(permissions.BasePermission):
    message = 'Solo el propietario de la encomienda o un administrador puede acceder.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        remitente = getattr(obj, 'remitente', None)
        destinatario = getattr(obj, 'destinatario', None)
        user_email = (request.user.email or '').lower()
        username = request.user.get_username()

        return any([
            remitente and remitente.nro_doc == username,
            destinatario and destinatario.nro_doc == username,
            remitente and remitente.email and remitente.email.lower() == user_email,
            destinatario and destinatario.email and destinatario.email.lower() == user_email,
        ])
