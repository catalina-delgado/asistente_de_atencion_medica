# Memoria de conversaciones de pacientes.

import time
from models.conversacion import Conversacion
from models.paciente import Paciente
from config.settings import get_settings


class InMemorySessionStore:
    def __init__(self, ttl_minutes: int = 60):
        self._data: dict[str, Conversacion] = {}
        self._ttl_seconds = ttl_minutes * 60

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [sid for sid, c in self._data.items() if now - c.actualizada_en > self._ttl_seconds]
        for sid in expired:
            del self._data[sid]

    def create(self, paciente: Paciente | None = None) -> Conversacion:
        self._purge_expired()
        conversacion = Conversacion(paciente=paciente)
        self._data[conversacion.session_id] = conversacion
        return conversacion

    def get(self, session_id: str) -> Conversacion | None:
        self._purge_expired()
        return self._data.get(session_id)


_store: InMemorySessionStore | None = None


def get_session_store() -> InMemorySessionStore:
    """Singleton a nivel de proceso. FastAPI lo obtiene vía dependencia
    (ver app/api/deps.py) para que sea fácil sustituirlo en tests."""
    global _store
    if _store is None:
        _store = InMemorySessionStore(ttl_minutes=get_settings().session_ttl_minutes)
    return _store