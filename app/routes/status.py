from fastapi import APIRouter

from app.utils.globals import latest_status

router = APIRouter()


@router.get("/status")
def get_status():
    return latest_status
