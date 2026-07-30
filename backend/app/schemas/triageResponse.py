from pydantic import BaseModel, Field
from app.models.enums import NivelTriage

class TriageResponse(BaseModel):
    sessionId: str
    triage: NivelTriage
    prioridad: str
    especialidadSugerida: str
    resumenClinico: str
    banderasDeAlarma: list[str] = Field(default_factory=list)
    recomendacionInicial: str
    requiereAtencionInmediata: bool