"""Motor de reglas de triage basado en combinaciones de palabras clave ("red flags").

Este motor cumple dos roles:
1. Es el clasificador usado por el proveedor LLM "mock" (sin API key configurada),
   de modo que el sistema es evaluable end-to-end sin depender de un servicio externo.
2. Actúa como red de seguridad ("safety net") sobre la clasificación del LLM real:
   si el LLM sugiere un triage menos urgente que el que indican las banderas de
   alarma detectadas por reglas, se usa el más urgente. Nunca se relaja la
   clasificación de un LLM hacia algo menos urgente que lo que dicen las reglas.

Cada regla define grupos de palabras clave: para que la regla dispare, el texto
debe contener al menos una palabra de CADA grupo (AND entre grupos, OR dentro
de un grupo). Esto evita depender de frases exactas y tolera texto natural
como "dolor fuerte en el pecho y dificultad para respirar".
"""

import unicodedata
from dataclasses import dataclass

from models.enums import NivelTriage as TriageLevel

PRIORIDAD_POR_TRIAGE: dict[TriageLevel, str] = {
    "I": "Emergencia inmediata",
    "II": "Urgente",
    "III": "Prioritario",
    "IV": "No urgente",
}

_SEVERITY_RANK: dict[TriageLevel, int] = {"I": 1, "II": 2, "III": 3, "IV": 4}


def more_urgent(a: TriageLevel, b: TriageLevel) -> TriageLevel:
    """Devuelve el nivel más urgente entre dos clasificaciones de triage."""
    return a if _SEVERITY_RANK[a] <= _SEVERITY_RANK[b] else b


def _normalize(text: str) -> str:
    """Minúsculas + sin acentos, para que las reglas no dependan de tildes."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


KeywordGroup = tuple[str, ...]


@dataclass(frozen=True)
class RedFlagRule:
    level: TriageLevel
    label: str
    groups: tuple[KeywordGroup, ...]
    especialidad: str

    def matches(self, normalized_text: str) -> bool:
        return all(any(kw in normalized_text for kw in group) for group in self.groups)


# Reglas ordenadas de más a menos severas.
RED_FLAG_RULES: list[RedFlagRule] = [
    # Triage I – Emergencia inmediata
    RedFlagRule("I", "Dolor torácico con dificultad respiratoria",
                (("dolor", "opresion"), ("pecho", "torax", "toracico"),
                 ("dificultad para respirar", "cuesta respirar", "falta de aire", "ahogo", "no puedo respirar")),
                "Urgencias / Medicina Interna"),
    RedFlagRule("I", "Dificultad respiratoria severa",
                (("no puedo respirar", "me ahogo", "dificultad severa para respirar", "falta de aire severa"),),
                "Urgencias / Neumología"),
    RedFlagRule("I", "Pérdida de conciencia / desmayo",
                (("perdida de conciencia", "se desmayo", "me desmaye", "inconsciente", "no reacciona"),),
                "Urgencias / Medicina Interna"),
    RedFlagRule("I", "Posibles signos de accidente cerebrovascular",
                (("no puede hablar bien", "se le desvia la boca", "paralisis facial",
                  "debilidad subita", "hablar arrastrado", "un lado del cuerpo"),),
                "Urgencias / Neurología"),
    RedFlagRule("I", "Convulsiones",
                (("convulsion", "convulsiones"),),
                "Urgencias / Neurología"),
    RedFlagRule("I", "Sangrado abundante o incontrolable",
                (("sangrado", "hemorragia", "sangra"), ("abundante", "incontrolable", "mucho", "severa", "severo")),
                "Urgencias / Cirugía General"),
    RedFlagRule("I", "Posible reacción alérgica severa (anafilaxia)",
                (("hinchazon", "hinchazo"), ("garganta", "cara", "labios")),
                "Urgencias / Alergología"),
    RedFlagRule("I", "Trauma o accidente grave",
                (("accidente", "trauma", "caida de altura", "herida por arma"), ("grave", "severo", "fuerte")),
                "Urgencias / Cirugía General"),
    RedFlagRule("I", "Ideación o intento suicida",
                (("suicid", "quitarme la vida", "matarme"),),
                "Urgencias / Psiquiatría"),

    # Triage II – Urgente
    RedFlagRule("II", "Fiebre alta o prolongada",
                (("fiebre",), ("39", "40", "hace 2 dias", "hace 3 dias", "varios dias", "persistente")),
                "Medicina General"),
    RedFlagRule("II", "Dolor abdominal severo",
                (("dolor",), ("abdomen", "abdominal", "estomago", "barriga"),
                 ("severo", "fuerte", "intenso", "muy fuerte")),
                "Medicina General / Cirugía General"),
    RedFlagRule("II", "Vómito persistente o signos de deshidratación",
                (("vomito", "deshidratacion"), ("persistente", "constante", "no puede retener liquidos")),
                "Medicina General"),
    RedFlagRule("II", "Dificultad respiratoria moderada",
                (("dificultad", "cuesta", "agita"), ("respirar",)),
                "Medicina General / Neumología"),
    RedFlagRule("II", "Dolor intenso localizado",
                (("dolor",), ("muy fuerte", "intenso", "insoportable")),
                "Medicina General"),

    # Triage III – Prioritario
    RedFlagRule("III", "Fiebre moderada",
                (("fiebre",), ("38", "moderada", "febricula")),
                "Medicina General"),
    RedFlagRule("III", "Tos con flema o congestión con fiebre",
                (("tos", "congestion"), ("flema", "fiebre")),
                "Medicina General"),
    RedFlagRule("III", "Síntomas gastrointestinales leves-moderados",
                (("diarrea", "nauseas", "malestar estomacal"),),
                "Medicina General"),

    # Triage IV – No urgente
    RedFlagRule("IV", "Síntomas leves de resfriado",
                (("tos", "congestion", "gripa", "resfriado", "moco"),),
                "Medicina General"),
    RedFlagRule("IV", "Dolor leve de garganta",
                (("garganta",), ("leve", "molestia", "un poco")),
                "Medicina General"),
]


@dataclass
class RuleClassification:
    triage: TriageLevel
    banderas: list[str]
    especialidad: str
    razonamiento: str


DEFAULT_CLASSIFICATION = RuleClassification(
    triage="III",
    banderas=[],
    especialidad="Medicina General",
    razonamiento=(
        "No se detectaron banderas de alarma claras en el texto proporcionado; "
        "se asigna prioridad intermedia en espera de valoración adicional."
    ),
)


def classify_by_rules(*texts: str) -> RuleClassification:
    """Clasifica el conjunto de texto (síntomas + respuestas de seguimiento)
    según las reglas de banderas de alarma. Devuelve el nivel más urgente
    entre todas las coincidencias encontradas."""
    joined = _normalize(" \n ".join(t for t in texts if t))

    matched = [rule for rule in RED_FLAG_RULES if rule.matches(joined)]
    if not matched:
        return DEFAULT_CLASSIFICATION

    best_level: TriageLevel = min(matched, key=lambda r: _SEVERITY_RANK[r.level]).level
    matches_at_best_level = [r for r in matched if r.level == best_level]

    especialidad = matches_at_best_level[0].especialidad
    banderas = [r.label for r in matches_at_best_level]
    razonamiento = (
        f"Se detectaron {len(banderas)} bandera(s) de alarma de nivel {best_level}: "
        + "; ".join(banderas) + "."
    )
    return RuleClassification(
        triage=best_level, banderas=banderas, especialidad=especialidad, razonamiento=razonamiento
    )