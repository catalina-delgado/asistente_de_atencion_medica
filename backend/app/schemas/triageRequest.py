from dataclasses import Field
from pydantic import BaseModel
from models.paciente import Patient


class TriageRequest(BaseModel):
    sessionId: str | None = None
    sintomas: str | None = Field(
        default=None,
        max_length=4000,
        description="Texto libre opcional; si se omite se usa el historial de la sesión.",
    )
    paciente: Patient | None = None

