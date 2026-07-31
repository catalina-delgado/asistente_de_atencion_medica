# Instalación

## Requisitos

- **Con Docker (recomendado):** Docker + Docker Compose.
- **Sin Docker:** Python 3.12+ y Node 20+.

## 1. Variables de entorno

Copia las plantillas y complétalas (ninguna se sube a git):

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Genera un token para proteger la API y ponlo en **ambos** archivos (`API_TOKEN` en `backend/.env`, `API_TOKEN` en `.env` de raíz):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Ver el detalle de cada variable en la tabla más abajo.

## 2a. Con Docker Compose

```bash
docker compose up -d --build
```

- **Frontend:** http://localhost:5173
- **Backend / docs interactivas (Swagger):** http://localhost:8010/docs

Bajar los contenedores: `docker compose down`.

## 2b. Sin Docker

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend en http://localhost:8000 (docs en http://localhost:8000/docs).

### Frontend

En otra terminal:

```bash
cd frontend
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Frontend en http://localhost:5173.

> Sin Docker, `CORS_ORIGINS` en `backend/.env` debe seguir incluyendo `http://localhost:5173`, y `VITE_API_TOKEN` en `frontend/.env` debe coincidir con `API_TOKEN` de `backend/.env`.

## 3. Probar la API

Importa `postman/Emermedica-API.postman_collection.json` en Postman y completa la variable de colección `api_token` con el valor de `API_TOKEN`. Ver [`api.md`](api.md) para el detalle de cada endpoint.

## Variables de entorno

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

### `.env` (raíz)

Solo se usa para que `docker-compose.yml` sustituya el build arg del frontend. Debe tener el **mismo** `API_TOKEN` que `backend/.env`.

### `frontend/.env` (solo para correr sin Docker)

| Variable           | Descripción                                                |
| -------------------- | ------------------------------------------------------------ |
| `VITE_API_BASE_URL` | URL del backend (`http://localhost:8000` sin Docker)        |
| `VITE_API_TOKEN`    | Debe coincidir con `API_TOKEN` de `backend/.env`             |

Con Docker Compose, estas dos variables se pasan como build args (`docker-compose.yml`) en vez de leerse de `frontend/.env`.
