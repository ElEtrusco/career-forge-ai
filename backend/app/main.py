from fastapi import FastAPI

from app.api.router import router
from app.core.logger import logger


app = FastAPI(
    title="Career Forge AI",
    version="v1"
)


@app.on_event("startup")
def startup_event():
    logger.info("Career Forge AI API started")


app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Career Forge AI"
    }


