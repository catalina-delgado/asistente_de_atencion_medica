from app.models.atencion import AtencionMedica
from app.models.conversacion import Conversacion
from app.models.enums import RolMensaje
from app.models.paciente import Paciente
from app.repositories.attention_repository import AttentionRepository
from app.schemas.attentionResponse import AttentionResponse
from app.services.triage_service import TriageService


class AtencionService:
    def __init__(self, triage_service: TriageService, repository: AttentionRepository):
        self._triage_service = triage_service
        self._repository = repository

    async def generar(
        self,
        *,
        session_id: str | None,
        sintomas: str | None,
        paciente: Paciente | None,
    ) -> AttentionResponse:

        # Recuperar conversación
        conversacion = self._triage_service.resolver_conversacion(
            session_id=session_id,
            sintomas=sintomas,
            paciente=paciente,
        )

        # Ejecutar clasificación
        resultado, recomendaciones = await self._triage_service.clasificar(conversacion)

        # Crear entidad de dominio
        atencion = AtencionMedica(
            session_id=conversacion.session_id,
            paciente=conversacion.paciente,
            motivo_consulta=resultado["resumenClinico"],
            sintomas_reportados=self._extraer_sintomas(conversacion),
            preguntas_respuestas=self._extraer_preguntas_respuestas(conversacion),
            triage=resultado["triage"],
            prioridad=resultado["prioridad"],
            especialidad_sugerida=resultado["especialidadSugerida"],
            resumen_clinico=resultado["resumenClinico"],
            banderas_alarma=resultado["banderasDeAlarma"],
            recomendaciones=recomendaciones,
        )

        # Persistir
        self._repository.guardar(atencion)

        # Convertir a respuesta
        return AttentionResponse(
            atencionId=atencion.atencion_id,
            sessionId=atencion.session_id,
            fechaCreacion=atencion.fecha_creacion,
            paciente=atencion.paciente or Paciente(),
            motivoConsulta=atencion.motivo_consulta,
            sintomasReportados=atencion.sintomas_reportados,
            preguntasYRespuestas=atencion.preguntas_respuestas,
            triage=atencion.triage,
            prioridad=atencion.prioridad,
            especialidadSugerida=atencion.especialidad_sugerida,
            resumenClinico=atencion.resumen_clinico,
            banderasDeAlarma=atencion.banderas_alarma,
            recomendacionesEnfermeria=atencion.recomendaciones,
        )

    @staticmethod
    def _extraer_sintomas(conversacion: Conversacion) -> list[str]:
        """
        Temporalmente retorna todos los mensajes del paciente.
        En el futuro deberá usar los síntomas estructurados extraídos
        durante el flujo conversacional.
        """
        return [
            mensaje.contenido
            for mensaje in conversacion.historial
            if mensaje.rol == RolMensaje.PACIENTE
        ]

    @staticmethod
    def _extraer_preguntas_respuestas(
        conversacion: Conversacion,
    ) -> list[dict[str, str]]:

        pares: list[dict[str, str]] = []
        pregunta: str | None = None

        for turno in conversacion.historial:

            if turno.rol == RolMensaje.ASISTENTE:
                pregunta = turno.contenido

            elif turno.rol == RolMensaje.PACIENTE and pregunta:
                pares.append(
                    {
                        "pregunta": pregunta,
                        "respuesta": turno.contenido,
                    }
                )
                pregunta = None

        return pares