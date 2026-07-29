from fastapi import APIRouter

router = APIRouter(
    prefix="/attention",
    tags=["Medical Attention"]
)

@router.post("")
def create_attention():
    return {
        "message": "Attention endpoint"
    }