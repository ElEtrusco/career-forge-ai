from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.cv import router as cv_router
from app.api.routes.admin import router as admin_router
from app.api.routes import ai



router = APIRouter()

router.include_router(auth_router)
router.include_router(cv_router)
router.include_router(admin_router)
router.include_router(ai.router)


@router.get("/ping")
def ping():
    return {
        "message": "pong"
    }