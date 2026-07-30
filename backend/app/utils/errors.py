import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.security import InputValidationError, new_request_id
from app.utils.logging import audit_event

logger = logging.getLogger("app")


class LLMProviderError(Exception):
    """Error al comunicarse con el proveedor de LLM (timeout, 4xx/5xx, etc.)."""


class SessionNotFoundError(Exception):
    """La sesión de conversación referenciada no existe o expiró."""


def _error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "requestId": request_id}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InputValidationError)
    async def handle_input_validation(request: Request, exc: InputValidationError):
        request_id = getattr(request.state, "request_id", new_request_id())
        audit_event("input_validation_error", request_id=request_id, detail=str(exc))
        return _error_response(status.HTTP_400_BAD_REQUEST, "INVALID_INPUT", str(exc), request_id)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", new_request_id())
        audit_event("request_validation_error", request_id=request_id, detail=exc.errors())
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "INVALID_REQUEST",
            "El cuerpo de la petición no tiene el formato esperado.",
            request_id,
        )

    @app.exception_handler(SessionNotFoundError)
    async def handle_session_not_found(request: Request, exc: SessionNotFoundError):
        request_id = getattr(request.state, "request_id", new_request_id())
        audit_event("session_not_found", request_id=request_id, detail=str(exc))
        return _error_response(status.HTTP_404_NOT_FOUND, "SESSION_NOT_FOUND", str(exc), request_id)

    @app.exception_handler(LLMProviderError)
    async def handle_llm_error(request: Request, exc: LLMProviderError):
        request_id = getattr(request.state, "request_id", new_request_id())
        logger.error("Fallo del proveedor LLM [%s]: %s", request_id, exc)
        audit_event("llm_provider_error", request_id=request_id, detail=str(exc))
        return _error_response(
            status.HTTP_502_BAD_GATEWAY,
            "LLM_PROVIDER_ERROR",
            "El asistente no pudo procesar la solicitud en este momento. Intenta nuevamente.",
            request_id,
        )