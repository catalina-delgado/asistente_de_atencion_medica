# Instalación — entornos y variables

Esta guía cubre solo la configuración de entornos y variables. Los comandos para levantar el proyecto una vez configurado están en el [`README`](../README.md).

## Requisitos

- **Con Docker (recomendado):** Docker + Docker Compose.
- **Sin Docker:** Python 3.12+ y Node 20+.

## Archivos de entorno

Hay hasta tres `.env` distintos, ninguno se sube a git (ver sus `.env.example` correspondientes):

| Archivo             | Cuándo hace falta                          | Para qué se usa                                                          |
| --------------------- | --------------------------------------------- | --------------------------------------------------------------------------- |
| `backend/.env`       | Siempre                                       | Configuración que consume el backend en runtime (Docker o local)          |
| `.env` (raíz)        | Solo con Docker Compose                       | Sustituye el build-arg del frontend (`API_TOKEN`) — Compose no lee `backend/.env` para esto |
| `frontend/.env`      | Solo si corres el frontend **sin Docker**     | Vite lo lee en `npm run dev`; con Docker estas variables van como build-args en `docker-compose.yml` |

## 1. Copiar las plantillas

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Si vas a correr el frontend sin Docker, copia también:

```bash
cp frontend/.env.example frontend/.env
```

## 2. Generar y sincronizar `API_TOKEN`

Protege `/chat`, `/triage` y `/atencion`. Genera uno:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Pon el **mismo valor** en:

- `API_TOKEN` de `backend/.env`
- `API_TOKEN` de `.env` (raíz) — debe coincidir
- `VITE_API_TOKEN` de `frontend/.env` — solo si corres sin Docker

## 3. Completar el resto de variables

### `backend/.env`

| Variable              | Descripción                                                                    |
| ---------------------- | ------------------------------------------------------------------------------- |
| `APP_ENV`              | `development` \| `production` \| `test`                                        |
| `LOG_LEVEL`            | Nivel de logging (`INFO`, `DEBUG`, ...)                                        |
| `CORS_ORIGINS`         | Orígenes permitidos, separados por coma (debe incluir la URL del frontend)     |
| `LLM_PROVIDER`         | `mock` (reglas locales, sin costo/red) o `gemini` (requiere `GEMINI_API_KEY`)  |
| `GEMINI_API_KEY`       | API key de Gemini. Si falta, la app cae automáticamente a `mock`.              |
| `GEMINI_MODEL`         | Modelo de Gemini a usar                                                        |
| `SESSION_TTL_MINUTES`  | Minutos de inactividad antes de expirar una sesión de conversación             |
| `AUDIT_LOG_PATH`       | Ruta del log de auditoría dentro del contenedor                                |
| `API_TOKEN`            | Token bearer requerido para `/chat`, `/triage` y `/atencion`                   |

> Con Docker, `CORS_ORIGINS` debe incluir `http://localhost:5173` (el puerto publicado del frontend). Sin Docker sigue siendo `http://localhost:5173` (el puerto de `npm run dev`), así que no cambia entre ambos modos.

### `.env` (raíz)

Solo `API_TOKEN` — debe ser idéntico al de `backend/.env`.

### `frontend/.env` (solo sin Docker)

| Variable           | Descripción                                                |
| -------------------- | ------------------------------------------------------------ |
| `VITE_API_BASE_URL` | URL del backend. Sin Docker es `http://localhost:8000` (uvicorn corre directo en ese puerto, no en el 8010 remapeado de Docker) |
| `VITE_API_TOKEN`    | Debe coincidir con `API_TOKEN` de `backend/.env`             |

## Listo

Con esto configurado, los comandos para levantar el proyecto (con o sin Docker) están en el [`README`](../README.md).
