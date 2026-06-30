from app.database.session import Base, engine

# IMPORTANTE: forzar carga de modelos
from app.models.user import User  # noqa


def create_database():
    print(">>> CREANDO TABLAS EN BD")
    Base.metadata.create_all(bind=engine)
    print(">>> TABLAS CREADAS")
