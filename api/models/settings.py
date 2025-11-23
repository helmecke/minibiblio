from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppSetting(BaseModel):
    """A single application setting."""

    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True


class AppSettingUpdate(BaseModel):
    """Update payload for a setting."""

    value: str


class CatalogIdSettings(BaseModel):
    """Catalog ID configuration settings."""

    format: str = "{number}/{year}"
    last_number: int = 0
    last_year: int = 0


class CatalogIdPreview(BaseModel):
    """Preview of next catalog ID."""

    next_id: str
    current_number: int
    current_year: int
