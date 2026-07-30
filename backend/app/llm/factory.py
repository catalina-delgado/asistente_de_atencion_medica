from app.config.settings import Settings
from app.llm.base import LLMAdapter
from app.llm.gemini import GeminiAdapter
from app.llm.mock import MockAdapter


def build_llm_adapter(settings: Settings) -> LLMAdapter:
    provider = settings.active_provider()

    if provider == "gemini":
        return GeminiAdapter(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    return MockAdapter()