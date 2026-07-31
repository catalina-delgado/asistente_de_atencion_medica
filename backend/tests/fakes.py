# Doble de prueba de LLMAdapter: determinista, sin red, sin costo de API.
# No es un "proveedor mock" de producción (ese se eliminó a propósito, ver
# docs/decisiones_tecnicas.md) — solo existe dentro de tests/.

from app.llm.base import IntakeReply, LLMAdapter, TriageSuggestion
from app.models.paciente import Paciente


class FakeLLMAdapter(LLMAdapter):
    provider_name = "fake-test-double"

    def __init__(self, triage_sugerido: str = "III", justificacion: str = "fake"):
        self.triage_sugerido = triage_sugerido
        self.justificacion = justificacion
        self.calls: list[dict] = []

    async def responder_intake(self, *, historial, sintomas_acumulados) -> IntakeReply:
        return IntakeReply(respuesta="ok", preguntas=[], listo=True)

    async def generar_resumen_clinico(
        self, *, sintomas_acumulados, paciente: Paciente | None, contexto_protocolos, banderas_detectadas
    ) -> str:
        self.calls.append(
            {
                "method": "generar_resumen_clinico",
                "banderas_detectadas": banderas_detectadas,
                "contexto_protocolos": contexto_protocolos,
            }
        )
        return f"Resumen de prueba. Banderas recibidas: {banderas_detectadas}"

    async def sugerir_triage(
        self, *, sintomas_acumulados, contexto_protocolos, banderas_detectadas, razonamiento_reglas
    ) -> TriageSuggestion:
        self.calls.append(
            {
                "method": "sugerir_triage",
                "banderas_detectadas": banderas_detectadas,
                "razonamiento_reglas": razonamiento_reglas,
            }
        )
        return TriageSuggestion(triage=self.triage_sugerido, justificacion=self.justificacion)

    async def generar_recomendaciones(self, *, triage, resumen_clinico) -> list[str]:
        self.calls.append({"method": "generar_recomendaciones", "triage": triage})
        return ["Recomendación de prueba 1", "Recomendación de prueba 2"]
