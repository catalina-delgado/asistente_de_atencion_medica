import datetime
from models.enums import NivelTriage
from models.paciente import Patient
from pydantic import BaseModel


class AtentionResponse(BaseModel):
    atencionId: str
    sessionId: str
    fechaCreacion: datetime
    paciente: Patient
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