import uuid
from datetime import datetime, timezone

from app.models.conversacion import Conversacion
from app.models.enums import RolMensaje
from app.models.paciente import Paciente
from app.schemas.attentionResponse import AttentionResponse
from app.services.triage_service import TriageService


class AtencionService:
    def __init__(self, triage_service: TriageService):
        self._triage_service = triage_service

    async def generar(
        self, *, session_id: str | None, sintomas: str | None, paciente: Paciente | None
    ) -> AttentionResponse:
        conversacion = self._triage_service.resolver_conversacion(session_id, sintomas, paciente)
        resultado, recomendaciones = await self._triage_service.clasificar(conversacion)

        motivo = conversacion.historial[0].contenido if conversacion.historial else (sintomas or "")

        return AttentionResponse(
            atencionId=f"AT-{uuid.uuid4().hex[:10].upper()}",
            sessionId=conversacion.session_id,
            fechaCreacion=datetime.now(timezone.utc),
            paciente=conversacion.paciente or Paciente(),
            motivoConsulta=motivo,
            sintomasReportados=[m.contenido for m in conversacion.historial if m.rol == RolMensaje.PACIENTE],
            preguntasYRespuestas=self._extraer_preguntas_respuestas(conversacion),
            triage=resultado["triage"],
            prioridad=resultado["prioridad"],
            especialidadSugerida=resultado["especialidadSugerida"],
            resumenClinico=resultado["resumenClinico"],
            banderasDeAlarma=resultado["banderasDeAlarma"],
            recomendacionesEnfermeria=recomendaciones,
        )

    @staticmethod
    def _extraer_preguntas_respuestas(conversacion: Conversacion) -> list[dict[str, str]]:
        pares: list[dict[str, str]] = []
        pregunta_pendiente: str | None = None
        for turno in conversacion.historial:
            if turno.rol == RolMensaje.ASISTENTE:
                pregunta_pendiente = turno.contenido
            elif turno.rol == RolMensaje.PACIENTE and pregunta_pendiente:
                pares.append({"pregunta": pregunta_pendiente, "respuesta": turno.contenido})
                pregunta_pendiente = None
        return pares