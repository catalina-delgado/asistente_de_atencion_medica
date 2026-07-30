from pydantic import BaseModel, Field
from app.models.paciente import Paciente


class TriageRequest(BaseModel):
    sessionId: str | None = None
    sintomas: str | None = Field(
        default=None,
        max_length=4000,
        description="Texto libre opcional; si se omite se usa el historial de la sesión.",
    )
    paciente: Paciente | None = None

