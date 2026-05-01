from django.contrib import admin
from .models import Encomienda, HistorialEstado


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'remitente', 'ruta', 'peso')
    search_fields = ('descripcion',)

admin.site.register(HistorialEstado)