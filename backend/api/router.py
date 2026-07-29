from fastapi import APIRouter

from api.chat import router as chat_router
from api.triage import router as triage_router
from api.attention import router as attention_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat_router)
api_router.include_router(triage_router)
api_router.include_router(attention_router)