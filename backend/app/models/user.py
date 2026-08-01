from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base
from app.models.mixins import ActiveMixin
from app.models.mixins import TimestampMixin


class User(
    TimestampMixin,
    ActiveMixin,
    Base,
):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_admin: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )



"""from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(150))

    email: Mapped[str] = mapped_column(String(200), unique=True)

    password: Mapped[str] = mapped_column(String(255))"""
