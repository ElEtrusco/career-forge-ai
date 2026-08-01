from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class TimestampMixin:
    """
    Añade fechas automáticas.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ActiveMixin:
    """
    Añade estado activo/inactivo.
    """

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )