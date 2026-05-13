from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente
from config.choices import EstadoGeneral
from empleados.models import Empleado
from envios.models import Encomienda, EstadoEncomienda
from rutas.models import Ruta


class EncomiendaAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='renzo',
            password='Soccer123pro',
            email='admin@example.com',
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        self.remitente = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='12345678',
            nombres='Ana',
            apellidos='Ramos',
            email='ana@example.com',
        )
        self.destinatario = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='87654321',
            nombres='Luis',
            apellidos='Perez',
            email='luis@example.com',
        )
        self.ruta = Ruta.objects.create(
            origen='Lima',
            destino='Cusco',
            precio='35.50',
        )
        self.encomienda = Encomienda.objects.create(
            codigo='ENC-001',
            descripcion='Caja mediana',
            peso=2.5,
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
        )

    def payload(self, codigo='ENC-002'):
        return {
            'codigo': codigo,
            'descripcion': 'Sobre documentario',
            'peso': 1.2,
            'remitente': self.remitente.id,
            'destinatario': self.destinatario.id,
            'ruta': self.ruta.id,
        }

    def test_list_encomiendas(self):
        url = reverse('v1:encomiendas-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_uses_pagination_and_max_three_queries(self):
        for index in range(2, 18):
            Encomienda.objects.create(
                codigo=f'ENC-{index:03d}',
                descripcion='Caja de prueba',
                peso=1.0,
                remitente=self.remitente,
                destinatario=self.destinatario,
                ruta=self.ruta,
            )

        url = reverse('v1:encomiendas-list')
        with self.assertNumQueries(3):
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 17)
        self.assertEqual(len(response.data['results']), 15)

    def test_create_encomienda(self):
        url = reverse('v1:encomiendas-list')
        response = self.client.post(url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Encomienda.objects.count(), 2)

    def test_create_encomienda_error_400(self):
        url = reverse('v1:encomiendas-list')
        payload = self.payload(codigo='MAL-001')
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['status_code'], 400)

    def test_cambiar_estado(self):
        url = reverse('v1:encomiendas-cambiar-estado', args=[self.encomienda.id])
        response = self.client.post(
            url,
            {'estado': EstadoEncomienda.ENTREGADA},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.encomienda.refresh_from_db()
        self.assertEqual(self.encomienda.estado, EstadoEncomienda.ENTREGADA)
        self.assertEqual(self.encomienda.historialestado_set.count(), 1)

    def test_bulk_create(self):
        url = reverse('v1:encomiendas-bulk-create')
        payload = [
            self.payload(codigo='ENC-010'),
            self.payload(codigo='ENC-011'),
        ]
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Encomienda.objects.count(), 3)

    def test_estadisticas(self):
        url = reverse('v1:encomiendas-estadisticas')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)
        self.assertIn('por_estado', response.data)

    def test_v2_uses_distinct_serializer(self):
        url = reverse('v2:encomiendas-detail', args=[self.encomienda.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('resumen', response.data)

    def test_v2_root_lists_router_endpoints_without_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse('v2:api-root')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('encomiendas', response.data)
        self.assertIn('clientes', response.data)
        self.assertIn('rutas', response.data)
        self.assertIn('empleados', response.data)

    def test_global_docs_include_v1_and_v2(self):
        self.client.force_authenticate(user=None)

        docs_response = self.client.get(reverse('swagger-ui'))
        self.assertEqual(docs_response.status_code, status.HTTP_200_OK)

        schema_response = self.client.get(reverse('schema'))
        schema_content = schema_response.content.decode()
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        self.assertIn('/api/v1/encomiendas/', schema_content)
        self.assertIn('/api/v2/encomiendas/', schema_content)

    def test_v2_token_is_available(self):
        self.client.force_authenticate(user=None)

        token_response = self.client.post(
            reverse('v2:token_obtain_pair'),
            {'username': 'admin', 'password': 'admin12345'},
            format='json',
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_response.data)

    def test_token_payload_includes_custom_user_data(self):
        self.client.force_authenticate(user=None)
        url = reverse('v1:token_obtain_pair')
        response = self.client.post(
            url,
            {'username': 'admin', 'password': 'admin12345'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'admin')
        self.assertTrue(response.data['user']['is_staff'])

    def test_empleado_permission_requires_active_employee(self):
        User = get_user_model()
        empleado_user = User.objects.create_user(
            username='11223344',
            password='empleado12345',
        )
        self.client.force_authenticate(empleado_user)
        url = reverse('v1:empleados-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        empleado = Empleado.objects.create(
            dni='11223344',
            nombres='Mario',
            apellidos='Salas',
            cargo='Operador',
            estado=EstadoGeneral.INACTIVO,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        empleado.estado = EstadoGeneral.ACTIVO
        empleado.save(update_fields=['estado'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
