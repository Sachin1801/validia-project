from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", summary="Ping")
async def ping():
    """Simple liveness check."""
    return {"ping": "pong"}
