from dataclasses import Field
from app.models.paciente import Patient
from pydantic import BaseModel


class AtencionRequest(BaseModel):
    sessionId: str | None = None
    sintomas: str | None = Field(default=None, max_length=4000)
    paciente: Patient | None = None