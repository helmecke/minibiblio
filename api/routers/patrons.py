from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from api.models.patron import Patron, PatronCreate, PatronUpdate, PatronStatus

router = APIRouter(prefix="/patrons", tags=["patrons"])

# Mock data store
_patrons: dict[str, Patron] = {}


def _init_mock_data():
    """Initialize with sample patron data."""
    if _patrons:
        return

    sample_patrons = [
        {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@email.com",
            "phone": "+1 555-0101",
            "status": PatronStatus.active,
            "borrowing_limit": 5,
            "current_borrowed_count": 2,
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@email.com",
            "phone": "+1 555-0102",
            "status": PatronStatus.active,
            "borrowing_limit": 5,
            "current_borrowed_count": 0,
        },
        {
            "first_name": "Carol",
            "last_name": "Williams",
            "email": "carol.w@email.com",
            "phone": "+1 555-0103",
            "status": PatronStatus.suspended,
            "borrowing_limit": 5,
            "current_borrowed_count": 3,
            "notes": "Overdue books - contacted on 2024-01-15",
        },
        {
            "first_name": "David",
            "last_name": "Brown",
            "email": "david.brown@email.com",
            "status": PatronStatus.inactive,
            "borrowing_limit": 3,
            "current_borrowed_count": 0,
        },
        {
            "first_name": "Emma",
            "last_name": "Davis",
            "email": "emma.davis@email.com",
            "phone": "+1 555-0105",
            "status": PatronStatus.active,
            "borrowing_limit": 10,
            "current_borrowed_count": 5,
            "notes": "Premium member",
        },
    ]

    for i, data in enumerate(sample_patrons):
        patron_id = str(uuid.uuid4())
        now = datetime.now()
        _patrons[patron_id] = Patron(
            id=patron_id,
            membership_id=f"LIB-{1000 + i}",
            created_at=now,
            updated_at=now,
            **data,
        )


# Initialize mock data on module load
_init_mock_data()


@router.get("", response_model=List[Patron])
async def list_patrons():
    """Get all patrons."""
    return list(_patrons.values())


@router.get("/{patron_id}", response_model=Patron)
async def get_patron(patron_id: str):
    """Get a single patron by ID."""
    if patron_id not in _patrons:
        raise HTTPException(status_code=404, detail="Patron not found")
    return _patrons[patron_id]


@router.post("", response_model=Patron, status_code=201)
async def create_patron(patron_data: PatronCreate):
    """Create a new patron."""
    patron_id = str(uuid.uuid4())
    now = datetime.now()

    # Generate membership ID
    max_num = 1000
    for p in _patrons.values():
        num = int(p.membership_id.split("-")[1])
        if num >= max_num:
            max_num = num + 1
    membership_id = f"LIB-{max_num}"

    patron = Patron(
        id=patron_id,
        membership_id=membership_id,
        current_borrowed_count=0,
        created_at=now,
        updated_at=now,
        **patron_data.model_dump(),
    )
    _patrons[patron_id] = patron
    return patron


@router.put("/{patron_id}", response_model=Patron)
async def update_patron(patron_id: str, patron_data: PatronUpdate):
    """Update an existing patron."""
    if patron_id not in _patrons:
        raise HTTPException(status_code=404, detail="Patron not found")

    existing = _patrons[patron_id]
    update_data = patron_data.model_dump(exclude_unset=True)

    updated = existing.model_copy(
        update={**update_data, "updated_at": datetime.now()}
    )
    _patrons[patron_id] = updated
    return updated


@router.delete("/{patron_id}", status_code=204)
async def delete_patron(patron_id: str):
    """Delete a patron."""
    if patron_id not in _patrons:
        raise HTTPException(status_code=404, detail="Patron not found")
    del _patrons[patron_id]
