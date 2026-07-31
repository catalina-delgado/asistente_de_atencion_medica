# Casos de prueba compartidos entre los tests automatizados
# (test_triage_rules.py) y el generador del informe QA
# (scripts/generar_informe_qa.py) — una sola fuente de verdad.
#
# Cada caso: (nombre, sintomas_reportados, nivel_triage_esperado)

CASOS_TRIAGE: list[tuple[str, str, str]] = [
    ("Dolor torácico + disnea", "Tengo un dolor fuerte en el pecho y no puedo respirar bien", "I"),
    ("Signos neurológicos (ACV)", "Se le desvía la boca y no puede hablar bien", "I"),
    ("Convulsión", "Tuvo una convulsión hace unos minutos", "I"),
    ("Pérdida de conciencia", "El paciente se desmayó y no reacciona", "I"),
    ("Ideación suicida", "El paciente dice que quiere quitarme la vida", "I"),
    ("Fiebre alta prolongada", "Tengo fiebre de 39 grados desde hace 2 días", "II"),
    ("Dolor abdominal severo", "Tengo un dolor abdominal muy fuerte", "II"),
    ("Vómito persistente", "Vómito persistente, no puede retener líquidos", "II"),
    ("Fiebre moderada", "Tengo fiebre moderada, como 38 grados", "III"),
    ("Tos con flema y fiebre", "Tengo tos con flema y algo de fiebre", "III"),
    ("Síntomas gastrointestinales leves", "Tengo diarrea y náuseas desde ayer", "III"),
    ("Resfriado leve", "Tengo un poco de tos y congestión, nada grave", "IV"),
    ("Dolor leve de garganta", "Me duele un poco la garganta", "IV"),
    ("Sin banderas de alarma (fallback)", "Me siento un poco cansado pero nada más", "III"),
    ("Múltiples banderas de nivel I", "Dolor en el pecho, no puedo respirar, además tengo fiebre alta", "I"),
]
