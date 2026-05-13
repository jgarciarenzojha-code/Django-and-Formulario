from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from envios.models import Encomienda, EstadoEncomienda, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta
from empleados.models import Empleado


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['fecha_registro']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated and not request.user.is_staff:
            data.pop('email', None)
            data.pop('telefono', None)
            data.pop('direccion', None)
        return data


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'
        read_only_fields = ['fecha_creacion']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstado
        fields = ['id', 'estado', 'fecha']
        read_only_fields = fields


class EncomiendaSerializer(serializers.ModelSerializer):
    esta_entregada = serializers.BooleanField(read_only=True)
    tiene_retraso = serializers.BooleanField(read_only=True)
    dias_en_transito = serializers.IntegerField(read_only=True)
    descripcion_corta = serializers.CharField(read_only=True)

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'descripcion_corta',
            'peso',
            'estado',
            'remitente',
            'destinatario',
            'ruta',
            'fecha_envio',
            'fecha_entrega',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
        ]
        read_only_fields = [
            'fecha_envio',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
            'descripcion_corta',
        ]

    def validate_peso(self, value):
        return self.validate_peso_kg(value)

    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError('El peso debe ser mayor a 0 kg')
        return value

    def validate_codigo(self, value):
        if not value.startswith('ENC-'):
            raise serializers.ValidationError('El codigo debe comenzar con ENC-')
        return value

    def validate(self, attrs):
        remitente = attrs.get('remitente', getattr(self.instance, 'remitente', None))
        destinatario = attrs.get('destinatario', getattr(self.instance, 'destinatario', None))
        fecha_entrega = attrs.get(
            'fecha_entrega',
            getattr(self.instance, 'fecha_entrega', None)
        )

        if remitente and destinatario and remitente == destinatario:
            raise serializers.ValidationError({
                'destinatario': 'Remitente y destinatario no pueden ser iguales'
            })

        if fecha_entrega and fecha_entrega < timezone.now():
            raise serializers.ValidationError({
                'fecha_entrega': 'La fecha de entrega no puede estar en el pasado'
            })

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class EncomiendaDetailSerializer(EncomiendaSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)
    historial = serializers.SerializerMethodField()

    class Meta(EncomiendaSerializer.Meta):
        fields = EncomiendaSerializer.Meta.fields + ['historial']

    def get_historial(self, obj):
        estados = obj.historialestado_set.order_by('-fecha')
        return HistorialEstadoSerializer(estados, many=True).data


class EncomiendaV2Serializer(EncomiendaDetailSerializer):
    resumen = serializers.SerializerMethodField()

    class Meta(EncomiendaDetailSerializer.Meta):
        fields = EncomiendaDetailSerializer.Meta.fields + ['resumen']

    def get_resumen(self, obj):
        return f'{obj.codigo} - {obj.estado} - {obj.descripcion_corta}'


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.get_username()
        token['is_staff'] = user.is_staff
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.get_username(),
            'is_staff': self.user.is_staff,
        }
        return data
