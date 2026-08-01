from fastapi import APIRouter

from app.api.routes.cv import router as cv_router
from app.api.routes.auth import router as auth_router


router = APIRouter()


router.include_router(cv_router)
router.include_router(auth_router)


@router.get("/ping")
def ping():
    return {
        "message": "pong"
    }