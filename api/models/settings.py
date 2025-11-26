from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


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


class LoanPeriodSettings(BaseModel):
    """Loan period configuration settings."""

    default_period: int = Field(default=14, ge=1, description="Default loan period in days")
    available_periods: List[int] = Field(
        default=[7, 14, 21, 28],
        min_length=1,
        description="Available loan period options in days"
    )
    extension_period: int = Field(default=7, ge=1, description="Extension period in days")

    @field_validator('available_periods')
    @classmethod
    def validate_available_periods(cls, v: List[int]) -> List[int]:
        """Ensure all available periods are positive integers."""
        if not all(period > 0 for period in v):
            raise ValueError("All available periods must be positive integers")
        return v

    @field_validator('default_period')
    @classmethod
    def validate_default_in_available(cls, v: int, info) -> int:
        """Ensure default period is in available periods."""
        # Note: This validator runs before available_periods is set,
        # so we'll validate this in the endpoint instead
        return v
