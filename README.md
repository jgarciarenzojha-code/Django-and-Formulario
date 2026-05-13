# Proyecto Django REST Framework - Encomiendas

API y aplicacion web para gestionar clientes, rutas, empleados y encomiendas. El proyecto esta preparado para ejecutarse con Docker Compose usando Django, Django REST Framework, PostgreSQL y Redis.

## Servicios

- `web`: Django 5.2 + Django REST Framework.
- `db`: PostgreSQL 15.
- `redis`: Redis 7 para cache y throttling.

## Ejecutar con Docker

1. Copiar variables de entorno:

   ```bash
   copy .env.example .env
   ```

2. Construir y levantar contenedores:

   ```bash
   docker compose up -d --build
   ```

3. Aplicar migraciones:

   ```bash
   docker compose exec web python manage.py migrate
   ```

4. Crear superusuario:

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. Ejecutar pruebas:

   ```bash
   docker compose exec web python manage.py test api -v 2
   ```

## URLs principales

- Aplicacion web: `http://localhost:8000/`
- Admin Django: `http://localhost:8000/admin/`
- Swagger/OpenAPI unificado: `http://localhost:8000/api/docs/`
- Schema OpenAPI unificado: `http://localhost:8000/api/schema/`

## Autenticacion JWT

Obtener token:

```http
POST http://localhost:8000/api/v1/auth/token/
Content-Type: application/json

{
  "username": "renzo",
  "password": "Soccer123pro"
}
```

Usar el token:

```http
Authorization: Bearer ACCESS_TOKEN
```

Renovar token:

```http
POST http://localhost:8000/api/v1/auth/token/refresh/
```

## Endpoints API v1

- `GET/POST /api/v1/encomiendas/`
- `GET/PATCH/DELETE /api/v1/encomiendas/{id}/`
- `POST /api/v1/encomiendas/{id}/cambiar_estado/`
- `GET /api/v1/encomiendas/pendientes/`
- `GET /api/v1/encomiendas/con_retraso/`
- `GET /api/v1/encomiendas/estadisticas/`
- `POST /api/v1/encomiendas/bulk_create/`
- `PATCH /api/v1/encomiendas/bulk_estado/`
- `GET/POST /api/v1/clientes/`
- `GET/POST /api/v1/rutas/`
- `GET/POST /api/v1/empleados/`

Tambien se incluyen endpoints equivalentes para demostrar FBV, APIView, mixins y generics:

- `/api/v1/fbv/encomiendas/`
- `/api/v1/apiview/encomiendas/`
- `/api/v1/mixins/encomiendas/`
- `/api/v1/generics/encomiendas/`

## API v2

- `POST /api/v2/auth/token/`
- `POST /api/v2/auth/token/refresh/`
- `GET /api/v2/encomiendas/`
- `GET /api/v2/encomiendas/{id}/`
- `GET/POST /api/v2/clientes/`
- `GET/POST /api/v2/rutas/`
- `GET/POST /api/v2/empleados/`
- `/api/v2/fbv/encomiendas/`
- `/api/v2/apiview/encomiendas/`
- `/api/v2/mixins/encomiendas/`
- `/api/v2/generics/encomiendas/`

La version v2 expone las mismas familias de endpoints que v1. En encomiendas usa un serializer distinto e incluye el campo `resumen`.

## Checklist del entregable DRF

- DRF instalado y configurado.
- `EncomiendaSerializer` y `EncomiendaDetailSerializer` con propiedades del modelo.
- Endpoints FBV para listar y detallar encomiendas.
- Endpoints CBV con `APIView` para `get`, `post`, `patch` y `delete`.
- Mixins con `List`, `Create`, `Retrieve`, `Update` y `Destroy`.
- Generic views con `ListCreateAPIView` y `RetrieveUpdateDestroyAPIView`.
- `EncomiendaViewSet` con `@action` para `cambiar_estado`.
- Acciones de lista: `pendientes`, `con_retraso` y `estadisticas`.
- Router DRF con URLs automaticas.
- Serializer anidado para objetos relacionados e historial.
- Paginacion `PageNumberPagination` con `PAGE_SIZE = 15`.
- Filtros por `estado`, `ruta`, `remitente`, `destinatario` y `con_retraso`.
- Busqueda y ordenamiento configurados.
- JWT con obtencion, renovacion y payload personalizado.
- Permisos `EsEmpleadoActivo` y `EsPropietarioOAdmin`.
- Validaciones `validate_peso_kg`, `validate_codigo` y `validate`.
- Swagger unificado en `/api/docs/` y schema en `/api/schema/`.
- Versionado `/api/v1/` y `/api/v2/`.
- Tests para list, create, error 400, cambiar estado, bulk, JWT, permisos, paginacion y versionado.
- Throttling para login y empleados.
- Exception handler con formato JSON uniforme.
- CORS habilitado.
- `to_representation` oculta campos sensibles para usuarios no staff.
- Bulk create y bulk estado.
- `select_related` y `prefetch_related` en relaciones.
- Redis en Docker Compose para cache de estadisticas por 15 minutos.

## Notas

- No subir `.env` al repositorio.
- Si Docker conserva datos antiguos, las migraciones nuevas se aplican con `docker compose exec web python manage.py migrate`.
