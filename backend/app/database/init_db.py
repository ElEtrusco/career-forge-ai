from app.database.session import Base, engine

# IMPORTANTE: asegurar que modelos se registran
from app.models.user import User  # noqa


def create_database():
    Base.metadata.create_all(bind=engine)
