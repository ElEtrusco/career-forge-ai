from fastapi import APIRouter

from app.api.routes.cv import router as cv_router

router = APIRouter()

router.include_router(cv_router)


@router.get("/ping")
def ping():
    return {"message": "pong"}
