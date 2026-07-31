# Decisiones técnicas

## El motor de reglas de triage nunca cede autoridad al LLM

`app/clinical/triage_rules.py` clasifica por banderas de alarma (palabras clave) de forma completamente independiente del LLM. `TriageService` siempre toma el **nivel más urgente** entre la sugerencia del LLM y la del motor de reglas (`more_urgent`) — el LLM puede escalar la urgencia, nunca reducirla por debajo de lo que indican las reglas.

**Por qué:** es un asistente clínico; un falso negativo (subestimar urgencia) es mucho más costoso que un falso positivo. Las reglas actúan como red de seguridad determinista sobre un componente probabilístico (el LLM).

## Proveedor de LLM con fallback automático a `mock`

`Settings.active_provider()` (`app/config/settings.py`) hace que si `LLM_PROVIDER=gemini` pero no hay `GEMINI_API_KEY` configurada, la app use `mock` automáticamente en vez de fallar.

**Por qué:** permite levantar el proyecto sin depender de credenciales externas. 

## Dos stores en memoria, no en base de datos (todavía)

`app/database/` tiene dos implementaciones separadas: `InMemorySessionStore` (conversaciones, con TTL) y `InMemoryAttentionStore` (atenciones, sin TTL). Cada `Repository` (`ConversationRepository`, `AttentionRepository`) recibe el suyo por constructor. 

**Por qué dos stores y no uno genérico:** tienen ciclos de vida distintos a propósito. Una conversación abandonada es estado efímero — tiene sentido que expire. Una atención ya generada es un registro clínico — no debería desaparecer solo por tiempo. 

**Por qué en memoria y no Postgres:** el diseño de `app/repositories/` ya aísla el acceso a datos detrás de una interfaz mínima (`guardar`/`obtener`, `crear`/`obtener`), así que migrar a Postgres más adelante implica cambiar la implementación de cada store, no los servicios que los consumen. Mientras tanto, evita la complejidad operativa de una base de datos para un flujo que no la necesitaba todavía.

**Implicación a tener en cuenta:** las conversaciones y las atenciones se pierden al reiniciar el contenedor del backend — incluidas las atenciones, pese a que conceptualmente son registros permanentes. No apto para producción sin implementar la persistencia real, sobre todo para `InMemoryAttentionStore`.

## Autenticación: token bearer estático, no login de usuarios

`app/api/auth.py` valida un único `API_TOKEN` compartido contra el header `Authorization: Bearer`, aplicado solo a `/chat`, `/triage` y `/atencion` (no a `/` ni `/health`, que las necesita el healthcheck de Docker sin credenciales).

**Por qué:** forma simple de dejar de tener la API completamente abierta. Fail-closed por diseño: si el servidor no tiene `API_TOKEN` configurado, rechaza todo en vez de dejar las rutas abiertas por descuido.


## Config del frontend vía build-args, no runtime

`VITE_API_BASE_URL` y `VITE_API_TOKEN` se inyectan en `frontend/Dockerfile` como `ARG`/`ENV` en tiempo de build, no se leen del contenedor en tiempo de ejecución.

**Por qué:** es el patrón estándar para una SPA estática servida por nginx — más simple que generar un `config.js` en el arranque del contenedor vía `envsubst`.

**Trade-off aceptado:** la misma imagen Docker no se puede reutilizar en distintos entornos (dev/staging/prod) sin reconstruirla, porque la URL del backend y el token quedan fijos en el bundle. Si en algún momento se necesita "build once, deploy anywhere" (una sola imagen desplegable en cualquier servidor sin recompilar), hay que migrar a inyección de config en runtime.

