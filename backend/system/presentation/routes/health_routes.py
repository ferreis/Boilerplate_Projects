from fastapi import APIRouter


router = APIRouter(tags=["Sistema"])


@router.get("/health")
async def get_health_status() -> dict[str, str]:
    return {"status": "ok"}
