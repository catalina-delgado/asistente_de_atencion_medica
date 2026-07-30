from fastapi import FastAPI

from api.routes import router
from config.settings import get_settings
from utils.errors import register_exception_handlers
from utils.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Asistente de IA para triage y creación de atención médica de Emermédica. "
            "No emite diagnósticos médicos; actúa como auxiliar de enfermería digital."
        ),
        version="0.1.0",
    )

    register_exception_handlers(app)
    app.include_router(router)

    return app


app = create_app()