from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.core.logger import logger
from app.database.init_db import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando %s...", settings.APP_NAME)

    try:
        create_database()
        logger.info("Base de datos inicializada correctamente")
    except Exception:
        logger.exception("Error al inicializar la base de datos")
        raise

    yield

    logger.info("Apagando aplicación")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "ok",
    }


"""from fastapi import FastAPI

from app.api.router import router
from app.database.init_db import create_database

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print(">>> STARTUP EJECUTADO")
    try:
        create_database()
        print(">>> BD CREADA OK")
    except Exception as e:
        print(">>> ERROR BD:", e)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok"}"""
