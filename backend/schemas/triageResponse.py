from dataclasses import Field
from pydantic import BaseModel
from models.enums import NivelTriage

class TriageResponse(BaseModel):
    sessionId: str
    triage: NivelTriage
    prioridad: str
    especialidadSugerida: str
    resumenClinico: str
    banderasDeAlarma: list[str] = Field(default_factory=list)
    recomendacionInicial: str
    requiereAtencionInmediata: bool