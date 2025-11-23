import csv
import io
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.import_models import (
    CSVPreviewRow,
    CSVPreviewResponse,
    ImportOptions,
    ImportResult,
    ImportError,
    ValidationStatus,
    DuplicateHandling,
)
from api.db.database import get_db
from api.db.models import CatalogItemDB
from api.db.models import CatalogItemType as DBCatalogItemType
from api.db.models import CatalogItemStatus as DBCatalogItemStatus

router = APIRouter(prefix="/import", tags=["import"])

# Expected column names (case-insensitive matching)
TITLE_COLUMNS = ["titel", "title"]
AUTHOR_COLUMNS = ["autor", "author"]
PUBLISHER_COLUMNS = ["verlag", "publisher"]
GENRE_COLUMNS = ["genres", "genre"]
CATALOG_ID_COLUMNS = ["inventarnr.", "inventarnr", "catalog_id", "inventory_number"]
ISBN_COLUMNS = ["isbn"]


def _find_column(headers: list[str], possible_names: list[str]) -> str | None:
    """Find a column by checking multiple possible names (case-insensitive)."""
    headers_lower = [h.lower().strip() for h in headers]
    for name in possible_names:
        if name.lower() in headers_lower:
            idx = headers_lower.index(name.lower())
            return headers[idx]
    return None


def _get_value(row: dict, headers: list[str], possible_names: list[str]) -> str | None:
    """Get a value from a row by checking multiple possible column names."""
    col = _find_column(headers, possible_names)
    if col and col in row:
        value = row[col].strip() if row[col] else None
        return value if value else None
    return None


def _validate_row(
    row_number: int,
    title: str | None,
    catalog_id: str | None,
    isbn: str | None,
) -> tuple[ValidationStatus, list[str], list[str]]:
    """Validate a single row and return status, errors, and warnings."""
    errors = []
    warnings = []

    # Required fields
    if not title:
        errors.append("Title is required")
    if not catalog_id:
        errors.append("Inventory number (InventarNr.) is required")

    # ISBN validation
    if isbn and isbn.lower() not in ["keine", ""]:
        # Basic ISBN validation - should be 10 or 13 digits (ignoring hyphens)
        isbn_digits = "".join(c for c in isbn if c.isdigit())
        if len(isbn_digits) not in [0, 10, 13]:
            warnings.append(f"ISBN '{isbn}' may be invalid (expected 10 or 13 digits)")

    if errors:
        return ValidationStatus.error, errors, warnings
    elif warnings:
        return ValidationStatus.warning, errors, warnings
    return ValidationStatus.valid, errors, warnings


def _parse_csv_rows(
    content: str,
) -> tuple[list[CSVPreviewRow], list[str], bool, bool]:
    """Parse CSV content and return preview rows with metadata."""
    rows = []
    headers = []
    has_author = False
    has_publisher = False

    # Try to detect delimiter
    try:
        # Use csv.Sniffer to detect dialect
        dialect = csv.Sniffer().sniff(content[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel  # Default to comma-separated

    reader = csv.DictReader(io.StringIO(content), dialect=dialect)
    headers = reader.fieldnames or []

    # Check which columns are present
    has_author = _find_column(headers, AUTHOR_COLUMNS) is not None
    has_publisher = _find_column(headers, PUBLISHER_COLUMNS) is not None

    row_number = 0
    for row in reader:
        row_number += 1

        # Skip empty rows
        if all(not v or not v.strip() for v in row.values()):
            continue

        title = _get_value(row, headers, TITLE_COLUMNS)
        author = _get_value(row, headers, AUTHOR_COLUMNS)
        publisher = _get_value(row, headers, PUBLISHER_COLUMNS)
        genre = _get_value(row, headers, GENRE_COLUMNS)
        catalog_id = _get_value(row, headers, CATALOG_ID_COLUMNS)
        isbn = _get_value(row, headers, ISBN_COLUMNS)

        status, errors, warnings = _validate_row(row_number, title, catalog_id, isbn)

        rows.append(
            CSVPreviewRow(
                row_number=row_number,
                title=title,
                author=author,
                publisher=publisher,
                genre=genre,
                catalog_id=catalog_id,
                isbn=isbn if isbn and isbn.lower() != "keine" else None,
                status=status,
                errors=errors,
                warnings=warnings,
            )
        )

    return rows, headers, has_author, has_publisher


@router.post("/catalog/preview", response_model=CSVPreviewResponse)
async def preview_csv(file: UploadFile = File(...)):
    """Preview a CSV file before importing to catalog."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        # Read file content with proper encoding
        content_bytes = await file.read()
        # Try UTF-8 with BOM first, then fallback to latin-1
        try:
            content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1")

        rows, headers, has_author, has_publisher = _parse_csv_rows(content)

        valid_count = sum(1 for r in rows if r.status == ValidationStatus.valid)
        warning_count = sum(1 for r in rows if r.status == ValidationStatus.warning)
        error_count = sum(1 for r in rows if r.status == ValidationStatus.error)

        return CSVPreviewResponse(
            total_rows=len(rows),
            valid_rows=valid_count,
            warning_rows=warning_count,
            error_rows=error_count,
            columns_detected=headers,
            has_author_column=has_author,
            has_publisher_column=has_publisher,
            rows=rows,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")


@router.post("/catalog", response_model=ImportResult)
async def import_catalog(
    file: UploadFile = File(...),
    duplicate_handling: DuplicateHandling = DuplicateHandling.skip,
    default_language: str = "German",
    db: AsyncSession = Depends(get_db),
):
    """Import catalog items from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        # Read and parse file
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1")

        rows, headers, has_author, has_publisher = _parse_csv_rows(content)

        success_count = 0
        skipped_count = 0
        updated_count = 0
        error_count = 0
        errors: list[ImportError] = []

        for row in rows:
            # Skip rows with errors
            if row.status == ValidationStatus.error:
                error_count += 1
                errors.append(
                    ImportError(
                        row_number=row.row_number,
                        catalog_id=row.catalog_id,
                        title=row.title,
                        error="; ".join(row.errors),
                    )
                )
                continue

            try:
                # Check for existing item by catalog_id
                existing = await db.execute(
                    select(CatalogItemDB).where(
                        CatalogItemDB.catalog_id == row.catalog_id
                    )
                )
                existing_item = existing.scalar_one_or_none()

                if existing_item:
                    if duplicate_handling == DuplicateHandling.skip:
                        skipped_count += 1
                        continue
                    elif duplicate_handling == DuplicateHandling.update:
                        # Update existing item
                        existing_item.title = row.title or existing_item.title
                        existing_item.author = row.author or existing_item.author
                        existing_item.publisher = (
                            row.publisher or existing_item.publisher
                        )
                        existing_item.genre = row.genre or existing_item.genre
                        existing_item.isbn = row.isbn or existing_item.isbn
                        updated_count += 1
                        continue
                    # DuplicateHandling.create falls through to create new item

                # Create new item
                db_item = CatalogItemDB(
                    catalog_id=row.catalog_id,
                    type=DBCatalogItemType.book,
                    title=row.title,
                    author=row.author,
                    publisher=row.publisher,
                    genre=row.genre,
                    isbn=row.isbn,
                    language=default_language,
                    status=DBCatalogItemStatus.available,
                )
                db.add(db_item)
                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(
                    ImportError(
                        row_number=row.row_number,
                        catalog_id=row.catalog_id,
                        title=row.title,
                        error=str(e),
                    )
                )

        # Commit all changes
        await db.commit()

        return ImportResult(
            success_count=success_count,
            skipped_count=skipped_count,
            updated_count=updated_count,
            error_count=error_count,
            errors=errors,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
