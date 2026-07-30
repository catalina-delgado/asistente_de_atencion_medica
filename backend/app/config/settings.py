from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["gemini", "mock"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Emermedica Triage Assistant"
    env: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    # Proveedor de LLM activo. Si no hay API key configurada para el
    # proveedor elegido, la app cae automáticamente a "mock" (motor de
    # reglas) para poder seguir funcionando en desarrollo/pruebas.
    llm_provider: LLMProvider = "mock"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    llm_timeout_seconds: float = 20.0

    session_ttl_minutes: int = 60

    # Ruta relativa al directorio desde donde se ejecuta el proceso (por
    # convención, siempre "backend/", que es donde vive requirements.txt/.env).
    audit_log_path: str = "logs/audit.log"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def active_provider(self) -> LLMProvider:
        """Determina el proveedor realmente utilizable según las keys presentes."""
        key_by_provider = {
            "gemini": self.gemini_api_key,
        }
        if self.llm_provider != "mock" and not key_by_provider.get(self.llm_provider):
            return "mock"
        return self.llm_provider


@lru_cache
def get_settings() -> Settings:
    return Settings()