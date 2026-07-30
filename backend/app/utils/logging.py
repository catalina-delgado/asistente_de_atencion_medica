import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.config.settings import get_settings

_audit_logger: logging.Logger | None = None


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_audit_logger() -> logging.Logger:
    global _audit_logger
    if _audit_logger is not None:
        return _audit_logger

    settings = get_settings()
    log_path = Path(settings.audit_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        if settings.env != "production":
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter("[AUDIT] %(message)s"))
            logger.addHandler(stream_handler)

    _audit_logger = logger
    return logger


def audit_event(event: str, *, request_id: str, session_id: str | None = None, **fields) -> None:
    """Escribe un evento de auditoría estructurado (una línea JSON)."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "request_id": request_id,
        "session_id": session_id,
        **fields,
    }
    get_audit_logger().info(json.dumps(record, ensure_ascii=False))