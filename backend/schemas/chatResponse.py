from dataclasses import Field
from pydantic import BaseModel


class ChatResponse(BaseModel):
    sessionId: str
    respuesta: str
    preguntasSeguimiento: list[str] = Field(default_factory=list)
    listoParaTriage: bool = Field(
        default=False, description="True cuando el asistente ya reunió suficiente información."
    )
    turno: int
    