from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.llm.base import IntakeReply, LLMAdapter, TriageSuggestion
from app.models.enums import RolMensaje
from app.models.mensaje import Mensaje
from app.models.paciente import Paciente
from app.llm.prompts import (
    INTAKE_SYSTEM_PROMPT,
    RECOMENDACIONES_SYSTEM_PROMPT,
    RESUMEN_SYSTEM_PROMPT,
    TRIAGE_SYSTEM_PROMPT,
    extract_json,
)
from app.utils.errors import LLMProviderError


class GeminiAdapter(LLMAdapter):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str, timeout_seconds: float):
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        )
        self._model = model

    async def _complete(self, *, system: str, messages: list[dict[str, str]]) -> str:
        contents = [
            types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part(text=m["content"])],
            )
            for m in messages
        ]
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0.2),
            )
            return response.text or ""
        except APIError as exc:
            raise self._traducir_error(exc) from exc
        except (IndexError, AttributeError) as exc:
            raise LLMProviderError(f"Gemini: respuesta con formato inesperado ({exc})") from exc

    def _traducir_error(self, exc: APIError) -> LLMProviderError:
        """Traduce un error real de la API de Gemini (con su código y status,
        ver google.genai.errors.APIError) a un LLMProviderError con el HTTP
        status y el mensaje de usuario adecuados, en vez de devolver siempre
        el mismo 502 genérico sin importar la causa real."""
        detalle = f"Gemini: error de API ({exc})"

        if exc.code == 503 or exc.status == "UNAVAILABLE":
            return LLMProviderError(
                detalle,
                http_status=503,
                user_message=(
                    f"El modelo de IA ({self._model}) no está disponible en este momento "
                    "por alta demanda del proveedor. Intenta de nuevo en unos segundos."
                ),
            )

        if exc.code == 404 or exc.status == "NOT_FOUND":
            return LLMProviderError(
                detalle,
                http_status=502,
                user_message=(
                    f"El modelo configurado ({self._model}) no existe o no está disponible "
                    "para esta API key. Revisa la variable GEMINI_MODEL."
                ),
            )

        if exc.code == 429 or exc.status == "RESOURCE_EXHAUSTED":
            return LLMProviderError(
                detalle,
                http_status=429,
                user_message=(
                    "Se alcanzó el límite de solicitudes al proveedor de IA "
                    f"({self._model}). Intenta de nuevo más tarde."
                ),
            )

        return LLMProviderError(detalle)

    async def responder_intake(self, *, historial: list[Mensaje], sintomas_acumulados: str) -> IntakeReply:
        messages = [
            {"role": "user" if t.rol == RolMensaje.PACIENTE else "assistant", "content": t.contenido}
            for t in historial
        ]
        messages.append({"role": "user", "content": f"Síntomas acumulados: {sintomas_acumulados}"})
        raw = await self._complete(system=INTAKE_SYSTEM_PROMPT, messages=messages)
        try:
            return IntakeReply(**extract_json(raw))
        except Exception as exc:
            raise LLMProviderError(f"Gemini: no se pudo interpretar la respuesta de intake ({exc})") from exc

    async def generar_resumen_clinico(
        self,
        *,
        sintomas_acumulados: str,
        paciente: Paciente | None,
        contexto_protocolos: str,
        banderas_detectadas: list[str],
    ) -> str:
        datos_paciente = {"edad": paciente.edad, "sexo": paciente.sexo} if paciente else "no proporcionados"
        banderas_texto = ", ".join(banderas_detectadas) if banderas_detectadas else "ninguna detectada"
        contenido = (
            f"Síntomas reportados: {sintomas_acumulados}\n"
            f"Datos del paciente: {datos_paciente}\n"
            f"Banderas de alarma ya detectadas por el motor de reglas: {banderas_texto}\n"
            f"Contexto de protocolos relevante:\n{contexto_protocolos or 'N/A'}"
        )
        return (await self._complete(system=RESUMEN_SYSTEM_PROMPT, messages=[{"role": "user", "content": contenido}])).strip()

    async def sugerir_triage(
        self,
        *,
        sintomas_acumulados: str,
        contexto_protocolos: str,
        banderas_detectadas: list[str],
        razonamiento_reglas: str,
    ) -> TriageSuggestion:
        banderas_texto = ", ".join(banderas_detectadas) if banderas_detectadas else "ninguna"
        contenido = (
            f"Síntomas: {sintomas_acumulados}\n"
            f"Protocolos relevantes:\n{contexto_protocolos or 'N/A'}\n"
            f"Banderas de alarma ya detectadas por el motor de reglas: {banderas_texto}\n"
            f"Razonamiento del motor de reglas: {razonamiento_reglas}"
        )
        raw = await self._complete(system=TRIAGE_SYSTEM_PROMPT, messages=[{"role": "user", "content": contenido}])
        try:
            return TriageSuggestion(**extract_json(raw))
        except Exception as exc:
            raise LLMProviderError(f"Gemini: no se pudo interpretar la sugerencia de triage ({exc})") from exc

    async def generar_recomendaciones(self, *, triage: str, resumen_clinico: str) -> list[str]:
        contenido = f"Triage: {triage}\nResumen clínico: {resumen_clinico}"
        raw = await self._complete(system=RECOMENDACIONES_SYSTEM_PROMPT, messages=[{"role": "user", "content": contenido}])
        try:
            return list(extract_json(raw).get("recomendaciones", []))
        except Exception as exc:
            raise LLMProviderError(f"Gemini: no se pudo interpretar recomendaciones ({exc})") from exc