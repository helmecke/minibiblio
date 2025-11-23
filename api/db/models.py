import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Text, Integer, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class LoanStatus(str, enum.Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"
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


class LoanDB(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    loan_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    catalog_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_items.id"),
        nullable=False,
        index=True,
    )
    patron_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patrons.id"),
        nullable=False,
        index=True,
    )
    checkout_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    return_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus),
        nullable=False,
        default=LoanStatus.active,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    # Relationships
    catalog_item: Mapped["CatalogItemDB"] = relationship()
    patron: Mapped["PatronDB"] = relationship()


class AppSettingDB(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
