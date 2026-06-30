from fastapi import FastAPI

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
    return {"status": "ok"}
