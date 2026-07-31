# Decisiones técnicas

Registro de decisiones de diseño relevantes, con su razonamiento. El objetivo es que quede explícito el *por qué*, no solo el *qué* (eso ya lo dice el código).

## El motor de reglas de triage nunca cede autoridad al LLM

`app/clinical/triage_rules.py` clasifica por banderas de alarma (palabras clave) de forma completamente independiente del LLM. `TriageService` siempre toma el **nivel más urgente** entre la sugerencia del LLM y la del motor de reglas (`more_urgent`) — el LLM puede escalar la urgencia, nunca reducirla por debajo de lo que indican las reglas.

**Por qué:** es un asistente clínico; un falso negativo (subestimar urgencia) es mucho más costoso que un falso positivo. Las reglas actúan como red de seguridad determinista sobre un componente probabilístico (el LLM).

## Proveedor de LLM con fallback automático a `mock`

`Settings.active_provider()` (`app/config/settings.py`) hace que si `LLM_PROVIDER=gemini` pero no hay `GEMINI_API_KEY` configurada, la app use `mock` automáticamente en vez de fallar.

**Por qué:** permite levantar el proyecto (local, CI, onboarding de un nuevo dev) sin depender de credenciales externas. El motor `mock` reutiliza el mismo `triage_rules.py`, así que el comportamiento clínico es coherente entre ambos proveedores, solo cambia la calidad conversacional del intake.

## Dos stores en memoria, no en base de datos (todavía)

`app/database/` tiene dos implementaciones separadas: `InMemorySessionStore` (conversaciones, con TTL) y `InMemoryAttentionStore` (atenciones, sin TTL). Cada `Repository` (`ConversationRepository`, `AttentionRepository`) recibe el suyo por constructor. `sqlalchemy`, `psycopg2-binary` y `alembic` están en `requirements.txt` pero **no están conectados a nada** hoy.

**Por qué dos stores y no uno genérico:** tienen ciclos de vida distintos a propósito. Una conversación abandonada es estado efímero — tiene sentido que expire. Una atención ya generada es un registro clínico — no debería desaparecer solo por tiempo. Iban a vivir en `app/database/` desde el inicio; que `AttentionRepository` tuviera su dict inline en `app/repositories/` (en vez de en `app/database/`) fue una inconsistencia de capas, no una decisión — se corrigió moviéndolo a `attention_store.py`.

**Por qué en memoria y no Postgres:** el diseño de `app/repositories/` ya aísla el acceso a datos detrás de una interfaz mínima (`guardar`/`obtener`, `crear`/`obtener`), así que migrar a Postgres más adelante implica cambiar la implementación de cada store, no los servicios que los consumen. Mientras tanto, evita la complejidad operativa de una base de datos para un flujo que no la necesitaba todavía.

**Implicación a tener en cuenta:** las conversaciones y las atenciones se pierden al reiniciar el contenedor del backend — incluidas las atenciones, pese a que conceptualmente son registros permanentes. No apto para producción sin implementar la persistencia real, sobre todo para `InMemoryAttentionStore`.

## Autenticación: token bearer estático, no login de usuarios

`app/api/auth.py` valida un único `API_TOKEN` compartido contra el header `Authorization: Bearer`, aplicado solo a `/chat`, `/triage` y `/atencion` (no a `/` ni `/health`, que las necesita el healthcheck de Docker sin credenciales).

**Por qué:** es la forma más simple de dejar de tener la API completamente abierta, adecuada para el estado actual del proyecto (sin sistema de usuarios/pacientes autenticados). Fail-closed por diseño: si el servidor no tiene `API_TOKEN` configurado, rechaza todo en vez de dejar las rutas abiertas por descuido.

**Limitación conocida:** el mismo token se embebe en el bundle JS del frontend en build-time (`VITE_API_TOKEN`), por lo tanto es visible para cualquiera que inspeccione el JS servido. No es control de acceso real frente a usuarios finales de un sitio público — solo evita que bots/scanners genéricos le peguen a la API sin más. Si el proyecto necesita distinguir usuarios o exponerse públicamente, esto debe reemplazarse por un login real (ej. OAuth/JWT por usuario).

## Config del frontend vía build-args, no runtime

`VITE_API_BASE_URL` y `VITE_API_TOKEN` se inyectan en `frontend/Dockerfile` como `ARG`/`ENV` en tiempo de build, no se leen del contenedor en tiempo de ejecución.

**Por qué:** es el patrón estándar para una SPA estática servida por nginx — más simple que generar un `config.js` en el arranque del contenedor vía `envsubst`.

**Trade-off aceptado:** la misma imagen Docker no se puede reutilizar en distintos entornos (dev/staging/prod) sin reconstruirla, porque la URL del backend y el token quedan fijos en el bundle. Si en algún momento se necesita "build once, deploy anywhere" (una sola imagen desplegable en cualquier servidor sin recompilar), hay que migrar a inyección de config en runtime.

## Dos archivos `.env` distintos (raíz y `backend/`)

`backend/.env` trae la config que consume el contenedor del backend en runtime (vía `env_file` en `docker-compose.yml`). El `.env` de la raíz solo existe para que Compose sustituya `${API_TOKEN}` como build-arg del frontend — Compose no lee `backend/.env` para eso.

**Por qué:** es la forma más directa de lograrlo con Docker Compose sin introducir scripts extra. El trade-off es que el mismo valor de `API_TOKEN` vive duplicado en dos archivos, que deben mantenerse sincronizados manualmente.

## El `.env` de la raíz estuvo trackeado en git

El commit inicial del repo incluía un `.env` en la raíz con una `GEMINI_API_KEY` real en texto plano. Se corrigió: se agregó `.env` a `.gitignore` y se destrackeó con `git rm --cached .env`.

**Por qué importa:** agregar un archivo a `.gitignore` **no** destrackea archivos que ya estaban en el índice de git — solo evita que se vuelvan a agregar. Cualquier secreto commiteado sigue en el historial de git aunque se borre después; si algún key llegó a subirse a un remoto compartido, debe rotarse, no solo borrarse.
