# Asistente de Atención Médica

Asistente de IA para triage y creación de atención médica. No emite diagnósticos médicos; actúa como auxiliar de enfermería digital.

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite + TypeScript, servido con nginx

## Antes de empezar

Configura las variables de entorno siguiendo **[`docs/instalacion.md`](docs/instalacion.md)**. Los comandos de abajo asumen que ya lo hiciste.

## Ejecución con Docker Compose

```bash
docker compose up -d --build
```

- **Frontend**: http://localhost:5173
- **Backend / docs interactivas**: http://localhost:8010/docs

Bajar los contenedores: `docker compose down`.

## Ejecución sin Docker

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
npm install
npm run dev
```

Frontend en http://localhost:5173.

## Documentación

- [`docs/arquitectura.md`](docs/arquitectura.md) — arquitectura del backend
- [`docs/logica_clinica.md`](docs/logica_clinica.md) — motor de reglas + RAG, cómo se combinan con el LLM
- [`docs/instalacion.md`](docs/instalacion.md) — entornos y variables
- [`docs/api.md`](docs/api.md) — referencia de endpoints
- [`docs/decisiones_tecnicas.md`](docs/decisiones_tecnicas.md) — decisiones de diseño y su porqué
- [`postman/Emermedica-API.postman_collection.json`](postman/Emermedica-API.postman_collection.json) — colección de Postman
