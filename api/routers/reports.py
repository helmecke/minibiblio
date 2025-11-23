from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from api.models.reports import (
    PatronLoanHistory,
    PatronLoanItem,
    BookLoanHistory,
    BookLoanRecord,
    YearlyStatistics,
    TopBorrowedBook,
    MonthlyLoanCount,
)
from api.db.database import get_db
from api.db.models import LoanDB, PatronDB, CatalogItemDB

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/patron/{patron_id}/loans", response_model=PatronLoanHistory)
async def get_patron_loan_history(patron_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete loan history for a patron."""
    try:
        patron_uuid = uuid.UUID(patron_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patron ID format")

    # Get patron
    patron_result = await db.execute(
        select(PatronDB).where(PatronDB.id == patron_uuid)
    )
    patron = patron_result.scalar_one_or_none()
    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")

    # Get all loans for this patron with catalog item details
    loans_result = await db.execute(
        select(LoanDB)
        .options(selectinload(LoanDB.catalog_item))
        .where(LoanDB.patron_id == patron_uuid)
        .order_by(LoanDB.checkout_date.desc())
    )
    loans = loans_result.scalars().all()

    loan_items = []
    active_count = 0
    for loan in loans:
        if loan.status.value == "active":
            active_count += 1
        loan_items.append(
            PatronLoanItem(
                loan_id=loan.loan_id,
                catalog_id=loan.catalog_item.catalog_id,
                title=loan.catalog_item.title,
                author=loan.catalog_item.author,
                checkout_date=loan.checkout_date,
                due_date=loan.due_date,
                return_date=loan.return_date,
                status=loan.status.value,
            )
        )

    return PatronLoanHistory(
        patron_id=str(patron.id),
        membership_id=patron.membership_id,
        patron_name=f"{patron.first_name} {patron.last_name}",
        total_loans=len(loans),
        active_loans=active_count,
        loans=loan_items,
    )


@router.get("/book/{item_id}/loans", response_model=BookLoanHistory)
async def get_book_loan_history(item_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete loan history for a book."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    # Get catalog item
    item_result = await db.execute(
        select(CatalogItemDB).where(CatalogItemDB.id == item_uuid)
    )
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    # Get all loans for this item with patron details
    loans_result = await db.execute(
        select(LoanDB)
        .options(selectinload(LoanDB.patron))
        .where(LoanDB.catalog_item_id == item_uuid)
        .order_by(LoanDB.checkout_date.desc())
    )
    loans = loans_result.scalars().all()

    loan_records = [
        BookLoanRecord(
            loan_id=loan.loan_id,
            patron_id=str(loan.patron_id),
            membership_id=loan.patron.membership_id,
            patron_name=f"{loan.patron.first_name} {loan.patron.last_name}",
            checkout_date=loan.checkout_date,
            due_date=loan.due_date,
            return_date=loan.return_date,
            status=loan.status.value,
        )
        for loan in loans
    ]

    return BookLoanHistory(
        item_id=str(item.id),
        catalog_id=item.catalog_id,
        title=item.title,
        author=item.author,
        total_loans=len(loans),
        loans=loan_records,
    )


@router.get("/statistics/yearly", response_model=YearlyStatistics)
async def get_yearly_statistics(
    year: int = Query(default=None, description="Year for statistics (default: current year)"),
    db: AsyncSession = Depends(get_db),
):
    """Get annual loan statistics."""
    if year is None:
        year = datetime.now().year

    # Get all loans for the specified year
    loans_result = await db.execute(
        select(LoanDB)
        .options(selectinload(LoanDB.catalog_item))
        .where(extract("year", LoanDB.checkout_date) == year)
    )
    loans = loans_result.scalars().all()

    # Calculate statistics
    total_loans = len(loans)
    unique_books = len(set(loan.catalog_item_id for loan in loans))
    unique_patrons = len(set(loan.patron_id for loan in loans))

    # Count loans per book
    book_counts: dict[uuid.UUID, int] = {}
    book_info: dict[uuid.UUID, CatalogItemDB] = {}
    for loan in loans:
        book_counts[loan.catalog_item_id] = book_counts.get(loan.catalog_item_id, 0) + 1
        book_info[loan.catalog_item_id] = loan.catalog_item

    # Get top 10 borrowed books
    sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_books = [
        TopBorrowedBook(
            item_id=str(item_id),
            catalog_id=book_info[item_id].catalog_id,
            title=book_info[item_id].title,
            author=book_info[item_id].author,
            loan_count=count,
        )
        for item_id, count in sorted_books
    ]

    # Monthly breakdown
    monthly_counts: dict[int, int] = {i: 0 for i in range(1, 13)}
    for loan in loans:
        month = loan.checkout_date.month
        monthly_counts[month] += 1

    monthly_breakdown = [
        MonthlyLoanCount(month=month, count=count)
        for month, count in monthly_counts.items()
    ]

    return YearlyStatistics(
        year=year,
        total_loans=total_loans,
        unique_books=unique_books,
        unique_patrons=unique_patrons,
        top_borrowed_books=top_books,
        monthly_breakdown=monthly_breakdown,
    )


@router.get("/patrons", response_model=list[dict])
async def list_patrons_for_reports(db: AsyncSession = Depends(get_db)):
    """Get list of patrons for report selection dropdown."""
    result = await db.execute(
        select(PatronDB).order_by(PatronDB.last_name, PatronDB.first_name)
    )
    patrons = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "membership_id": p.membership_id,
            "name": f"{p.first_name} {p.last_name}",
        }
        for p in patrons
    ]
