from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str = "Medical Triage"

    API_VERSION: str = "1.0.0"

    DATABASE_URL: str

    LLM_API_KEY: str

    MODEL_NAME: str = "gmini-3b"

    TEMPERATURE: float = 0.2

    MAX_TOKENS: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()