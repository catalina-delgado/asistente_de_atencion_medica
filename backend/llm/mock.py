from clinical.triage_rules import classify_by_rules
from llm.base import IntakeReply, LLMAdapter, TriageSuggestion
from models.enums import RolMensaje
from models.mensaje import Mensaje
from models.paciente import Paciente

_RECOMENDACIONES_POR_TRIAGE: dict[str, list[str]] = {
    "I": [
        "Buscar atención de urgencias de inmediato o llamar a la línea de emergencias.",
        "No conducir usted mismo; solicitar ayuda o una ambulancia.",
        "Mantener a la persona en reposo y acompañada mientras llega la ayuda.",
    ],
    "II": [
        "Acudir a un servicio de urgencias en las próximas horas.",
        "Mantenerse hidratado y en reposo mientras es atendido.",
        "Buscar ayuda inmediata si los síntomas empeoran (dificultad para respirar, confusión, dolor intenso).",
    ],
    "III": [
        "Programar una consulta médica en las próximas 24-48 horas.",
        "Controlar la temperatura y los síntomas; mantenerse hidratado.",
        "Consultar antes si aparecen signos de alarma (fiebre muy alta, dificultad respiratoria, dolor intenso).",
    ],
    "IV": [
        "Puede manejar los síntomas con medidas generales en casa (hidratación, reposo).",
        "Si los síntomas persisten más de 5-7 días o empeoran, agendar una consulta médica.",
        "No es necesario acudir a urgencias salvo que aparezcan nuevas señales de alarma.",
    ],
}

_PREGUNTAS_SEGUIMIENTO = [
    "¿Desde hace cuánto tiempo presentas estos síntomas?",
    "En una escala de 1 a 10, ¿qué tan intenso es el malestar?",
    "¿Tienes algún otro síntoma asociado (fiebre, mareo, náuseas, dificultad para respirar)?",
]


class MockAdapter(LLMAdapter):
    provider_name = "mock"

    async def responder_intake(self, *, historial: list[Mensaje], sintomas_acumulados: str) -> IntakeReply:
        turnos_paciente = sum(1 for t in historial if t.rol == RolMensaje.PACIENTE)

        if turnos_paciente == 0:
            return IntakeReply(
                respuesta=(
                    "Entiendo, gracias por contarme. Para orientar mejor tu atención "
                    "necesito un par de datos adicionales."
                ),
                preguntas=_PREGUNTAS_SEGUIMIENTO,
                listo=False,
            )

        return IntakeReply(
            respuesta=(
                "Gracias por la información adicional. Con esto ya puedo evaluar el "
                "nivel de prioridad de tu atención."
            ),
            preguntas=[],
            listo=True,
        )

    async def generar_resumen_clinico(
        self, *, sintomas_acumulados: str, paciente: Paciente | None, contexto_protocolos: str
    ) -> str:
        descripcion_paciente = "Paciente"
        if paciente and paciente.edad is not None:
            descripcion_paciente += f" de {paciente.edad} años"
        if paciente and paciente.sexo:
            descripcion_paciente += f", sexo {paciente.sexo}"

        resumen = f"{descripcion_paciente} que refiere: {sintomas_acumulados.strip()}."
        if contexto_protocolos:
            resumen += " El caso fue contrastado con los protocolos internos de triage disponibles."
        return resumen

    async def sugerir_triage(self, *, sintomas_acumulados: str, contexto_protocolos: str) -> TriageSuggestion:
        # Sin LLM real disponible, la "sugerencia" es directamente el resultado
        # del motor de reglas: mantiene el sistema evaluable end-to-end y
        # coherente con los 4 casos de prueba del enunciado.
        clasificacion = classify_by_rules(sintomas_acumulados)
        return TriageSuggestion(triage=clasificacion.triage, justificacion=clasificacion.razonamiento)

    async def generar_recomendaciones(self, *, triage: str, resumen_clinico: str) -> list[str]:
        return list(_RECOMENDACIONES_POR_TRIAGE.get(triage, _RECOMENDACIONES_POR_TRIAGE["III"]))