from typing import List, Optional
from datetime import date, datetime

from database.db_manager import DatabaseManager
from database.models import Loan, Reader, Book

class LoanService:
    """Service class for managing book loans with lending business logic."""
    
    def __init__(self, db_manager: DatabaseManager, audit_service=None):
        """
        Initialize loan service.
        
        Args:
            db_manager: Database manager instance
            audit_service: Audit service instance (optional, for logging)
        """
        self.db = db_manager
        self.audit_service = audit_service
    
    def check_out_book(self, reader_id: int, book_id: int, borrow_date: date = None, loan_duration_days: int = 14) -> Loan:
        """
        Check out a book to a reader.
        
        Args:
            reader_id: Reader's database ID
            book_id: Book's database ID
            borrow_date: Date of borrowing (defaults to today)
            loan_duration_days: Number of days for the loan duration (defaults to 14)
            
        Returns:
            Created Loan object
            
        Raises:
            ValueError: If validation fails or business rules are violated
            RuntimeError: If database operation fails
        """
        # Use today's date if not provided
        if borrow_date is None:
            borrow_date = date.today()
        
        # Calculate due date
        from datetime import timedelta
        due_date = borrow_date + timedelta(days=loan_duration_days)
        
        # Validate reader exists
        reader_check = self.db.execute_query(
            "SELECT id FROM readers WHERE id = ?",
            (reader_id,)
        )
        if not reader_check:
            raise ValueError(f"Reader with ID {reader_id} does not exist")
        
        # Validate book exists
        book_check = self.db.execute_query(
            "SELECT id FROM books WHERE id = ?",
            (book_id,)
        )
        if not book_check:
            raise ValueError(f"Book with ID {book_id} does not exist")
        
        # Check if book is already borrowed
        active_loan_check = self.db.execute_query(
            "SELECT id FROM loans WHERE book_id = ? AND status = 'borrowed'",
            (book_id,)
        )
        if active_loan_check:
            raise ValueError("Book is already borrowed and not available")
        
        # Create loan object for validation
        loan = Loan(
            reader_id=reader_id,
            book_id=book_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status="borrowed"
        )
        
        # Insert into database
        loan_id = self.db.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (loan.reader_id, loan.book_id, loan.borrow_date.isoformat(), loan.due_date.isoformat(), loan.status)
        )
        
        # Return created loan with ID
        loan.id = loan_id
        loan.created_date = datetime.now()
        
        # Get reader and book names for audit logging
        if self.audit_service:
            try:
                # Get reader and book info for the audit log
                reader_info = self.db.execute_query(
                    "SELECT name FROM readers WHERE id = ?", (reader_id,)
                )
                book_info = self.db.execute_query(
                    "SELECT title, book_number FROM books WHERE id = ?", (book_id,)
                )
                
                if reader_info and book_info:
                    loan.reader_name = reader_info[0]['name']
                    loan.book_title = book_info[0]['title'] 
                    loan.book_number = book_info[0]['book_number']
                
                # Log the checkout activity
                self.audit_service.log_checkout(loan)
            except Exception:
                # Don't fail the checkout if audit logging fails
                pass
        
        return loan
    
    def return_book(self, loan_id: int, return_date: date = None) -> Loan:
        """
        Process book return.
        
        Args:
            loan_id: Loan's database ID
            return_date: Date of return (defaults to today)
            
        Returns:
            Updated Loan object
            
        Raises:
            ValueError: If loan not found or already returned
            RuntimeError: If database operation fails
        """
        # Use today's date if not provided
        if return_date is None:
            return_date = date.today()
        
        # Get existing loan
        loan_rows = self.db.execute_query(
            "SELECT * FROM loans WHERE id = ?",
            (loan_id,)
        )
        
        if not loan_rows:
            raise ValueError(f"Loan with ID {loan_id} does not exist")
        
        loan = Loan.from_db_row(loan_rows[0])
        
        # Check if already returned
        if loan.status == "returned":
            raise ValueError("Book has already been returned")
        
        # Validate return date
        if return_date < loan.borrow_date:
            raise ValueError("Return date cannot be before borrow date")
        
        # Update loan
        affected_rows = self.db.execute_command(
            "UPDATE loans SET return_date = ?, status = 'returned' WHERE id = ?",
            (return_date.isoformat(), loan_id)
        )
        
        if affected_rows == 0:
            raise RuntimeError("Failed to update loan")
        
        # Store old loan state for audit
        old_loan = Loan.from_db_row(loan_rows[0])
        
        # Update loan object
        loan.return_date = return_date
        loan.status = "returned"
        
        # Log the return activity
        if self.audit_service:
            try:
                # Get updated loan with reader and book info
                updated_loan = self.get_loan_by_id(loan_id)
                if updated_loan:
                    self.audit_service.log_return(updated_loan, old_loan)
            except Exception:
                # Don't fail the return if audit logging fails
                pass
        
        return loan
    
    def return_book_by_book_id(self, book_id: int, return_date: date = None) -> Loan:
        """
        Process book return by book ID (finds active loan automatically).
        
        Args:
            book_id: Book's database ID
            return_date: Date of return (defaults to today)
            
        Returns:
            Updated Loan object
            
        Raises:
            ValueError: If no active loan found for book
            RuntimeError: If database operation fails
        """
        # Find active loan for this book
        loan_rows = self.db.execute_query(
            "SELECT * FROM loans WHERE book_id = ? AND status = 'borrowed'",
            (book_id,)
        )
        
        if not loan_rows:
            raise ValueError(f"No active loan found for book ID {book_id}")
        
        loan = Loan.from_db_row(loan_rows[0])
        return self.return_book(loan.id, return_date)
    
    def get_loan_by_id(self, loan_id: int) -> Optional[Loan]:
        """
        Get loan by ID with reader and book information.
        
        Args:
            loan_id: Loan's database ID
            
        Returns:
            Loan object with reader and book info if found, None otherwise
        """
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.id = ?
        """, (loan_id,))
        
        return Loan.from_db_row(rows[0]) if rows else None
    
    def get_active_loans(self) -> List[Loan]:
        """
        Get all active loans with reader and book information.
        
        Returns:
            List of active Loan objects
        """
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.status = 'borrowed'
            ORDER BY l.borrow_date DESC
        """)
        
        return [Loan.from_db_row(row) for row in rows]
    
    def get_loans_by_reader(self, reader_id: int) -> List[Loan]:
        """
        Get all loans for a specific reader.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            List of Loan objects for the reader
        """
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.reader_id = ?
            ORDER BY l.borrow_date DESC
        """, (reader_id,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def get_loans_by_book(self, book_id: int) -> List[Loan]:
        """
        Get all loans for a specific book.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            List of Loan objects for the book
        """
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.book_id = ?
            ORDER BY l.borrow_date DESC, l.id DESC
        """, (book_id,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def get_active_loans_by_reader(self, reader_id: int) -> List[Loan]:
        """
        Get active loans for a specific reader.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            List of active Loan objects for the reader
        """
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.reader_id = ? AND l.status = 'borrowed'
            ORDER BY l.borrow_date DESC
        """, (reader_id,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Get loans that are overdue (due date has passed).
        
        Returns:
            List of overdue Loan objects
        """
        today = date.today()
        
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE l.status = 'borrowed' AND l.due_date < ?
            ORDER BY l.due_date ASC
        """, (today.isoformat(),))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def get_loan_history(self, limit: int = None) -> List[Loan]:
        """
        Get loan history (all loans) with reader and book information.
        
        Args:
            limit: Maximum number of loans to return (optional)
            
        Returns:
            List of Loan objects ordered by borrow date (newest first)
        """
        query = """
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            ORDER BY l.borrow_date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = self.db.execute_query(query)
        return [Loan.from_db_row(row) for row in rows]
    
    def search_loans_by_reader_name(self, reader_name: str) -> List[Loan]:
        """
        Search loans by reader name.
        
        Args:
            reader_name: Reader name to search for
            
        Returns:
            List of matching Loan objects
        """
        if not reader_name.strip():
            return []
        
        search_term = f"%{reader_name.strip()}%"
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE r.name LIKE ?
            ORDER BY l.borrow_date DESC
        """, (search_term,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def search_loans_by_book_title(self, book_title: str) -> List[Loan]:
        """
        Search loans by book title.
        
        Args:
            book_title: Book title to search for
            
        Returns:
            List of matching Loan objects
        """
        if not book_title.strip():
            return []
        
        search_term = f"%{book_title.strip()}%"
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE b.title LIKE ?
            ORDER BY l.borrow_date DESC
        """, (search_term,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def search_loans_by_book_number(self, book_number: str) -> List[Loan]:
        """
        Search loans by book number.
        
        Args:
            book_number: Book number to search for
            
        Returns:
            List of matching Loan objects
        """
        if not book_number.strip():
            return []
        
        search_term = f"%{book_number.strip()}%"
        rows = self.db.execute_query("""
            SELECT l.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            JOIN books b ON l.book_id = b.id
            WHERE b.book_number LIKE ?
            ORDER BY l.borrow_date DESC
        """, (search_term,))
        
        return [Loan.from_db_row(row) for row in rows]
    
    def extend_loan(self, loan_id: int, extension_days: int = 14) -> Loan:
        """
        Extend a loan by extending the due date.
        
        Args:
            loan_id: Loan's database ID
            extension_days: Number of days to extend (defaults to 14)
            
        Returns:
            Updated Loan object
            
        Raises:
            ValueError: If loan not found or already returned
            RuntimeError: If database operation fails
        """
        # Get existing loan
        loan_rows = self.db.execute_query(
            "SELECT * FROM loans WHERE id = ?",
            (loan_id,)
        )
        
        if not loan_rows:
            raise ValueError(f"Loan with ID {loan_id} does not exist")
        
        loan = Loan.from_db_row(loan_rows[0])
        
        # Check if already returned
        if loan.status == "returned":
            raise ValueError("Cannot extend a returned loan")
        
        # Store old due date for audit
        old_due_date = loan.due_date
        
        # Calculate new due date
        from datetime import timedelta
        new_due_date = loan.due_date + timedelta(days=extension_days)
        
        # Update loan in database
        affected_rows = self.db.execute_command(
            "UPDATE loans SET due_date = ? WHERE id = ?",
            (new_due_date.isoformat(), loan_id)
        )
        
        if affected_rows == 0:
            raise RuntimeError("Failed to extend loan")
        
        # Update loan object
        loan.due_date = new_due_date
        
        # Log the extension activity
        if self.audit_service:
            try:
                # Get updated loan with reader and book info
                updated_loan = self.get_loan_by_id(loan_id)
                if updated_loan:
                    self.audit_service.log_extension(updated_loan, old_due_date, extension_days)
            except Exception:
                # Don't fail the extension if audit logging fails
                pass
        
        return loan
    
    def get_loan_statistics(self) -> dict:
        """
        Get loan statistics for the library.
        
        Returns:
            Dictionary with loan statistics
        """
        # Total loans
        total_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans"
        )[0]['count']
        
        # Active loans
        active_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE status = 'borrowed'"
        )[0]['count']
        
        # Returned loans
        returned_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE status = 'returned'"
        )[0]['count']
        
        # Overdue loans
        overdue_loans = len(self.get_overdue_loans())
        
        # Most active readers (top 5)
        most_active_readers = self.db.execute_query("""
            SELECT r.name, r.reader_number, COUNT(l.id) as loan_count
            FROM readers r
            JOIN loans l ON r.id = l.reader_id
            GROUP BY r.id, r.name, r.reader_number
            ORDER BY loan_count DESC
            LIMIT 5
        """)
        
        # Most borrowed books (top 5)
        most_borrowed_books = self.db.execute_query("""
            SELECT b.title, b.book_number, COUNT(l.id) as loan_count
            FROM books b
            JOIN loans l ON b.id = l.book_id
            GROUP BY b.id, b.title, b.book_number
            ORDER BY loan_count DESC
            LIMIT 5
        """)
        
        return {
            'total_loans': total_loans,
            'active_loans': active_loans,
            'returned_loans': returned_loans,
            'overdue_loans': overdue_loans,
            'most_active_readers': [
                {
                    'name': row['name'],
                    'reader_number': row['reader_number'],
                    'loan_count': row['loan_count']
                }
                for row in most_active_readers
            ],
            'most_borrowed_books': [
                {
                    'title': row['title'],
                    'book_number': row['book_number'],
                    'loan_count': row['loan_count']
                }
                for row in most_borrowed_books
            ]
        }
    
    def is_book_available(self, book_id: int) -> bool:
        """
        Check if a book is available for borrowing.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            True if book is available, False if borrowed
        """
        active_loan = self.db.execute_query(
            "SELECT id FROM loans WHERE book_id = ? AND status = 'borrowed'",
            (book_id,)
        )
        
        return len(active_loan) == 0
    
    def get_reader_loan_count(self, reader_id: int) -> dict:
        """
        Get loan counts for a specific reader.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            Dictionary with loan counts
        """
        # Total loans for reader
        total_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE reader_id = ?",
            (reader_id,)
        )[0]['count']
        
        # Active loans for reader
        active_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE reader_id = ? AND status = 'borrowed'",
            (reader_id,)
        )[0]['count']
        
        # Returned loans for reader
        returned_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE reader_id = ? AND status = 'returned'",
            (reader_id,)
        )[0]['count']
        
        return {
            'total_loans': total_loans,
            'active_loans': active_loans,
            'returned_loans': returned_loans
        }
    
    def delete_loan(self, loan_id: int) -> bool:
        """
        Delete a loan record (admin function).
        
        Note: This should be used carefully as it removes loan history.
        
        Args:
            loan_id: Loan's database ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Get loan info before deletion for audit
        loan_to_delete = None
        if self.audit_service:
            try:
                loan_to_delete = self.get_loan_by_id(loan_id)
            except Exception:
                pass
        
        affected_rows = self.db.execute_command(
            "DELETE FROM loans WHERE id = ?",
            (loan_id,)
        )
        
        # Log the deletion activity
        if affected_rows > 0 and self.audit_service and loan_to_delete:
            try:
                self.audit_service.log_deletion(loan_to_delete)
            except Exception:
                # Don't fail the deletion if audit logging fails
                pass
        
        return affected_rows > 0