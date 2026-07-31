from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Emermedica Triage Assistant"
    env: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    # Gemini es el único proveedor de LLM soportado. Sin GEMINI_API_KEY
    # configurada, app/llm/factory.py falla al arrancar (fail-fast) en vez
    # de degradar en silencio a un motor sin LLM real.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    llm_timeout_seconds: float = 20.0

    session_ttl_minutes: int = 60

    # Token bearer requerido en el header Authorization para consumir /chat,
    # /triage y /atencion. Sin él configurado, el servidor rechaza esas
    # rutas (fail closed) en vez de dejarlas abiertas por descuido.
    api_token: str | None = None

    # Ruta relativa al directorio desde donde se ejecuta el proceso (por
    # convención, siempre "backend/", que es donde vive requirements.txt/.env).
    audit_log_path: str = "logs/audit.log"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()