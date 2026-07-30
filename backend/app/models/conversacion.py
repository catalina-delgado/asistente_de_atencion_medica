# Contexto del chatbot

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.models.paciente import Paciente
from app.models.mensaje import Mensaje
from .enums import RolMensaje


@dataclass
class Conversacion:
    session_id: str = field(default_factory=lambda: str(uuid4()))
    historial: list[Mensaje] = field(default_factory=list)
    paciente: Paciente | None = None
    creada_en: datetime = field(default_factory=datetime.utcnow)
    actualizada_en: datetime = field(default_factory=datetime.utcnow)

    # Propiedad que devuelve los sintomas acumulados del paciente en la conversacion
    @property
    def sintomas_acumulados(self) -> str:
        return " \n ".join(
            m.contenido for m in self.historial if m.rol == RolMensaje.PACIENTE
        )

    # Agrega un turno a la conversacion y actualiza la marca de tiempo
    def agregar_turno(self, rol: RolMensaje, contenido: str) -> None:
        self.historial.append(Mensaje(rol=rol, contenido=contenido))
        self.actualizada_en = datetime.utcnow()

    # Agrega un turno del paciente a la conversacion
    def agregar_turno_paciente(self, contenido: str) -> None:
        self.agregar_turno(RolMensaje.PACIENTE, contenido)