from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PatronLoanItem(BaseModel):
    """A single loan record for patron history."""

    loan_id: str
    catalog_id: str
    title: str
    author: Optional[str] = None
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str


class PatronLoanHistory(BaseModel):
    """Complete loan history for a patron."""

    patron_id: str
    membership_id: str
    patron_name: str
    total_loans: int
    active_loans: int
    loans: list[PatronLoanItem]


class BookLoanRecord(BaseModel):
    """A single loan record for book history."""

    loan_id: str
    patron_id: str
    membership_id: str
    patron_name: str
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str


class BookLoanHistory(BaseModel):
    """Complete loan history for a book."""

    item_id: str
    catalog_id: str
    title: str
    author: Optional[str] = None
    total_loans: int
    loans: list[BookLoanRecord]


class TopBorrowedBook(BaseModel):
    """A book with its loan count for statistics."""

    item_id: str
    catalog_id: str
    title: str
    author: Optional[str] = None
    loan_count: int


class MonthlyLoanCount(BaseModel):
    """Loan count for a specific month."""

    month: int
    count: int


class YearlyStatistics(BaseModel):
    """Annual loan statistics."""

    year: int
    total_loans: int
    unique_books: int
    unique_patrons: int
    top_borrowed_books: list[TopBorrowedBook]
    monthly_breakdown: list[MonthlyLoanCount]
