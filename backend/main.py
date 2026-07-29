from fastapi import FastAPI

from api.router import api_router

app = FastAPI(
    title="Medical Triage Chatbot",
    version="1.0.0",
    description="API para chatbot de triage médico."
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "medical-triage-chatbot"
    }