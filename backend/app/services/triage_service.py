from app.clinical.rag_retriever import RetrievedProtocol, render_context, retrieve
from app.clinical.triage_rules import PRIORIDAD_POR_TRIAGE, classify_by_rules, more_urgent
from app.llm.base import LLMAdapter
from app.models.conversacion import Conversacion
from app.models.paciente import Paciente
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.triageResponse import TriageResponse
from app.utils.errors import SessionNotFoundError
from app.utils.security import InputValidationError, sanitize_text

_VALID_LEVELS = {"I", "II", "III", "IV"}


class TriageService:
    def __init__(self, llm: LLMAdapter, repo: ConversationRepository):
        self._llm = llm
        self._repo = repo

    def resolver_conversacion(
        self, session_id: str | None, sintomas: str | None, paciente: Paciente | None
    ) -> Conversacion:
        if session_id:
            conversacion = self._repo.obtener(session_id)
            if conversacion is None:
                raise SessionNotFoundError(f"La sesión '{session_id}' no existe o expiró.")
            if sintomas:
                conversacion.agregar_turno_paciente(sanitize_text(sintomas, field_name="sintomas"))
            if paciente:
                conversacion.paciente = paciente
            return conversacion

        if not sintomas:
            raise InputValidationError(
                "Debes indicar 'sessionId' (de una conversación previa) o 'sintomas'."
            )
        conversacion = self._repo.crear(paciente=paciente)
        conversacion.agregar_turno_paciente(sanitize_text(sintomas, field_name="sintomas"))
        return conversacion

    async def clasificar(self, conversacion: Conversacion) -> tuple[dict, list[str]]:
        """Devuelve (resultado, recomendaciones). `resultado` es un dict simple
        (no una clase de modelo) porque es solo un valor de paso interno entre
        este servicio y sus llamadores (`clasificar_sesion` y
        `AtencionService`); el único lugar donde ese resultado se convierte en
        un objeto tipado es en el esquema de respuesta correspondiente."""
        sintomas_acumulados = conversacion.sintomas_acumulados

        protocolos: list[RetrievedProtocol] = retrieve(sintomas_acumulados, top_k=2)
        contexto_protocolos = render_context(protocolos)

        regla = classify_by_rules(sintomas_acumulados)

        resumen = await self._llm.generar_resumen_clinico(
            sintomas_acumulados=sintomas_acumulados,
            paciente=conversacion.paciente,
            contexto_protocolos=contexto_protocolos,
            banderas_detectadas=regla.banderas,
        )

        sugerencia = await self._llm.sugerir_triage(
            sintomas_acumulados=sintomas_acumulados,
            contexto_protocolos=contexto_protocolos,
            banderas_detectadas=regla.banderas,
            razonamiento_reglas=regla.razonamiento,
        )
        nivel_llm = sugerencia.triage if sugerencia.triage in _VALID_LEVELS else regla.triage
        nivel_final = more_urgent(nivel_llm, regla.triage)

        recomendaciones = await self._llm.generar_recomendaciones(
            triage=nivel_final, resumen_clinico=resumen
        )

        resultado = {
            "triage": nivel_final,
            "prioridad": PRIORIDAD_POR_TRIAGE[nivel_final],
            "especialidadSugerida": regla.especialidad,
            "resumenClinico": resumen,
            "banderasDeAlarma": regla.banderas,
            "recomendacionInicial": recomendaciones[0] if recomendaciones else sugerencia.justificacion,
            "requiereAtencionInmediata": nivel_final == "I",
        }
        return resultado, recomendaciones

    async def clasificar_sesion(
        self, *, session_id: str | None, sintomas: str | None, paciente: Paciente | None
    ) -> TriageResponse:
        conversacion = self.resolver_conversacion(session_id, sintomas, paciente)
        resultado, _ = await self.clasificar(conversacion)
        return TriageResponse(sessionId=conversacion.session_id, **resultado)