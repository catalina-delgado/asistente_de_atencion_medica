# controlador de la memoria de conversaciones de pacientes

from app.database.session_store import InMemorySessionStore
from app.models.conversacion import Conversacion
from app.models.paciente import Paciente


class ConversacionRepository:
    def __init__(self, store: InMemorySessionStore):
        self._store = store

    def crear(self, paciente: Paciente | None = None) -> Conversacion:
        return self._store.create(paciente=paciente)

    def obtener(self, session_id: str) -> Conversacion | None:
        return self._store.get(session_id)