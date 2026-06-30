from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(150))

    email: Mapped[str] = mapped_column(String(200), unique=True)

    password: Mapped[str] = mapped_column(String(255))
