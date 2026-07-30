from datetime import datetime
from app.models.enums import NivelTriage
from app.models.paciente import Paciente
from pydantic import BaseModel


class AttentionResponse(BaseModel):
    atencionId: str
    sessionId: str
    fechaCreacion: datetime
    paciente: Paciente
    motivoConsulta: str
    sintomasReportados: list[str]
    preguntasYRespuestas: list[dict[str, str]]
    triage: NivelTriage
    prioridad: str
    especialidadSugerida: str
    resumenClinico: str
    banderasDeAlarma: list[str]
    recomendacionesEnfermeria: list[str]
    disclaimer: str = (
        "Documento generado por un asistente de IA como apoyo a la clasificación y "
        "documentación clínica. No constituye un diagnóstico médico y debe ser "
        "validado por personal de salud calificado."
    )