from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.models.catalog import CatalogItem, CatalogItemCreate, CatalogItemUpdate, CatalogItemType, CatalogItemStatus
from api.db.database import get_db
from api.db.models import CatalogItemDB
from api.db.models import CatalogItemType as DBCatalogItemType
from api.db.models import CatalogItemStatus as DBCatalogItemStatus

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _generate_catalog_id() -> str:
    """Generate a unique catalog ID."""
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"CAT-{short_uuid}"


def _item_to_response(db_item: CatalogItemDB) -> CatalogItem:
    """Convert database model to response model."""
    return CatalogItem(
        id=str(db_item.id),
        catalog_id=db_item.catalog_id,
        type=db_item.type,
        title=db_item.title,
        author=db_item.author,
        isbn=db_item.isbn,
        publisher=db_item.publisher,
        year=db_item.year,
        description=db_item.description,
        genre=db_item.genre,
        language=db_item.language,
        location=db_item.location,
        status=db_item.status,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
    )


@router.get("", response_model=List[CatalogItem])
async def list_catalog_items(
    type: Optional[CatalogItemType] = None,
    status: Optional[CatalogItemStatus] = None,
    search: Optional[str] = Query(None, description="Search in title, author, ISBN"),
    db: AsyncSession = Depends(get_db),
):
    """Get all catalog items with optional filters."""
    query = select(CatalogItemDB)

    if type:
        query = query.where(CatalogItemDB.type == type)
    if status:
        query = query.where(CatalogItemDB.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                CatalogItemDB.title.ilike(search_term),
                CatalogItemDB.author.ilike(search_term),
                CatalogItemDB.isbn.ilike(search_term),
            )
        )

    query = query.order_by(CatalogItemDB.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()
    return [_item_to_response(item) for item in items]


@router.get("/count")
async def count_catalog_items(
    type: Optional[CatalogItemType] = None,
    status: Optional[CatalogItemStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get catalog item count, optionally filtered by type or status."""
    query = select(func.count(CatalogItemDB.id))
    if type:
        query = query.where(CatalogItemDB.type == type)
    if status:
        query = query.where(CatalogItemDB.status == status)
    result = await db.execute(query)
    return {"count": result.scalar()}


@router.get("/{item_id}", response_model=CatalogItem)
async def get_catalog_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single catalog item by ID."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = await db.execute(select(CatalogItemDB).where(CatalogItemDB.id == item_uuid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Catalog item not found")
    return _item_to_response(item)


@router.post("", response_model=CatalogItem, status_code=201)
async def create_catalog_item(item_data: CatalogItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new catalog item."""
    db_item = CatalogItemDB(
        catalog_id=_generate_catalog_id(),
        type=item_data.type,
        title=item_data.title,
        author=item_data.author,
        isbn=item_data.isbn,
        publisher=item_data.publisher,
        year=item_data.year,
        description=item_data.description,
        genre=item_data.genre,
        language=item_data.language,
        location=item_data.location,
        status=item_data.status,
    )
    db.add(db_item)
    await db.flush()
    await db.refresh(db_item)
    return _item_to_response(db_item)


@router.put("/{item_id}", response_model=CatalogItem)
async def update_catalog_item(
    item_id: str,
    item_data: CatalogItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing catalog item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = await db.execute(select(CatalogItemDB).where(CatalogItemDB.id == item_uuid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return _item_to_response(item)


@router.delete("/{item_id}", status_code=204)
async def delete_catalog_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a catalog item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = await db.execute(select(CatalogItemDB).where(CatalogItemDB.id == item_uuid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    await db.delete(item)
