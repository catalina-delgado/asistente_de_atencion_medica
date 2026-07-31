from app.config.settings import Settings
from app.llm.base import LLMAdapter
from app.llm.gemini import GeminiAdapter


def build_llm_adapter(settings: Settings) -> LLMAdapter:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY no está configurada. El asistente requiere un proveedor "
            "LLM real; configúrala en backend/.env antes de levantar el servicio."
        )
    return GeminiAdapter(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
