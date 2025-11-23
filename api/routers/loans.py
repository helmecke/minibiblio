from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone
import uuid

from api.models.loan import (
    Loan,
    LoanSimple,
    LoanCheckout,
    LoanExtend,
    LoanReturn,
    LoanStatus,
    PatronSummary,
    CatalogItemSummary,
)
from api.db.database import get_db
from api.db.models import LoanDB, PatronDB, CatalogItemDB
from api.db.models import LoanStatus as DBLoanStatus
from api.db.models import CatalogItemStatus as DBCatalogItemStatus

router = APIRouter(prefix="/loans", tags=["loans"])


def _generate_loan_id() -> str:
    """Generate a unique loan ID."""
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"LN-{short_uuid}"


def _loan_to_response(db_loan: LoanDB) -> Loan:
    """Convert database model to response model with related entities."""
    return Loan(
        id=str(db_loan.id),
        loan_id=db_loan.loan_id,
        catalog_item=CatalogItemSummary(
            id=str(db_loan.catalog_item.id),
            catalog_id=db_loan.catalog_item.catalog_id,
            title=db_loan.catalog_item.title,
            author=db_loan.catalog_item.author,
            type=db_loan.catalog_item.type.value,
        ),
        patron=PatronSummary(
            id=str(db_loan.patron.id),
            membership_id=db_loan.patron.membership_id,
            first_name=db_loan.patron.first_name,
            last_name=db_loan.patron.last_name,
        ),
        checkout_date=db_loan.checkout_date,
        due_date=db_loan.due_date,
        return_date=db_loan.return_date,
        status=db_loan.status,
        notes=db_loan.notes,
        created_at=db_loan.created_at,
        updated_at=db_loan.updated_at,
    )


@router.get("", response_model=List[Loan])
async def list_loans(
    search: Optional[str] = Query(None, description="Search in loan_id, patron name, item title"),
    status: Optional[LoanStatus] = None,
    patron_id: Optional[str] = None,
    catalog_item_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all loans with optional search and filters."""
    query = select(LoanDB).options(
        selectinload(LoanDB.catalog_item),
        selectinload(LoanDB.patron),
    )

    if search:
        search_term = f"%{search}%"
        query = query.join(LoanDB.patron).join(LoanDB.catalog_item).where(
            or_(
                LoanDB.loan_id.ilike(search_term),
                PatronDB.first_name.ilike(search_term),
                PatronDB.last_name.ilike(search_term),
                PatronDB.membership_id.ilike(search_term),
                CatalogItemDB.title.ilike(search_term),
                CatalogItemDB.catalog_id.ilike(search_term),
            )
        )

    if status:
        query = query.where(LoanDB.status == status)
    if patron_id:
        try:
            patron_uuid = uuid.UUID(patron_id)
            query = query.where(LoanDB.patron_id == patron_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid patron ID format")
    if catalog_item_id:
        try:
            item_uuid = uuid.UUID(catalog_item_id)
            query = query.where(LoanDB.catalog_item_id == item_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid catalog item ID format")

    query = query.order_by(LoanDB.checkout_date.desc())
    result = await db.execute(query)
    loans = result.scalars().unique().all()
    return [_loan_to_response(loan) for loan in loans]


@router.get("/count")
async def count_loans(
    status: Optional[LoanStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get loan count, optionally filtered by status."""
    query = select(func.count(LoanDB.id))
    if status:
        query = query.where(LoanDB.status == status)
    result = await db.execute(query)
    return {"count": result.scalar()}


@router.get("/active/count")
async def count_active_loans(db: AsyncSession = Depends(get_db)):
    """Get count of active loans (not returned)."""
    query = select(func.count(LoanDB.id)).where(LoanDB.status == DBLoanStatus.active)
    result = await db.execute(query)
    return {"count": result.scalar()}


@router.get("/overdue")
async def list_overdue_loans(db: AsyncSession = Depends(get_db)):
    """Get all overdue loans."""
    now = datetime.now(timezone.utc)
    query = (
        select(LoanDB)
        .options(
            selectinload(LoanDB.catalog_item),
            selectinload(LoanDB.patron),
        )
        .where(LoanDB.status == DBLoanStatus.active)
        .where(LoanDB.due_date < now)
        .order_by(LoanDB.due_date.asc())
    )
    result = await db.execute(query)
    loans = result.scalars().all()
    return [_loan_to_response(loan) for loan in loans]


@router.get("/{loan_id}", response_model=Loan)
async def get_loan(loan_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single loan by ID."""
    try:
        loan_uuid = uuid.UUID(loan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid loan ID format")

    result = await db.execute(
        select(LoanDB)
        .options(
            selectinload(LoanDB.catalog_item),
            selectinload(LoanDB.patron),
        )
        .where(LoanDB.id == loan_uuid)
    )
    loan = result.scalar_one_or_none()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return _loan_to_response(loan)


@router.post("/checkout", response_model=Loan, status_code=201)
async def checkout_item(checkout_data: LoanCheckout, db: AsyncSession = Depends(get_db)):
    """Check out an item to a patron."""
    # Validate and get catalog item
    try:
        item_uuid = uuid.UUID(checkout_data.catalog_item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid catalog item ID format")

    result = await db.execute(
        select(CatalogItemDB).where(CatalogItemDB.id == item_uuid)
    )
    catalog_item = result.scalar_one_or_none()

    if not catalog_item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    if catalog_item.status != DBCatalogItemStatus.available:
        raise HTTPException(
            status_code=400,
            detail=f"Item is not available for checkout (current status: {catalog_item.status.value})"
        )

    # Validate and get patron
    try:
        patron_uuid = uuid.UUID(checkout_data.patron_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patron ID format")

    result = await db.execute(select(PatronDB).where(PatronDB.id == patron_uuid))
    patron = result.scalar_one_or_none()

    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")

    if patron.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Patron account is not active (current status: {patron.status.value})"
        )

    # Create the loan
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(days=checkout_data.due_days)

    db_loan = LoanDB(
        loan_id=_generate_loan_id(),
        catalog_item_id=item_uuid,
        patron_id=patron_uuid,
        checkout_date=now,
        due_date=due_date,
        status=DBLoanStatus.active,
        notes=checkout_data.notes,
    )
    db.add(db_loan)

    # Update catalog item status to borrowed
    catalog_item.status = DBCatalogItemStatus.borrowed

    await db.flush()
    await db.refresh(db_loan)

    # Load relationships for response
    result = await db.execute(
        select(LoanDB)
        .options(
            selectinload(LoanDB.catalog_item),
            selectinload(LoanDB.patron),
        )
        .where(LoanDB.id == db_loan.id)
    )
    db_loan = result.scalar_one()

    return _loan_to_response(db_loan)


@router.post("/{loan_id}/return", response_model=Loan)
async def return_item(
    loan_id: str,
    return_data: LoanReturn,
    db: AsyncSession = Depends(get_db),
):
    """Return a borrowed item."""
    try:
        loan_uuid = uuid.UUID(loan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid loan ID format")

    result = await db.execute(
        select(LoanDB)
        .options(
            selectinload(LoanDB.catalog_item),
            selectinload(LoanDB.patron),
        )
        .where(LoanDB.id == loan_uuid)
    )
    loan = result.scalar_one_or_none()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.status == DBLoanStatus.returned:
        raise HTTPException(status_code=400, detail="Item has already been returned")

    # Update loan
    loan.return_date = datetime.now(timezone.utc)
    loan.status = DBLoanStatus.returned
    if return_data.notes:
        existing_notes = loan.notes or ""
        loan.notes = f"{existing_notes}\nReturn note: {return_data.notes}".strip()

    # Update catalog item status back to available
    loan.catalog_item.status = DBCatalogItemStatus.available

    await db.flush()
    await db.refresh(loan)

    return _loan_to_response(loan)


@router.post("/{loan_id}/extend", response_model=Loan)
async def extend_loan(
    loan_id: str,
    extend_data: LoanExtend,
    db: AsyncSession = Depends(get_db),
):
    """Extend the due date of an active loan."""
    try:
        loan_uuid = uuid.UUID(loan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid loan ID format")

    result = await db.execute(
        select(LoanDB)
        .options(
            selectinload(LoanDB.catalog_item),
            selectinload(LoanDB.patron),
        )
        .where(LoanDB.id == loan_uuid)
    )
    loan = result.scalar_one_or_none()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.status != DBLoanStatus.active:
        raise HTTPException(
            status_code=400,
            detail=f"Can only extend active loans (current status: {loan.status.value})"
        )

    # Extend due date
    loan.due_date = loan.due_date + timedelta(days=extend_data.additional_days)

    await db.flush()
    await db.refresh(loan)

    return _loan_to_response(loan)
