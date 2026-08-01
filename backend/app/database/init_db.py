from app.database.base import Base
from app.database.session import engine

import app.models  # noqa


def create_database():
    print(">>> CREANDO TABLAS EN BD")

    Base.metadata.create_all(bind=engine)

    print(">>> TABLAS CREADAS")