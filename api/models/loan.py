from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"
    lost = "lost"


class LoanCheckout(BaseModel):
    """Request body for checking out an item."""
    catalog_item_id: str
    patron_id: str
    due_days: int = 14  # Default loan period
    notes: Optional[str] = None


class LoanExtend(BaseModel):
    """Request body for extending a loan."""
    additional_days: int = 7


class LoanReturn(BaseModel):
    """Request body for returning an item."""
    notes: Optional[str] = None


class PatronSummary(BaseModel):
    """Embedded patron info in loan response."""
    id: str
    membership_id: str
    first_name: str
    last_name: str


class CatalogItemSummary(BaseModel):
    """Embedded catalog item info in loan response."""
    id: str
    catalog_id: str
    title: str
    author: Optional[str] = None
    type: str


class Loan(BaseModel):
    """Full loan response with related entities."""
    id: str
    loan_id: str
    catalog_item: CatalogItemSummary
    patron: PatronSummary
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoanSimple(BaseModel):
    """Simple loan response without nested entities."""
    id: str
    loan_id: str
    catalog_item_id: str
    patron_id: str
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
