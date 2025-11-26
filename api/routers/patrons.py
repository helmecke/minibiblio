from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.models.patron import Patron, PatronCreate, PatronUpdate
from api.db.database import get_db
from api.db.models import PatronDB, PatronStatus

router = APIRouter(prefix="/patrons", tags=["patrons"])


def _generate_membership_id() -> str:
    """Generate a unique membership ID."""
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"LIB-{short_uuid}"


def _patron_to_response(db_patron: PatronDB) -> Patron:
    """Convert database model to response model."""
    return Patron(
        id=str(db_patron.id),
        membership_id=db_patron.membership_id,
        first_name=db_patron.first_name,
        last_name=db_patron.last_name,
        email=db_patron.email,
        phone=db_patron.phone,
        address=db_patron.address,
        birthdate=db_patron.birthdate,
        status=db_patron.status,
        created_at=db_patron.created_at,
        updated_at=db_patron.updated_at,
    )


@router.get("", response_model=List[Patron])
async def list_patrons(
    search: Optional[str] = Query(None, description="Search in membership_id, name, email"),
    status: Optional[PatronStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """Get all patrons with optional search and filter."""
    query = select(PatronDB)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                PatronDB.membership_id.ilike(search_term),
                PatronDB.first_name.ilike(search_term),
                PatronDB.last_name.ilike(search_term),
                PatronDB.email.ilike(search_term),
            )
        )

    if status:
        query = query.where(PatronDB.status == status)

    query = query.order_by(PatronDB.created_at.desc())
    result = await db.execute(query)
    patrons = result.scalars().all()
    return [_patron_to_response(p) for p in patrons]


@router.get("/count")
async def count_patrons(
    status: PatronStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get patron count, optionally filtered by status."""
    query = select(func.count(PatronDB.id))
    if status:
        query = query.where(PatronDB.status == status)
    result = await db.execute(query)
    return {"count": result.scalar()}


@router.get("/{patron_id}", response_model=Patron)
async def get_patron(patron_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single patron by ID."""
    try:
        patron_uuid = uuid.UUID(patron_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patron ID format")

    result = await db.execute(select(PatronDB).where(PatronDB.id == patron_uuid))
    patron = result.scalar_one_or_none()

    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")
    return _patron_to_response(patron)


@router.post("", response_model=Patron, status_code=201)
async def create_patron(patron_data: PatronCreate, db: AsyncSession = Depends(get_db)):
    """Create a new patron."""
    db_patron = PatronDB(
        membership_id=_generate_membership_id(),
        first_name=patron_data.first_name,
        last_name=patron_data.last_name,
        email=patron_data.email,
        phone=patron_data.phone,
        status=patron_data.status,
    )
    db.add(db_patron)
    await db.flush()
    await db.refresh(db_patron)
    return _patron_to_response(db_patron)


@router.put("/{patron_id}", response_model=Patron)
async def update_patron(
    patron_id: str,
    patron_data: PatronUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing patron."""
    try:
        patron_uuid = uuid.UUID(patron_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patron ID format")

    result = await db.execute(select(PatronDB).where(PatronDB.id == patron_uuid))
    patron = result.scalar_one_or_none()

    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")

    update_data = patron_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patron, field, value)

    await db.flush()
    await db.refresh(patron)
    return _patron_to_response(patron)


@router.delete("/{patron_id}", status_code=204)
async def delete_patron(patron_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a patron."""
    try:
        patron_uuid = uuid.UUID(patron_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patron ID format")

    result = await db.execute(select(PatronDB).where(PatronDB.id == patron_uuid))
    patron = result.scalar_one_or_none()

    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")

    await db.delete(patron)
