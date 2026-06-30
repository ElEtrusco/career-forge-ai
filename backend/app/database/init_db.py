from app.database.session import Base, engine

# Importar modelos
from app.models.user import User


def create_database():
    Base.metadata.create_all(bind=engine)
