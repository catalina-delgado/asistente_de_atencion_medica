import pytest
from pytest_html import extras as html_extras

from app.clinical.triage_rules import classify_by_rules, more_urgent
from tests.casos_triage import CASOS_TRIAGE


def _tabla_clasificacion(sintomas: str, nivel_esperado: str, resultado) -> str:
    banderas = ", ".join(resultado.banderas) if resultado.banderas else "—"
    return f"""
    <table style="font-size:0.85em; border-collapse:collapse;">
      <tr><th style="text-align:left; padding-right:8px;">Síntomas reportados</th><td>{sintomas}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Nivel esperado</th><td>{nivel_esperado}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Nivel obtenido</th><td><b>{resultado.triage}</b></td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Especialidad sugerida</th><td>{resultado.especialidad}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Banderas detectadas</th><td>{banderas}</td></tr>
      <tr><th style="text-align:left; padding-right:8px;">Razonamiento</th><td>{resultado.razonamiento}</td></tr>
    </table>
    """


@pytest.mark.parametrize("nombre,sintomas,nivel_esperado", CASOS_TRIAGE)
def test_classify_by_rules(nombre, sintomas, nivel_esperado, extras):
    resultado = classify_by_rules(sintomas)
    extras.append(html_extras.html(_tabla_clasificacion(sintomas, nivel_esperado, resultado)))

    assert resultado.triage == nivel_esperado, (
        f"{nombre}: se esperaba triage {nivel_esperado}, se obtuvo {resultado.triage} "
        f"(banderas: {resultado.banderas})"
    )


def test_fallback_sin_banderas_cuando_no_hay_match():
    resultado = classify_by_rules("Me siento un poco cansado pero nada más")
    assert resultado.banderas == []
    assert resultado.especialidad == "Medicina General"


def test_normaliza_acentos_y_mayusculas():
    con_acentos = classify_by_rules("TENGO FIEBRE DE 39 GRADOS DESDE HACE 2 DÍAS")
    sin_acentos = classify_by_rules("tengo fiebre de 39 grados desde hace 2 dias")
    assert con_acentos.triage == sin_acentos.triage == "II"


@pytest.mark.parametrize(
    "a,b,esperado",
    [
        ("I", "II", "I"),
        ("II", "I", "I"),
        ("III", "IV", "III"),
        ("IV", "III", "III"),
        ("II", "II", "II"),
        ("I", "IV", "I"),
    ],
)
def test_more_urgent(a, b, esperado):
    assert more_urgent(a, b) == esperado
