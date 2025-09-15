from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    """Simple finance module ping endpoint."""
    return {"finance": True}


