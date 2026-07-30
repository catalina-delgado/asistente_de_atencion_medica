from fastapi import APIRouter, Depends, Request

from deps import get_chat_service
from schemas.chatRequest import ChatRequest
from schemas.chatResponse import ChatResponse
from services.chat_service import ChatService
from utils.security import truncate_for_audit
from utils.logging import audit_event

router = APIRouter()


@router.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, tags=["asistente"])
async def chat(
    payload: ChatRequest,
    request: Request,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    resultado = await service.procesar_mensaje(
        session_id=payload.sessionId, mensaje=payload.mensaje, paciente=payload.paciente
    )
    audit_event(
        "chat_turno",
        request_id=request.state.request_id,
        session_id=resultado.sessionId,
        listo_para_triage=resultado.listoParaTriage,
        mensaje_truncado=truncate_for_audit(payload.mensaje),
    )
    return resultado


