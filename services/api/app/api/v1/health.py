from fastapi import APIRouter

router = APIRouter()


@router.get("/readyz")
async def readyz() -> dict:
    return {"status": "ready"}
