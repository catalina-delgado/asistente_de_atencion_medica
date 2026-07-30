from fastapi import APIRouter, Depends, Request

from api.deps import get_atencion_service, get_chat_service, get_triage_service
from schemas.attentionRequest import AttentionRequest
from schemas.attentionResponse import AttentionResponse
from schemas.chatRequest import ChatRequest
from schemas.chatResponse import ChatResponse
from schemas.triageRequest import TriageRequest
from schemas.triageResponse import TriageResponse
from services.attention_service import AtencionService
from services.chat_service import ChatService
from services.triage_service import TriageService
from utils.logging import audit_event
from utils.security import mask_sensitive, truncate_for_audit

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


@router.post("/triage", response_model=TriageResponse, tags=["asistente"])
async def triage(
    payload: TriageRequest,
    request: Request,
    service: TriageService = Depends(get_triage_service),
) -> TriageResponse:
    resultado = await service.clasificar_sesion(
        session_id=payload.sessionId, sintomas=payload.sintomas, paciente=payload.paciente
    )
    audit_event(
        "triage_clasificado",
        request_id=request.state.request_id,
        session_id=resultado.sessionId,
        triage=resultado.triage,
        especialidad=resultado.especialidadSugerida,
        requiere_atencion_inmediata=resultado.requiereAtencionInmediata,
    )
    return resultado


@router.post("/atencion", response_model=AttentionResponse, tags=["asistente"])
async def atencion(
    payload: AttentionRequest,
    request: Request,
    service: AtencionService = Depends(get_atencion_service),
) -> AttentionResponse:
    resultado = await service.generar(
        session_id=payload.sessionId, sintomas=payload.sintomas, paciente=payload.paciente
    )
    audit_event(
        "atencion_creada",
        request_id=request.state.request_id,
        session_id=resultado.sessionId,
        atencion_id=resultado.atencionId,
        triage=resultado.triage,
        paciente=mask_sensitive(resultado.paciente.model_dump()),
    )
    return resultado