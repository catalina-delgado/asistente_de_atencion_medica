# API

## Autenticación

`POST /chat`, `POST /triage` y `POST /atencion` requieren un header:

```
Authorization: Bearer <API_TOKEN>
```

El token se configura en `API_TOKEN` (`backend/.env`). Sin token configurado en el servidor, o con uno inválido/ausente en el request, la API responde **401**:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token de autenticación inválido o ausente.",
    "requestId": "..."
  }
}
```

`GET /` y `GET /health` **no** requieren token (el segundo lo usa el healthcheck de Docker).

## Formato de errores

Todas las respuestas de error siguen la misma forma:

```json
{ "error": { "code": "STRING", "message": "STRING", "requestId": "STRING" } }
```

| code                      | status | cuándo ocurre                                              |
| -------------------------- | ------ | ------------------------------------------------------------ |
| `INVALID_INPUT`            | 400    | Texto de entrada inválido (vacío, demasiado largo, etc.)    |
| `INVALID_REQUEST`          | 422    | El body no cumple el schema esperado                        |
| `UNAUTHORIZED`             | 401    | Token bearer ausente/inválido, o servidor sin token configurado |
| `SESSION_NOT_FOUND`        | 404    | `sessionId` no existe o expiró (`SESSION_TTL_MINUTES`)      |
| `LLM_PROVIDER_ERROR`       | 503    | Gemini sobrecargado por alta demanda (`UNAVAILABLE`) — el `message` incluye el modelo configurado |
| `LLM_PROVIDER_ERROR`       | 429    | Se agotó la cuota de la API de Gemini (`RESOURCE_EXHAUSTED`) |
| `LLM_PROVIDER_ERROR`       | 502    | El modelo configurado no existe (`NOT_FOUND`, revisar `GEMINI_MODEL`), timeout, error de red, u otro error del proveedor |

En los tres casos el `message` de la respuesta ya viene redactado para mostrarse directo al usuario (ver `GeminiAdapter._traducir_error()` en `app/llm/gemini.py`).

## Endpoints

### `GET /`

Metadata del servicio. Sin autenticación.

### `GET /health`

Healthcheck. Sin autenticación. Respuesta: `{"status": "ok"}`.

### `POST /chat`

Turno conversacional de intake (recolección de síntomas).

**Request**

```json
{
  "sessionId": null,
  "mensaje": "Tengo fiebre y dolor de cabeza desde ayer",
  "paciente": { "edad": 34, "sexo": "F", "nombre": "..." }
}
```

- `sessionId` — opcional. Si se omite, se crea una sesión nueva.
- `mensaje` — requerido, 1–4000 caracteres.
- `paciente` — opcional (`edad`, `sexo`: `M`|`F`|`Otro`, `nombre`).

**Response**

```json
{
  "sessionId": "uuid",
  "respuesta": "...",
  "preguntasSeguimiento": ["..."],
  "listoParaTriage": false,
  "turno": 2
}
```

`listoParaTriage: true` indica que ya se reunió suficiente información para llamar a `/triage`.

### `POST /triage`

Clasifica el nivel de triage de la sesión.

**Request**

```json
{
  "sessionId": "uuid",
  "sintomas": "Fiebre de 39C, dolor de cabeza intenso",
  "paciente": { "edad": 34, "sexo": "F" }
}
```

- `sintomas` — opcional; si se omite, usa el historial acumulado de la sesión (`sessionId` en ese caso es obligatorio).

**Response**

```json
{
  "sessionId": "uuid",
  "triage": "II",
  "prioridad": "Urgente",
  "especialidadSugerida": "Medicina General",
  "resumenClinico": "...",
  "banderasDeAlarma": ["Fiebre alta o prolongada"],
  "recomendacionInicial": "...",
  "requiereAtencionInmediata": false
}
```

`triage` es uno de `I` (emergencia inmediata) a `IV` (no urgente). El nivel resulta de tomar **el más urgente** entre la sugerencia del LLM y el motor de reglas de banderas de alarma — ver la sección "Clinical y LLM" en [`arquitectura.md`](arquitectura.md).

### `POST /atencion`

Genera el documento final de atención (incluye triage + resumen + recomendaciones).

**Request:** igual que `/triage`.

**Response**

```json
{
  "atencionId": "AT-XXXXXXXXXX",
  "sessionId": "uuid",
  "fechaCreacion": "2026-07-30T23:17:42.234579",
  "paciente": { "edad": 34, "sexo": "F", "nombre": "..." },
  "motivoConsulta": "...",
  "sintomasReportados": ["..."],
  "preguntasYRespuestas": [],
  "triage": "II",
  "prioridad": "Urgente",
  "especialidadSugerida": "Medicina General",
  "resumenClinico": "...",
  "banderasDeAlarma": ["..."],
  "recomendacionesEnfermeria": ["..."],
  "disclaimer": "Documento generado por un asistente de IA como apoyo a la clasificación y documentación clínica. No constituye un diagnóstico médico y debe ser validado por personal de salud calificado."
}
```
