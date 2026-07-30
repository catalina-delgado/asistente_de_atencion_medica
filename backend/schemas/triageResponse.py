from dataclasses import Field
from pydantic import BaseModel
from models.triage import TriageLevel


class TriageResult(BaseModel):
    triage: TriageLevel
    prioridad: str
    especialidadSugerida: str
    resumenClinico: str
    banderasDeAlarma: list[str] = Field(default_factory=list)
    recomendacionInicial: str
    requiereAtencionInmediata: bool


class TriageResponse(TriageResult):
    sessionId: str