from config.settings import get_settings
from database.session_store import get_session_store
from llm.factory import build_llm_adapter
from repositories.conversacion_repository import ConversacionRepository
from services.atencion_service import AtencionService
from services.chat_service import ChatService
from services.triage_service import TriageService

_llm = build_llm_adapter(get_settings())
_repo = ConversacionRepository(get_session_store())

_chat_service = ChatService(llm=_llm, repo=_repo)
_triage_service = TriageService(llm=_llm, repo=_repo)
_atencion_service = AtencionService(triage_service=_triage_service)


def get_chat_service() -> ChatService:
    return _chat_service


def get_triage_service() -> TriageService:
    return _triage_service


def get_atencion_service() -> AtencionService:
    return _atencion_service