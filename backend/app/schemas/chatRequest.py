from pydantic import BaseModel, Field
from app.models.paciente import Paciente

class ChatRequest(BaseModel):
    sessionId: str | None = Field(default=None, description="Si se omite, se crea una sesión nueva.")
    mensaje: str = Field(..., min_length=1, max_length=4000)
    paciente: Paciente | None = None


