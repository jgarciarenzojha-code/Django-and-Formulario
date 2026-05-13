from django.db import models
from config.choices import EstadoGeneral

class Empleado(models.Model):
    dni = models.CharField(max_length=8, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    estado = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO
    )

    @property
    def esta_activo(self):
        return self.estado == EstadoGeneral.ACTIVO

    def __str__(self):
        return f"{self.dni} - {self.nombres}"

    class Meta:
        db_table = 'empleados'
        ordering = ['apellidos', 'nombres']
