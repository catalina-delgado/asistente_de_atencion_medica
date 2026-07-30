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
from asistente.backend.app.utils.errors import LLMProviderError


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
            raise LLMProviderError(f"Gemini: error de API ({exc})") from exc
        except (IndexError, AttributeError) as exc:
            raise LLMProviderError(f"Gemini: respuesta con formato inesperado ({exc})") from exc

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
        self, *, sintomas_acumulados: str, paciente: Paciente | None, contexto_protocolos: str
    ) -> str:
        datos_paciente = {"edad": paciente.edad, "sexo": paciente.sexo} if paciente else "no proporcionados"
        contenido = (
            f"Síntomas reportados: {sintomas_acumulados}\n"
            f"Datos del paciente: {datos_paciente}\n"
            f"Contexto de protocolos relevante:\n{contexto_protocolos or 'N/A'}"
        )
        return (await self._complete(system=RESUMEN_SYSTEM_PROMPT, messages=[{"role": "user", "content": contenido}])).strip()

    async def sugerir_triage(self, *, sintomas_acumulados: str, contexto_protocolos: str) -> TriageSuggestion:
        contenido = f"Síntomas: {sintomas_acumulados}\nProtocolos relevantes:\n{contexto_protocolos or 'N/A'}"
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