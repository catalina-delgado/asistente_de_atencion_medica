from app.database.attention_store import InMemoryAttentionStore
from app.models.atencion import AtencionMedica


class AttentionRepository:
    def __init__(self, store: InMemoryAttentionStore):
        self._store = store

    def guardar(self, atencion: AtencionMedica) -> AtencionMedica:
        return self._store.guardar(atencion)

    def obtener(self, atencion_id: str) -> AtencionMedica | None:
        return self._store.obtener(atencion_id)
