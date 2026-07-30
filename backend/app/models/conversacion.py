# Contexto del chatbot

from dataclasses import dataclass, field
from datetime import time
from uuid import UUID

from app.models.paciente import Paciente
from app.models.mensaje import Mensaje
from .enums import messageRole


@dataclass
class Conversacion:
    session_id: str = field(default_factory=lambda: str(UUID(int=UUID().hex)))
    historial: list[Mensaje] = field(default_factory=list)
    paciente: Paciente | None = None
    creada_en: float = field(default_factory=time.time)
    actualizada_en: float = field(default_factory=time.time)

    # Propiedad que devuelve los sintomas acumulados del paciente en la conversacion
    @property
    def sintomas_acumulados(self) -> str:
        return " \n ".join(
            m.contenido for m in self.historial if m.rol == messageRole.PACIENTE
        )

    # Agrega un turno a la conversacion y actualiza la marca de tiempo
    def agregar_turno(self, rol: messageRole, contenido: str) -> None:
        self.historial.append(Mensaje(rol=rol, contenido=contenido))
        self.actualizada_en = time.time()

    # Agrega un turno del paciente a la conversacion
    def agregar_turno_paciente(self, contenido: str) -> None:
        self.agregar_turno(messageRole.PACIENTE, contenido)