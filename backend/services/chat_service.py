from llm.base import LLMAdapter
from asistente.backend.repositories.conversation_repository import ConversationRepository
from models.enums import RolMensaje
from models.paciente import Patient
from schemas.chatResponse import ChatResponse
from utils.security import sanitize_text


class ChatService:
    def __init__(self, llm: LLMAdapter, repo: ConversationRepository):
        self._llm = llm
        self._repo = repo

    # Procesa un mensaje del paciente, generando una respuesta del asistente y actualizando la conversacion
    async def procesar_mensaje(self, *, session_id: str | None, mensaje: str, paciente: Patient | None) -> ChatResponse:
        mensaje_limpio = sanitize_text(mensaje, field_name="mensaje")

        conversacion = self._repo.obtener(session_id) if session_id else None
        if session_id and conversacion is None:
            raise ValueError(f"Conversación con session_id {session_id} no encontrada.")
        if conversacion is None:
            conversacion = self._repo.crear(paciente=paciente)
        elif paciente:
            conversacion.paciente = paciente

        # Agregar el mensaje del usuario a la conversación
        historial_previo = list(conversacion.historial)
        conversacion.agregar_turno(RolMensaje.PACIENTE, mensaje_limpio)

        respuesta = await self._llm.responder_intake(
            historial=historial_previo, sintomas_acumulados=conversacion.sintomas_acumulados
        )
        conversacion.agregar_turno(RolMensaje.ASISTENTE, respuesta.respuesta)

        return ChatResponse(
            sessionId=conversacion.session_id,
            respuesta=respuesta.respuesta,
            preguntasSeguimiento=respuesta.preguntas,
            listoParaTriage=respuesta.listo,
            turno=len(conversacion.historial),
        )