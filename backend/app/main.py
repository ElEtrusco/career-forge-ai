from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.core.logger import logger
from app.database.init_db import create_database

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    logger.info("Iniciando Career Forge AI")

    try:
        create_database()
        logger.info("Base de datos creada correctamente")
    except Exception as e:
        logger.error(f"Error creando BD: {e}")


app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
