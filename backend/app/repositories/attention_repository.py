from app.models.atencion import AtencionMedica


class AttentionRepository:

    def __init__(self):
        self._store: dict[str, AtencionMedica] = {}

    def guardar(self, atencion: AtencionMedica):
        self._store[atencion.atencion_id] = atencion
        return atencion

    def obtener(self, atencion_id: str):
        return self._store.get(atencion_id)