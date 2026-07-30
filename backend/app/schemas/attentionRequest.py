from app.models.paciente import Paciente
from pydantic import BaseModel, Field


class AttentionRequest(BaseModel):
    sessionId: str | None = None
    sintomas: str | None = Field(default=None, max_length=4000)
    paciente: Paciente | None = None