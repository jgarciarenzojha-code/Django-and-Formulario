from django.db import models

class EncomiendaQuerySet(models.QuerySet):

    def pendientes(self):
        return self.filter(fecha_entrega__isnull=True)

    def activas(self):
        return self.filter(fecha_entrega__isnull=True)

    def con_retraso(self):
        return self.filter(fecha_entrega__gt=models.F('fecha_envio'))

    def por_ruta(self, ruta):
        return self.filter(ruta=ruta)
