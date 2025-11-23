from pydantic import BaseModel
from enum import Enum
from typing import Optional


class DuplicateHandling(str, Enum):
    skip = "skip"
    update = "update"
    create = "create"


class ValidationStatus(str, Enum):
    valid = "valid"
    warning = "warning"
    error = "error"


class CSVPreviewRow(BaseModel):
    """A single row from the CSV with validation status."""

    row_number: int
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    catalog_id: Optional[str] = None
    isbn: Optional[str] = None
    status: ValidationStatus = ValidationStatus.valid
    errors: list[str] = []
    warnings: list[str] = []


class CSVPreviewResponse(BaseModel):
    """Response for CSV preview endpoint."""

    total_rows: int
    valid_rows: int
    warning_rows: int
    error_rows: int
    columns_detected: list[str]
    has_author_column: bool
    has_publisher_column: bool
    rows: list[CSVPreviewRow]


class ImportOptions(BaseModel):
    """Options for the import operation."""

    duplicate_handling: DuplicateHandling = DuplicateHandling.skip
    default_language: str = "German"


class ImportError(BaseModel):
    """Details about an import error."""

    row_number: int
    catalog_id: Optional[str] = None
    title: Optional[str] = None
    error: str


class ImportResult(BaseModel):
    """Result of an import operation."""

    success_count: int
    skipped_count: int
    updated_count: int
    error_count: int
    errors: list[ImportError]
