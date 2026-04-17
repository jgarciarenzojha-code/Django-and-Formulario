# Django con Docker

Este proyecto contiene una aplicación Django mínima con un formulario de contacto y configuración para ejecutarse con Docker Compose.

## Archivos clave

- `Dockerfile` - imagen de Python 3.11 con Django y `psycopg2-binary`
- `docker-compose.yml` - servicios `db` (PostgreSQL) y `web` (Django)
- `.env.example` - ejemplo de variables de entorno para la base de datos

## Cómo ejecutar

1. Copiar `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```

2. Levantar los servicios:
   ```bash
   docker compose up --build -d
   ```

3. Ejecutar migraciones:
   ```bash
   docker compose exec web python manage.py migrate
   ```

4. Crear superusuario (opcional para admin):
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. Abrir la aplicación:
   - `http://localhost:8000/`
   - `http://localhost:8000/admin/`

## Notas

- No se debe subir `.env` al repositorio.
- Se incluye `.env.example` con valores de ejemplo.
