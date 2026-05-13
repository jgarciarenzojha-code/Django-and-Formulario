from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from .validators import validar_peso_positivo, validar_codigo_encomienda
from .querysets import EncomiendaQuerySet

from clientes.models import Cliente
from rutas.models import Ruta

class EncomiendaManager(models.Manager):
    def get_queryset(self):
        return EncomiendaQuerySet(self.model, using=self._db)

    def pendientes(self):
        return self.get_queryset().pendientes()

    def activas(self):
        return self.get_queryset().activas()

    def con_retraso(self):
        return self.get_queryset().con_retraso()

    def por_ruta(self, ruta):
        return self.get_queryset().por_ruta(ruta)


class EstadoEncomienda(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    EN_TRANSITO = 'en_transito', 'En transito'
    ENTREGADA = 'entregada', 'Entregada'
    CANCELADA = 'cancelada', 'Cancelada'


class Encomienda(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        validators=[validar_codigo_encomienda]
    )

    descripcion = models.TextField()

    peso = models.FloatField(
        validators=[
            validar_peso_positivo,
            MinValueValidator(0.01)
        ]
    )

    remitente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='envios_realizados'
    )

    destinatario = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='envios_recibidos',
        null=True, blank=True
    )

    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)

    estado = models.CharField(
        max_length=20,
        choices=EstadoEncomienda.choices,
        default=EstadoEncomienda.PENDIENTE
    )

    fecha_envio = models.DateTimeField(auto_now_add=True)

    fecha_entrega = models.DateTimeField(
        null=True, blank=True
    )

    objects = EncomiendaManager()


    def clean(self):
        errors = {}

        if self.remitente and self.remitente.estado != 1:
            errors['remitente'] = "El remitente no está activo"

        if self.remitente and self.destinatario:
            if self.remitente == self.destinatario:
                errors['destinatario'] = "No pueden ser la misma persona"

        if self.fecha_entrega and self.estado != EstadoEncomienda.ENTREGADA:
            if self.fecha_entrega < timezone.now():
                errors['fecha_entrega'] = "No puede ser en el pasado"

        if errors:
            raise ValidationError(errors)


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    @property
    def esta_entregada(self):
        return self.fecha_entrega is not None

    @property
    def tiene_retraso(self):
        if self.fecha_entrega:
            return self.fecha_entrega > self.fecha_envio
        return False

    @property
    def dias_en_transito(self):
        if not self.fecha_entrega:
            return (timezone.now() - self.fecha_envio).days
        return (self.fecha_entrega - self.fecha_envio).days

    @property
    def descripcion_corta(self):
        return self.descripcion[:20]

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in EstadoEncomienda.values:
            raise ValidationError({'estado': 'Estado de encomienda invalido'})

        self.estado = nuevo_estado
        if nuevo_estado == EstadoEncomienda.ENTREGADA and not self.fecha_entrega:
            self.fecha_entrega = timezone.now()
        self.save(update_fields=['estado', 'fecha_entrega'])

        HistorialEstado.objects.create(
            encomienda=self,
            estado=nuevo_estado
        )
        return self


    @classmethod
    def crear_con_costo_calculado(cls, codigo, descripcion, peso, remitente, destinatario, ruta):
        costo = peso * ruta.precio

        return cls.objects.create(
            codigo=codigo,
            descripcion=f"{descripcion} (Costo: {costo})",
            peso=peso,
            remitente=remitente,
            destinatario=destinatario,
            ruta=ruta
        )

    def __str__(self):
        return f"{self.codigo} - {self.remitente}"

    class Meta:
        db_table = 'encomiendas'
        verbose_name = 'Encomienda'
        verbose_name_plural = 'Encomiendas'



class HistorialEstado(models.Model):
    encomienda = models.ForeignKey('Encomienda', on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.encomienda.codigo} - {self.estado}"

    class Meta:
        db_table = 'historial_estados'
