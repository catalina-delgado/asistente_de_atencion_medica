from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.models.paciente import Paciente


@dataclass
class AtencionMedica:
    atencion_id: str = field(default_factory=lambda: f"AT-{uuid4().hex[:10].upper()}")
    session_id: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)

    paciente: Paciente | None = None
    motivo_consulta: str = ""
    sintomas_reportados: list[str] = field(default_factory=list)
    preguntas_respuestas: list[dict[str, str]] = field(default_factory=list)
    triage: str = ""
    prioridad: str = ""
    especialidad_sugerida: str = ""
    resumen_clinico: str = ""
    banderas_alarma: list[str] = field(default_factory=list)
    recomendaciones: list[str] = field(default_factory=list)