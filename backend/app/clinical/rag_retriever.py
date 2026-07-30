import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_PROTOCOLS_DIR = Path(__file__).parent / "protocols"

# Stopwords en español para que el vectorizador no les dé peso a palabras
# puramente gramaticales (scikit-learn solo trae stopwords en inglés).
_SPANISH_STOPWORDS = [
    "a", "al", "algo", "algun", "alguna", "algunas", "alguno", "algunos", "asi",
    "como", "con", "cual", "cuales", "cuando", "de", "del", "desde", "donde",
    "durante", "e", "el", "ella", "ellas", "ellos", "en", "entre", "era", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "estas", "este", "esto",
    "estos", "ha", "hace", "han", "hay", "la", "las", "le", "les", "lo", "los",
    "mas", "mi", "mis", "mucho", "muy", "no", "nos", "o", "otra", "otras",
    "otro", "otros", "para", "pero", "poco", "por", "porque", "que", "se",
    "sea", "segun", "ser", "si", "sin", "sobre", "son", "su", "sus", "tambien",
    "tiene", "tienen", "todo", "todos", "un", "una", "unas", "uno", "unos", "y",
    "ya", "yo",
]


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def _preprocess(text: str) -> str:
    return _strip_accents(text.lower())


@dataclass(frozen=True)
class ProtocolDoc:
    id: str
    titulo: str
    contenido: str


@dataclass(frozen=True)
class RetrievedProtocol:
    id: str
    titulo: str
    contenido: str
    score: float


def _extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


@lru_cache
def _load_corpus() -> tuple[TfidfVectorizer, "object", tuple[ProtocolDoc, ...]]:
    docs = tuple(
        ProtocolDoc(id=path.stem, titulo=_extract_title(path.read_text(encoding="utf-8"), path.stem),
                     contenido=path.read_text(encoding="utf-8"))
        for path in sorted(_PROTOCOLS_DIR.glob("*.md"))
    )
    vectorizer = TfidfVectorizer(
        preprocessor=_preprocess,
        stop_words=_SPANISH_STOPWORDS,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    doc_matrix = vectorizer.fit_transform([doc.contenido for doc in docs])
    return vectorizer, doc_matrix, docs


def retrieve(query: str, *, top_k: int = 2, min_score: float = 0.05) -> list[RetrievedProtocol]:
    """Devuelve hasta `top_k` protocolos más relevantes para `query`,
    ordenados por similitud de coseno descendente. Filtra resultados con
    score despreciable para no inyectar contexto irrelevante al LLM."""
    vectorizer, doc_matrix, docs = _load_corpus()
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, doc_matrix).ravel()

    results = [
        RetrievedProtocol(id=doc.id, titulo=doc.titulo, contenido=doc.contenido, score=float(score))
        for doc, score in zip(docs, scores)
        if score >= min_score
    ]
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def render_context(protocols: list[RetrievedProtocol]) -> str:
    """Renderiza los protocolos recuperados como bloque de texto para
    incluir en el prompt del LLM (o en el resumen del proveedor mock)."""
    if not protocols:
        return ""
    partes = [f"[{p.titulo} | relevancia={p.score:.2f}]\n{p.contenido}" for p in protocols]
    return "\n\n---\n\n".join(partes)