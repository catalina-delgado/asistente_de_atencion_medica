from app.config.settings import get_settings
from app.database.session_store import get_session_store
from app.llm.factory import build_llm_adapter
from app.repositories.conversation_repository import ConversationRepository
from app.services.attention_service import AtencionService
from app.services.chat_service import ChatService
from app.services.triage_service import TriageService

_llm = build_llm_adapter(get_settings())
_repo = ConversationRepository(get_session_store())

_chat_service = ChatService(llm=_llm, repo=_repo)
_triage_service = TriageService(llm=_llm, repo=_repo)
_atencion_service = AtencionService(triage_service=_triage_service)


def get_chat_service() -> ChatService:
    return _chat_service


def get_triage_service() -> TriageService:
    return _triage_service


def get_atencion_service() -> AtencionService:
    return _atencion_service