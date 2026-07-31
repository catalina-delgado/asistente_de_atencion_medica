# Arquitectura del Backend

![Arquitectura](imagenes/arquitectura.png)

El diagrama refleja el wiring real de `app/api/deps.py` (quién instancia a quién) y las llamadas que hace cada módulo, no una capa "ideal" — se explica en el mismo orden en que aparece, de arriba hacia abajo.

## Usuario → Frontend

El usuario interactúa con el **Frontend** (React + Vite, servido por nginx en `:5173`), que llama a la API por HTTP.

## API (`app/api/routes.py` + `app/api/auth.py`)

Punto de entrada único. No contiene lógica de negocio, solo valida el request y delega en un `Service`.

- `GET /` y `GET /health` — públicos (el segundo lo usa el healthcheck de Docker, que no manda credenciales).
- `POST /chat`, `POST /triage`, `POST /atencion` — cada uno declara `dependencies=[Depends(require_bearer_token)]`; sin un `Authorization: Bearer <API_TOKEN>` válido, responden 401 antes de tocar ningún servicio.

## Services (`app/services/`)

`app/api/deps.py` instancia exactamente tres, cada uno detrás de su propia ruta:

- **ChatService** — conduce el intake conversacional.
- **TriageService** — clasifica el nivel de triage.
- **AtencionService** — genera el documento final. No repite la lógica de clasificación: **llama directamente a `TriageService`** (`resolver_conversacion()` + `clasificar()`), de ahí la flecha "usa" entre ambos en el diagrama — es una llamada de método en Python, no un segundo request HTTP.

## Clinical y LLM (`app/clinical/`, `app/llm/`)

Ambos son usados directamente por los servicios (no hay una capa intermedia entre ellos):

- **ChatService** solo llama a **LLM** (`responder_intake()`).
- **TriageService** llama a **ambos**: `Clinical.classify_by_rules()` (motor de banderas de alarma, determinista) y `Clinical.retrieve()` (protocolos relevantes vía `rag_retriever.py`), más `LLM.sugerir_triage()` / `generar_resumen_clinico()` / `generar_recomendaciones()`. El nivel de triage final es **el más urgente entre la sugerencia del LLM y el motor de reglas** (`more_urgent()`) — el LLM puede escalar la urgencia, nunca reducirla.
- **LLM** (`app/llm/factory.py`) elige en runtime entre `GeminiAdapter` (llama a la Gemini API externa) o `MockAdapter`, según `Settings.active_provider()`.
- La flecha punteada **LLM → Clinical** representa un detalle no obvio: `MockAdapter.sugerir_triage()` reutiliza directamente `classify_by_rules()`, el mismo motor de reglas que ya usa `TriageService`. Así el sistema es evaluable end-to-end sin red ni API key, con comportamiento clínico coherente entre ambos proveedores.

## Repositories (`app/repositories/`)

Los servicios nunca acceden al almacenamiento directamente:

- **ConversationRepository** — usado por `ChatService` y `TriageService` (crear/obtener conversaciones).
- **AttentionRepository** — usado solo por `AtencionService` (guardar el documento de atención generado).

## Almacenamiento — dos stores distintos, mismo nivel de capa

**No hay una única "base de datos"**, hay dos implementaciones separadas dentro de `app/database/`, cada `Repository` con la suya:

- **`InMemorySessionStore`** (`app/database/session_store.py`) — diccionario con expiración por TTL (`SESSION_TTL_MINUTES`), detrás de `ConversationRepository`. Tiene sentido que expire: una conversación abandonada es estado efímero.
- **`InMemoryAttentionStore`** (`app/database/attention_store.py`) — diccionario **sin TTL**, detrás de `AttentionRepository`. También tiene sentido que sea distinto: una atención ya generada es un registro, no debería desaparecer solo por tiempo.

Ambos son intencionalmente clases separadas (ciclos de vida distintos), pero ahora ambos viven en `app/database/` y se inyectan al `Repository` correspondiente por constructor — ninguno vive "escondido" dentro de su repositorio, a diferencia del diseño anterior.

Ninguno persiste en disco todavía: ambos se pierden al reiniciar el contenedor del backend. `sqlalchemy`, `psycopg2-binary` y `alembic` están en `requirements.txt` pero no están conectados a nada (ver [`decisiones_tecnicas.md`](decisiones_tecnicas.md)) — es la brecha real pendiente, no la separación en sí.

## Dependencias externas

- **`backend/app/clinical/protocols/*.md`** — los archivos fuente que lee `rag_retriever.py`.
- **Gemini API** — solo se llama desde dentro de `GeminiAdapter`, y solo si `LLM_PROVIDER=gemini` con una `GEMINI_API_KEY` válida.

## Cross-cutting

`config/settings.py`, `utils/security.py` (sanitizar entrada), `utils/logging.py` (log de auditoría) y `utils/errors.py` (handlers de excepción → formato de error uniforme) no pertenecen a una capa específica: se usan desde varios de los módulos de arriba. Por eso aparecen aparte en el diagrama, no dentro del flujo principal.

---

Para el paso a paso de una conversación completa (chat → triage → atención), ver [`imagenes/flujo.png`](imagenes/flujo.png). Para el detalle de cada endpoint, [`api.md`](api.md).
