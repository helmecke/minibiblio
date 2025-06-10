from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
import json

@dataclass
class Reader:
    """Data model for library readers (Leserverzeichnis)."""
    
    id: Optional[int] = None
    reader_number: Optional[int] = None
    name: str = ""
    address: str = ""
    phone: str = ""
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.name.strip():
            raise ValueError("Reader name is required")
        if not self.address.strip():
            raise ValueError("Reader address is required")
        if not self.phone.strip():
            raise ValueError("Reader phone is required")
    
    @classmethod
    def from_db_row(cls, row) -> 'Reader':
        """Create Reader instance from database row."""
        return cls(
            id=row['id'],
            reader_number=row['reader_number'],
            name=row['name'],
            address=row['address'],
            phone=row['phone'],
            created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
        )
    
    def to_dict(self) -> dict:
        """Convert Reader to dictionary for database operations."""
        return {
            'reader_number': self.reader_number,
            'name': self.name,
            'address': self.address,
            'phone': self.phone
        }

@dataclass
class Book:
    """Data model for library books."""
    
    id: Optional[int] = None
    book_number: str = ""
    title: str = ""
    author: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.book_number.strip():
            raise ValueError("Book number is required")
        if not self.title.strip():
            raise ValueError("Book title is required")
        if self.publication_year is not None and self.publication_year < 0:
            raise ValueError("Publication year must be positive")
    
    @classmethod
    def from_db_row(cls, row) -> 'Book':
        """Create Book instance from database row."""
        return cls(
            id=row['id'],
            book_number=row['book_number'],
            title=row['title'],
            author=row['author'],
            isbn=row['isbn'],
            publication_year=row['publication_year'],
            created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
        )
    
    def to_dict(self) -> dict:
        """Convert Book to dictionary for database operations."""
        return {
            'book_number': self.book_number,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publication_year': self.publication_year
        }

@dataclass
class Loan:
    """Data model for book loans."""
    
    id: Optional[int] = None
    reader_id: int = 0
    book_id: int = 0
    borrow_date: Optional[date] = None
    due_date: Optional[date] = None
    return_date: Optional[date] = None
    status: str = "borrowed"
    created_date: Optional[datetime] = None
    
    # Additional fields for joined queries
    reader_name: Optional[str] = None
    book_title: Optional[str] = None
    book_number: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields and business rules."""
        if self.reader_id <= 0:
            raise ValueError("Valid reader ID is required")
        if self.book_id <= 0:
            raise ValueError("Valid book ID is required")
        if self.status not in ['borrowed', 'returned']:
            raise ValueError("Status must be 'borrowed' or 'returned'")
        if self.return_date and self.borrow_date and self.return_date < self.borrow_date:
            raise ValueError("Return date cannot be before borrow date")
        if self.due_date and self.borrow_date and self.due_date < self.borrow_date:
            raise ValueError("Due date cannot be before borrow date")
    
    @classmethod
    def from_db_row(cls, row) -> 'Loan':
        """Create Loan instance from database row."""
        # Handle joined fields if present (sqlite3.Row objects don't have .get() method)
        reader_name = None
        book_title = None
        book_number = None
        
        try:
            reader_name = row['reader_name']
        except (KeyError, IndexError):
            pass
            
        try:
            book_title = row['book_title']
        except (KeyError, IndexError):
            pass
            
        try:
            book_number = row['book_number']
        except (KeyError, IndexError):
            pass
        
        return cls(
            id=row['id'],
            reader_id=row['reader_id'],
            book_id=row['book_id'],
            borrow_date=date.fromisoformat(row['borrow_date']) if row['borrow_date'] else None,
            due_date=date.fromisoformat(row['due_date']) if row['due_date'] else None,
            return_date=date.fromisoformat(row['return_date']) if row['return_date'] else None,
            status=row['status'],
            created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None,
            reader_name=reader_name,
            book_title=book_title,
            book_number=book_number
        )
    
    def to_dict(self) -> dict:
        """Convert Loan to dictionary for database operations."""
        return {
            'reader_id': self.reader_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status
        }
    
    def is_active(self) -> bool:
        """Check if loan is currently active (borrowed and not returned)."""
        return self.status == 'borrowed' and self.return_date is None
    
    def mark_returned(self, return_date: Optional[date] = None) -> None:
        """Mark loan as returned with optional return date."""
        self.status = 'returned'
        self.return_date = return_date or date.today()

@dataclass
class SearchResult:
    """Data model for search results that can contain mixed entity types."""
    
    result_type: str  # 'reader', 'book', or 'loan'
    reader: Optional[Reader] = None
    book: Optional[Book] = None
    loan: Optional[Loan] = None
    
    def __post_init__(self):
        """Validate that appropriate entity is set for result type."""
        if self.result_type == 'reader' and not self.reader:
            raise ValueError("Reader must be set for reader result type")
        elif self.result_type == 'book' and not self.book:
            raise ValueError("Book must be set for book result type")
        elif self.result_type == 'loan' and not self.loan:
            raise ValueError("Loan must be set for loan result type")

@dataclass
class AuditLog:
    """Data model for audit log entries."""
    
    id: Optional[int] = None
    loan_id: Optional[int] = None
    reader_id: Optional[int] = None
    book_id: Optional[int] = None
    action: str = ""
    description: str = ""
    old_values: Optional[str] = None  # JSON string
    new_values: Optional[str] = None  # JSON string
    user_info: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    # Additional fields for joined queries
    reader_name: Optional[str] = None
    book_title: Optional[str] = None
    book_number: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.action.strip():
            raise ValueError("Action is required")
        if self.action not in ['checkout', 'return', 'extend', 'delete']:
            raise ValueError("Action must be one of: checkout, return, extend, delete")
        if not self.description.strip():
            raise ValueError("Description is required")
    
    @classmethod
    def from_db_row(cls, row) -> 'AuditLog':
        """Create AuditLog instance from database row."""
        # Handle joined fields if present
        reader_name = None
        book_title = None
        book_number = None
        
        try:
            reader_name = row['reader_name']
        except (KeyError, IndexError):
            pass
            
        try:
            book_title = row['book_title']
        except (KeyError, IndexError):
            pass
            
        try:
            book_number = row['book_number']
        except (KeyError, IndexError):
            pass
        
        return cls(
            id=row['id'],
            loan_id=row['loan_id'],
            reader_id=row['reader_id'],
            book_id=row['book_id'],
            action=row['action'],
            description=row['description'],
            old_values=row['old_values'],
            new_values=row['new_values'],
            user_info=row['user_info'],
            timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None,
            reader_name=reader_name,
            book_title=book_title,
            book_number=book_number
        )
    
    def to_dict(self) -> dict:
        """Convert AuditLog to dictionary for database operations."""
        return {
            'loan_id': self.loan_id,
            'reader_id': self.reader_id,
            'book_id': self.book_id,
            'action': self.action,
            'description': self.description,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'user_info': self.user_info
        }
    
    def get_old_values_dict(self) -> dict:
        """Parse old_values JSON string to dictionary."""
        if self.old_values:
            try:
                return json.loads(self.old_values)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_new_values_dict(self) -> dict:
        """Parse new_values JSON string to dictionary."""
        if self.new_values:
            try:
                return json.loads(self.new_values)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_old_values_dict(self, values: dict) -> None:
        """Set old_values from dictionary."""
        self.old_values = json.dumps(values) if values else None
    
    def set_new_values_dict(self, values: dict) -> None:
        """Set new_values from dictionary."""
        self.new_values = json.dumps(values) if values else None