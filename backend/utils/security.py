import html
import re
import uuid

MAX_MESSAGE_LENGTH = 4000
MIN_MESSAGE_LENGTH = 1


# Campos que se consideran información de identificación personal (PII) o
# clínica sensible y que deben enmascararse antes de escribirse en logs.
_SENSITIVE_KEYS = {"nombre", "documento", "identificacion", "telefono", "direccion", "email"}


class InputValidationError(ValueError):
    """Se lanza cuando una entrada de usuario no pasa las validaciones básicas."""


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


# Utilidad para sanitizar texto de entrada, eliminando espacios en blanco, validando longitud y escapando HTML
def sanitize_text(raw: str, *, field_name: str = "mensaje") -> str:
    if raw is None:
        raise InputValidationError(f"El campo '{field_name}' es obligatorio.")

    text = raw.strip()
    if len(text) < MIN_MESSAGE_LENGTH:
        raise InputValidationError(f"El campo '{field_name}' no puede estar vacío.")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise InputValidationError(
            f"El campo '{field_name}' supera el máximo permitido de {MAX_MESSAGE_LENGTH} caracteres."
        )

    text = html.escape(text, quote=False)

    return text


# Utilidad para enmascarar informacion sensible en diccionarios
def mask_sensitive(data: dict) -> dict:
    masked = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            masked[key] = "***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive(value)
        else:
            masked[key] = value
    return masked


# Utilidad para truncar texto largo en logs de auditoria, evitando exponer informacion sensible
def truncate_for_audit(text: str, *, max_chars: int = 120) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…[truncado]"