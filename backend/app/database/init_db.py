from app.database.session import Base, engine

# IMPORTAR TODOS LOS MODELOS AQUÍ (IMPORT CRÍTICO)
from app.models.user import User


def create_database():
    Base.metadata.create_all(bind=engine)
