from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from models.mensaje import Mensaje
from models.paciente import Paciente


class IntakeReply(BaseModel):
    respuesta: str
    preguntas: list[str] = Field(default_factory=list)
    listo: bool = False


class TriageSuggestion(BaseModel):
    triage: str  # "I" | "II" | "III" | "IV"
    justificacion: str


class LLMAdapter(ABC):
    """Contrato de alto nivel: cada método corresponde a una responsabilidad
    clínica concreta, no a una llamada genérica de chat. Esto permite que el
    proveedor "mock" implemente lógica basada en reglas sin necesidad de
    simular una API de LLM real."""

    provider_name: str

    @abstractmethod
    async def responder_intake(
        self, *, historial: list[Mensaje], sintomas_acumulados: str
    ) -> IntakeReply:
        """Genera la respuesta conversacional y, si falta información,
        preguntas de seguimiento. `listo=True` indica que ya hay suficiente
        información para clasificar el triage."""

    @abstractmethod
    async def generar_resumen_clinico(
        self,
        *,
        sintomas_acumulados: str,
        paciente: Paciente | None,
        contexto_protocolos: str,
    ) -> str:
        """Genera un resumen clínico breve en tercera persona, estilo nota
        de enfermería, a partir de los síntomas reportados."""

    @abstractmethod
    async def sugerir_triage(
        self, *, sintomas_acumulados: str, contexto_protocolos: str
    ) -> TriageSuggestion:
        """Sugiere un nivel de triage (I-IV) con su justificación. Esta sugerencia
        NUNCA se usa sola: el servicio de triage siempre la combina con el motor de
        reglas de banderas de alarma (`app/clinical/triage_rules.py`) tomando el
        nivel más urgente entre ambos, de modo que el LLM solo puede escalar la
        prioridad, nunca reducirla por debajo de lo que indican las reglas."""

    @abstractmethod
    async def generar_recomendaciones(
        self, *, triage: str, resumen_clinico: str
    ) -> list[str]:
        """Genera recomendaciones de enfermería acordes al nivel de triage."""