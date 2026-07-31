from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import get_settings
from app.utils.errors import UnauthorizedError

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Token bearer requerido para consumir el asistente.",
)


def require_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    expected = get_settings().api_token
    if not expected:
        raise UnauthorizedError("El servidor no tiene configurado un token de autenticación.")
    if credentials is None or credentials.credentials != expected:
        raise UnauthorizedError("Token de autenticación inválido o ausente.")
