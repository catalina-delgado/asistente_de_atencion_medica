from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.utils.security import new_request_id
from app.api.routes import router
from app.config.settings import get_settings
from app.utils.errors import register_exception_handlers
from app.utils.logging import configure_logging


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = new_request_id()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    register_exception_handlers(app)
    app.include_router(router)



    return app


app = create_app()