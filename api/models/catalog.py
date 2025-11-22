from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class CatalogItemType(str, Enum):
    book = "book"
    dvd = "dvd"
    cd = "cd"
    magazine = "magazine"
    other = "other"


class CatalogItemStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"
    damaged = "damaged"
    lost = "lost"


class CatalogItemBase(BaseModel):
    type: CatalogItemType = CatalogItemType.book
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    language: str = "English"
    location: Optional[str] = None
    status: CatalogItemStatus = CatalogItemStatus.available


class CatalogItemCreate(CatalogItemBase):
    pass


class CatalogItemUpdate(BaseModel):
    type: Optional[CatalogItemType] = None
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    location: Optional[str] = None
    status: Optional[CatalogItemStatus] = None


class CatalogItem(CatalogItemBase):
    id: str
    catalog_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
