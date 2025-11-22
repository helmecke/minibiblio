import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Text, Integer, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from api.db.database import Base


class PatronStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class CatalogItemType(str, enum.Enum):
    book = "book"
    dvd = "dvd"
    cd = "cd"
    magazine = "magazine"
    other = "other"


class CatalogItemStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"
    damaged = "damaged"
    lost = "lost"


class PatronDB(Base):
    __tablename__ = "patrons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    membership_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[PatronStatus] = mapped_column(
        Enum(PatronStatus),
        nullable=False,
        default=PatronStatus.active,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CatalogItemDB(Base):
    __tablename__ = "catalog_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    catalog_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    type: Mapped[CatalogItemType] = mapped_column(
        Enum(CatalogItemType),
        nullable=False,
        default=CatalogItemType.book,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="English")
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[CatalogItemStatus] = mapped_column(
        Enum(CatalogItemStatus),
        nullable=False,
        default=CatalogItemStatus.available,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
