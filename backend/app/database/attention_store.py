# Almacenamiento de atenciones médicas generadas.
# A diferencia de InMemorySessionStore, no tiene TTL: una atención ya
# generada es un registro, no un estado de sesión que deba expirar.

from app.models.atencion import AtencionMedica


class InMemoryAttentionStore:
    def __init__(self):
        self._data: dict[str, AtencionMedica] = {}

    def guardar(self, atencion: AtencionMedica) -> AtencionMedica:
        self._data[atencion.atencion_id] = atencion
        return atencion

    def obtener(self, atencion_id: str) -> AtencionMedica | None:
        return self._data.get(atencion_id)


_store: InMemoryAttentionStore | None = None


def get_attention_store() -> InMemoryAttentionStore:
    """Singleton a nivel de proceso. FastAPI lo obtiene vía dependencia
    (ver app/api/deps.py) para que sea fácil sustituirlo en tests."""
    global _store
    if _store is None:
        _store = InMemoryAttentionStore()
    return _store
