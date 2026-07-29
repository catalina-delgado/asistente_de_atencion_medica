from fastapi import APIRouter

router = APIRouter(
    prefix="/triage",
    tags=["Triage"]
)

@router.post("")
def triage():
    return {
        "message": "Triage endpoint"
    }