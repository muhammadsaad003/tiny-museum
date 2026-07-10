from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class MuseumObject(Base):
    __tablename__ = "museum_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    story: Mapped[str] = mapped_column(Text, nullable=False)
    room: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    material: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    mood: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(40), nullable=False, default="Unspecified")
    acquired_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    significance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
