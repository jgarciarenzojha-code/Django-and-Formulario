from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from envios.models import Encomienda, EstadoEncomienda
from clientes.models import Cliente
from rutas.models import Ruta
from empleados.models import Empleado

from .permissions import EsEmpleadoActivo, EsPropietarioOAdmin
from .serializers import (
    CustomTokenObtainPairSerializer,
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    EncomiendaV2Serializer,
    ClienteSerializer,
    RutaSerializer,
    EmpleadoSerializer,
)
from .throttles import EmpleadoRateThrottle, LoginRateThrottle


class EncomiendaFilter(filters.FilterSet):
    con_retraso = filters.BooleanFilter(method='filter_con_retraso')

    class Meta:
        model = Encomienda
        fields = ['estado', 'ruta', 'remitente', 'destinatario', 'con_retraso']

    def filter_con_retraso(self, queryset, name, value):
        if value:
            return queryset.con_retraso()
        return queryset.exclude(pk__in=queryset.con_retraso().values('pk'))


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class EncomiendaBaseQuerysetMixin:
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EncomiendaFilter
    search_fields = [
        'codigo',
        'descripcion',
        'remitente__nro_doc',
        'remitente__nombres',
        'remitente__apellidos',
        'destinatario__nro_doc',
        'destinatario__nombres',
        'destinatario__apellidos',
    ]
    ordering_fields = ['id', 'codigo', 'peso', 'estado', 'fecha_envio', 'fecha_entrega']
    ordering = ['-fecha_envio']

    def get_queryset(self):
        return (
            Encomienda.objects
            .select_related('remitente', 'destinatario', 'ruta')
            .prefetch_related('historialestado_set')
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def encomienda_fbv_list(request):
    if request.method == 'GET':
        serializer = EncomiendaSerializer(
            Encomienda.objects.select_related('remitente', 'destinatario', 'ruta'),
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    serializer = EncomiendaSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encomienda_fbv_detail(request, pk):
    encomienda = generics.get_object_or_404(
        Encomienda.objects.select_related('remitente', 'destinatario', 'ruta'),
        pk=pk,
    )
    serializer = EncomiendaDetailSerializer(encomienda, context={'request': request})
    return Response(serializer.data)


class EncomiendaAPIView(EncomiendaBaseQuerysetMixin, APIView):
    def get(self, request):
        serializer = EncomiendaSerializer(
            self.get_queryset(),
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = EncomiendaSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EncomiendaDetailAPIView(EncomiendaBaseQuerysetMixin, APIView):
    def get_object(self, pk):
        return generics.get_object_or_404(self.get_queryset(), pk=pk)

    def get(self, request, pk):
        serializer = EncomiendaDetailSerializer(
            self.get_object(pk),
            context={'request': request},
        )
        return Response(serializer.data)

    def patch(self, request, pk):
        serializer = EncomiendaSerializer(
            self.get_object(pk),
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EncomiendaMixinView(
    EncomiendaBaseQuerysetMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk=pk)
        return self.list(request)

    def post(self, request):
        return self.create(request)

    def patch(self, request, pk):
        return self.partial_update(request, pk=pk)

    def delete(self, request, pk):
        return self.destroy(request, pk=pk)


class EncomiendaListCreateAPIView(EncomiendaBaseQuerysetMixin, generics.ListCreateAPIView):
    pass


class EncomiendaRetrieveUpdateDestroyAPIView(
    EncomiendaBaseQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer


class EncomiendaViewSet(EncomiendaBaseQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), EsPropietarioOAdmin()]
        if self.action in ['cambiar_estado', 'bulk_estado']:
            return [EsEmpleadoActivo()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        encomienda = self.get_object()
        nuevo_estado = request.data.get('estado')

        if not nuevo_estado:
            return Response(
                {'estado': ['Debe enviar estado']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            encomienda.cambiar_estado(nuevo_estado)
        except DjangoValidationError as exc:
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)

        serializer = EncomiendaDetailSerializer(encomienda, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        serializer = self.get_serializer(
            self.filter_queryset(self.get_queryset().pendientes()),
            many=True,
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def con_retraso(self, request):
        serializer = self.get_serializer(
            self.filter_queryset(self.get_queryset().con_retraso()),
            many=True,
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        cache_key = 'api:encomiendas:estadisticas'
        data = cache.get(cache_key)
        if data is None:
            por_estado = dict(
                self.get_queryset()
                .values_list('estado')
                .annotate(total=Count('id'))
            )
            data = {
                'total': self.get_queryset().count(),
                'pendientes': self.get_queryset().pendientes().count(),
                'con_retraso': self.get_queryset().con_retraso().count(),
                'por_estado': por_estado,
            }
            cache.set(cache_key, data, 60 * 15)
        return Response(data)

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        serializer = EncomiendaSerializer(
            data=request.data,
            many=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='bulk_estado')
    def bulk_estado(self, request):
        ids = request.data.get('ids', [])
        nuevo_estado = request.data.get('estado')

        if not ids or not nuevo_estado:
            return Response(
                {'detail': 'Debe enviar ids y estado'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if nuevo_estado not in EstadoEncomienda.values:
            return Response(
                {'estado': ['Estado de encomienda invalido']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            encomiendas = list(self.get_queryset().filter(id__in=ids))
            for encomienda in encomiendas:
                encomienda.cambiar_estado(nuevo_estado)

        serializer = EncomiendaSerializer(
            encomiendas,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class EncomiendaV2ViewSet(EncomiendaViewSet):
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EncomiendaV2Serializer
        return EncomiendaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nro_doc', 'nombres', 'apellidos', 'email']
    ordering_fields = ['id', 'nro_doc', 'apellidos', 'nombres', 'estado']


class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['origen', 'destino']
    ordering_fields = ['id', 'origen', 'destino', 'precio']


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [EsEmpleadoActivo]
    throttle_classes = [EmpleadoRateThrottle]
    search_fields = ['dni', 'nombres', 'apellidos', 'cargo']
    ordering_fields = ['id', 'dni', 'apellidos', 'nombres', 'cargo']
