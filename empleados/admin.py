from django.contrib import admin
from .models import Empleado

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombres', 'apellidos', 'cargo', 'estado')
    list_filter = ('estado', 'cargo')
    search_fields = ('dni', 'nombres', 'apellidos', 'cargo')
