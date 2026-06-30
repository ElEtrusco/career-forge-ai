from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.core.logger import logger
from app.database.init_db import create_database

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Career Forge AI"
)


@app.on_event("startup")
def startup():

    logger.info("Iniciando Career Forge AI")

    create_database()


app.include_router(router)


@app.get("/")
def root():

    return {
        "application": settings.APP_NAME,
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }
