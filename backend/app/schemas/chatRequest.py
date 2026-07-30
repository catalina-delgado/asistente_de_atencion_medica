from dataclasses import Field
from pydantic import BaseModel
from models.paciente import Patient

class ChatRequest(BaseModel):
    sessionId: str | None = Field(default=None, description="Si se omite, se crea una sesión nueva.")
    mensaje: str = Field(..., min_length=1, max_length=4000)
    paciente: Patient | None = None


