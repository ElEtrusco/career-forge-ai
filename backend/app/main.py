from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI Job Search Assistant"
)


@app.on_event("startup")
def startup():

    logger.info("Career Forge AI iniciado")


@app.get("/")
def root():

    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }
