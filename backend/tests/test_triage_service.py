import asyncio

from pytest_html import extras as html_extras

from app.database.session_store import InMemorySessionStore
from app.repositories.conversation_repository import ConversationRepository
from app.services.triage_service import TriageService
from tests.fakes import FakeLLMAdapter


def _make_service(triage_sugerido: str = "III") -> tuple[TriageService, FakeLLMAdapter]:
    repo = ConversationRepository(InMemorySessionStore())
    llm = FakeLLMAdapter(triage_sugerido=triage_sugerido)
    return TriageService(llm=llm, repo=repo), llm


def _tabla_fusion(sintomas: str, triage_llm: str, respuesta) -> str:
    return f"""
    <table style="font-size:0.85em; border-collapse:collapse;">
      <tr><th style="text-align:left; padding-right:8px;">Síntomas reportados</th><td>{sintomas}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Sugerencia del LLM (fake)</th><td>{triage_llm}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Nivel final (más urgente gana)</th><td><b>{respuesta.triage}</b></td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Especialidad sugerida</th><td>{respuesta.especialidadSugerida}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Banderas de alarma</th><td>{", ".join(respuesta.banderasDeAlarma) or "—"}</td></tr>
    </table>
    """


def test_el_llm_no_puede_reducir_la_urgencia_de_las_reglas(extras):
    # Las reglas dicen I (dolor torácico + disnea); el LLM "sugiere" IV.
    service, _llm = _make_service(triage_sugerido="IV")
    sintomas = "Tengo un dolor fuerte en el pecho y no puedo respirar bien"

    respuesta = asyncio.run(
        service.clasificar_sesion(session_id=None, sintomas=sintomas, paciente=None)
    )
    extras.append(html_extras.html(_tabla_fusion(sintomas, "IV", respuesta)))

    assert respuesta.triage == "I"  # gana la regla, no el LLM
    assert respuesta.requiereAtencionInmediata is True


def test_el_llm_puede_escalar_la_urgencia(extras):
    # Las reglas dicen IV (resfriado leve); el LLM "sugiere" I.
    service, _llm = _make_service(triage_sugerido="I")
    sintomas = "Tengo un poco de tos y congestión, nada grave"

    respuesta = asyncio.run(
        service.clasificar_sesion(session_id=None, sintomas=sintomas, paciente=None)
    )
    extras.append(html_extras.html(_tabla_fusion(sintomas, "I", respuesta)))

    assert respuesta.triage == "I"  # el LLM sí puede escalar


def test_el_llm_recibe_las_banderas_y_el_razonamiento_de_las_reglas():
    service, llm = _make_service()

    asyncio.run(
        service.clasificar_sesion(
            session_id=None,
            sintomas="Tengo un dolor fuerte en el pecho y no puedo respirar bien",
            paciente=None,
        )
    )

    llamada_resumen = next(c for c in llm.calls if c["method"] == "generar_resumen_clinico")
    llamada_triage = next(c for c in llm.calls if c["method"] == "sugerir_triage")

    assert llamada_resumen["banderas_detectadas"], "el resumen debe recibir las banderas detectadas"
    assert llamada_triage["banderas_detectadas"], "la sugerencia de triage debe recibir las banderas"
    assert llamada_triage["razonamiento_reglas"], "debe recibir el razonamiento del motor de reglas"


def test_especialidad_y_banderas_siempre_vienen_de_las_reglas_no_del_llm():
    service, _llm = _make_service(triage_sugerido="I")

    respuesta = asyncio.run(
        service.clasificar_sesion(
            session_id=None,
            sintomas="Tengo un dolor abdominal muy fuerte",
            paciente=None,
        )
    )

    assert respuesta.especialidadSugerida == "Medicina General / Cirugía General"
    assert "Dolor abdominal severo" in respuesta.banderasDeAlarma
