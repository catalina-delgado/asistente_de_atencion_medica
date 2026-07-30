from config.settings import get_settings
from database.session_store import get_session_store
from llm.factory import build_llm_adapter
from repositories.conversation_repository import ConversacionRepository
from services.chat_service import ChatService

_llm = build_llm_adapter(get_settings())
_repo = ConversacionRepository(get_session_store())

_chat_service = ChatService(llm=_llm, repo=_repo)


def get_chat_service() -> ChatService:
    return _chat_service

