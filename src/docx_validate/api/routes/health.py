from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "code": 0,
        "message": "ok",
        "data": {"status": "ok"},
    }
