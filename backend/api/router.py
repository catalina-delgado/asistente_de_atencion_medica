from fastapi import APIRouter

from app.api.chat import router as chat_router
from app.api.triage import router as triage_router
from app.api.attention import router as attention_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat_router)
api_router.include_router(triage_router)
api_router.include_router(attention_router)