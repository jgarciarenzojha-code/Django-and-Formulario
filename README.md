# Sistema de Encomiendas con Django REST Framework

Proyecto Django para gestionar clientes, rutas, empleados y encomiendas. Incluye vistas web y una API REST documentada con Swagger.

## Tecnologias usadas

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Docker Compose
- JWT para autenticacion

## Levantar el proyecto

Copiar el archivo de variables:

```bash
copy .env.example .env
```

Construir y levantar los contenedores:

```bash
docker compose up -d --build
```

Aplicar migraciones:

```bash
docker compose exec web python manage.py migrate
```

Crear usuario administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Ejecutar pruebas:

```bash
docker compose exec web python manage.py test api -v 2
```

## Enlaces

- Aplicacion web: `http://localhost:8000/`
- Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`

## Autenticacion

Para obtener un token JWT:

```http
POST /api/v1/auth/token/
```

Body:

```json
{
  "username": "usuario",
  "password": "password"
}
```

Luego usar el token en Swagger o en las peticiones:

```http
Authorization: Bearer ACCESS_TOKEN
```

## Endpoints principales

API v1:

- `/api/v1/encomiendas/`
- `/api/v1/clientes/`
- `/api/v1/rutas/`
- `/api/v1/empleados/`
- `/api/v1/encomiendas/pendientes/`
- `/api/v1/encomiendas/con_retraso/`
- `/api/v1/encomiendas/estadisticas/`

API v2:

- `/api/v2/encomiendas/`
- `/api/v2/clientes/`
- `/api/v2/rutas/`
- `/api/v2/empleados/`

La version v2 mantiene las rutas principales y cambia la salida de encomiendas agregando el campo `resumen`.

## Funcionalidades implementadas

- Serializers para clientes, rutas, empleados y encomiendas.
- Vistas con FBV, APIView, mixins, generics y ViewSets.
- Router para generar rutas automaticamente.
- Acciones personalizadas para cambiar estado, listar pendientes, ver retrasos y estadisticas.
- Paginacion, filtros, busqueda y ordenamiento.
- Permisos personalizados para empleados activos y propietarios.
- Versionado con `/api/v1/` y `/api/v2/`.
- Swagger unificado para probar toda la API.
- Tests para validar los endpoints principales.

## Notas

El archivo `.env` no se sube al repositorio. Solo se deja `.env.example` como referencia.
