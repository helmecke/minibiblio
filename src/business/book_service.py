from typing import List, Optional
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import Book

class BookService:
    """Service class for managing library books with CRUD operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize book service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def create_book(self, book_number: str, title: str, author: str = None, 
                   isbn: str = None, publication_year: int = None) -> Book:
        """
        Create a new library book.
        
        Args:
            book_number: Unique book identifier/number
            title: Book title
            author: Book author (optional)
            isbn: ISBN number (optional)
            publication_year: Publication year (optional)
            
        Returns:
            Created Book object with assigned ID
            
        Raises:
            ValueError: If validation fails or book number already exists
            RuntimeError: If database operation fails
        """
        # Check if book number already exists
        if not self.validate_book_number_unique(book_number):
            raise ValueError(f"Book number '{book_number}' already exists")
        
        # Create book object for validation
        book = Book(
            book_number=book_number.strip(),
            title=title.strip(),
            author=author.strip() if author else None,
            isbn=isbn.strip() if isbn else None,
            publication_year=publication_year
        )
        
        # Insert into database
        book_id = self.db.execute_command(
            "INSERT INTO books (book_number, title, author, isbn, publication_year) VALUES (?, ?, ?, ?, ?)",
            (book.book_number, book.title, book.author, book.isbn, book.publication_year)
        )
        
        # Return created book with ID
        book.id = book_id
        book.created_date = datetime.now()
        
        return book
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get book by ID.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            Book object if found, None otherwise
        """
        rows = self.db.execute_query(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        )
        
        return Book.from_db_row(rows[0]) if rows else None
    
    def get_book_by_number(self, book_number: str) -> Optional[Book]:
        """
        Get book by book number.
        
        Args:
            book_number: Book's unique identifier
            
        Returns:
            Book object if found, None otherwise
        """
        rows = self.db.execute_query(
            "SELECT * FROM books WHERE book_number = ?",
            (book_number.strip(),)
        )
        
        return Book.from_db_row(rows[0]) if rows else None
    
    def get_all_books(self) -> List[Book]:
        """
        Get all books ordered by book number.
        
        Returns:
            List of all Book objects
        """
        rows = self.db.execute_query(
            "SELECT * FROM books ORDER BY book_number"
        )
        
        return [Book.from_db_row(row) for row in rows]
    
    def search_books_by_title(self, title_query: str) -> List[Book]:
        """
        Search books by title (case-insensitive partial match).
        
        Args:
            title_query: Search query for book title
            
        Returns:
            List of matching Book objects
        """
        if not title_query.strip():
            return []
        
        search_term = f"%{title_query.strip()}%"
        rows = self.db.execute_query(
            "SELECT * FROM books WHERE title LIKE ? ORDER BY book_number",
            (search_term,)
        )
        
        return [Book.from_db_row(row) for row in rows]
    
    def search_books_by_author(self, author_query: str) -> List[Book]:
        """
        Search books by author (case-insensitive partial match).
        
        Args:
            author_query: Search query for book author
            
        Returns:
            List of matching Book objects
        """
        if not author_query.strip():
            return []
        
        search_term = f"%{author_query.strip()}%"
        rows = self.db.execute_query(
            "SELECT * FROM books WHERE author LIKE ? ORDER BY book_number",
            (search_term,)
        )
        
        return [Book.from_db_row(row) for row in rows]
    
    def search_books_by_number(self, number_query: str) -> List[Book]:
        """
        Search books by book number (case-insensitive partial match).
        
        Args:
            number_query: Search query for book number
            
        Returns:
            List of matching Book objects
        """
        if not number_query.strip():
            return []
        
        search_term = f"%{number_query.strip()}%"
        rows = self.db.execute_query(
            "SELECT * FROM books WHERE book_number LIKE ? ORDER BY book_number",
            (search_term,)
        )
        
        return [Book.from_db_row(row) for row in rows]
    
    def search_books(self, query: str) -> List[Book]:
        """
        Search books by title, author, or book number.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Book objects (deduplicated)
        """
        if not query.strip():
            return []
        
        # Search in multiple fields
        search_term = f"%{query.strip()}%"
        rows = self.db.execute_query("""
            SELECT DISTINCT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR book_number LIKE ?
            ORDER BY book_number
        """, (search_term, search_term, search_term))
        
        return [Book.from_db_row(row) for row in rows]
    
    def update_book(self, book_id: int, book_number: str = None, title: str = None, 
                   author: str = None, isbn: str = None, publication_year: int = None) -> Optional[Book]:
        """
        Update book information.
        
        Args:
            book_id: Book's database ID
            book_number: New book number (optional)
            title: New title (optional)
            author: New author (optional)
            isbn: New ISBN (optional)
            publication_year: New publication year (optional)
            
        Returns:
            Updated Book object if successful, None if book not found
            
        Raises:
            ValueError: If validation fails or book number already exists
            RuntimeError: If database operation fails
        """
        # Get existing book
        existing_book = self.get_book_by_id(book_id)
        if not existing_book:
            return None
        
        # Prepare update values
        update_book_number = book_number.strip() if book_number is not None else existing_book.book_number
        update_title = title.strip() if title is not None else existing_book.title
        update_author = author.strip() if author is not None else existing_book.author
        update_isbn = isbn.strip() if isbn is not None else existing_book.isbn
        update_publication_year = publication_year if publication_year is not None else existing_book.publication_year
        
        # Check book number uniqueness if it's being changed
        if update_book_number != existing_book.book_number:
            if not self.validate_book_number_unique(update_book_number, exclude_id=book_id):
                raise ValueError(f"Book number '{update_book_number}' already exists")
        
        # Validate updated data
        updated_book = Book(
            id=existing_book.id,
            book_number=update_book_number,
            title=update_title,
            author=update_author if update_author else None,
            isbn=update_isbn if update_isbn else None,
            publication_year=update_publication_year,
            created_date=existing_book.created_date
        )
        
        # Update database
        affected_rows = self.db.execute_command(
            "UPDATE books SET book_number = ?, title = ?, author = ?, isbn = ?, publication_year = ? WHERE id = ?",
            (update_book_number, update_title, update_author, update_isbn, update_publication_year, book_id)
        )
        
        return updated_book if affected_rows > 0 else None
    
    def delete_book(self, book_id: int) -> bool:
        """
        Delete a book from the database.
        
        Note: This will only succeed if the book has no active loans.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            True if deletion was successful, False otherwise
            
        Raises:
            ValueError: If book has active loans
        """
        # Check for any loan history
        any_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE book_id = ?",
            (book_id,)
        )
        
        if any_loans and any_loans[0]['count'] > 0:
            raise ValueError("Cannot delete book with loan history")
        
        # Delete book
        affected_rows = self.db.execute_command(
            "DELETE FROM books WHERE id = ?",
            (book_id,)
        )
        
        return affected_rows > 0
    
    def get_book_with_loans(self, book_id: int) -> Optional[dict]:
        """
        Get book information along with its loan history.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            Dictionary with book info and loans, None if book not found
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        # Get loan history with reader information
        loan_rows = self.db.execute_query("""
            SELECT l.*, r.name, r.reader_number 
            FROM loans l
            JOIN readers r ON l.reader_id = r.id
            WHERE l.book_id = ?
            ORDER BY l.borrow_date DESC
        """, (book_id,))
        
        loans = []
        for row in loan_rows:
            loan_data = {
                'id': row['id'],
                'reader_name': row['name'],
                'reader_number': row['reader_number'],
                'borrow_date': row['borrow_date'],
                'return_date': row['return_date'],
                'status': row['status']
            }
            loans.append(loan_data)
        
        return {
            'book': book,
            'loans': loans,
            'active_loans_count': len([l for l in loans if l['status'] == 'borrowed']),
            'total_loans_count': len(loans),
            'is_available': len([l for l in loans if l['status'] == 'borrowed']) == 0
        }
    
    def get_available_books(self) -> List[Book]:
        """
        Get all books that are currently available (not borrowed).
        
        Returns:
            List of available Book objects
        """
        rows = self.db.execute_query("""
            SELECT b.* FROM books b
            WHERE b.id NOT IN (
                SELECT DISTINCT book_id FROM loans 
                WHERE status = 'borrowed'
            )
            ORDER BY b.book_number
        """)
        
        return [Book.from_db_row(row) for row in rows]
    
    def get_borrowed_books(self) -> List[dict]:
        """
        Get all books that are currently borrowed with reader information.
        
        Returns:
            List of dictionaries containing book and reader information
        """
        rows = self.db.execute_query("""
            SELECT b.*, l.borrow_date, r.name as reader_name, r.reader_number
            FROM books b
            JOIN loans l ON b.id = l.book_id
            JOIN readers r ON l.reader_id = r.id
            WHERE l.status = 'borrowed'
            ORDER BY b.book_number
        """)
        
        borrowed_books = []
        for row in rows:
            book_data = {
                'book': Book.from_db_row(row),
                'reader_name': row['reader_name'],
                'reader_number': row['reader_number'],
                'borrow_date': row['borrow_date']
            }
            borrowed_books.append(book_data)
        
        return borrowed_books
    
    def validate_book_number_unique(self, book_number: str, exclude_id: int = None) -> bool:
        """
        Check if book number is unique.
        
        Args:
            book_number: Book number to check
            exclude_id: Book ID to exclude from check (for updates)
            
        Returns:
            True if book number is unique, False otherwise
        """
        query = "SELECT COUNT(*) as count FROM books WHERE book_number = ?"
        params = [book_number.strip()]
        
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        
        result = self.db.execute_query(query, tuple(params))
        return result[0]['count'] == 0 if result else False
    
    def generate_book_number(self, prefix: str = "B") -> str:
        """
        Generate a new unique book number with the given prefix.
        
        Args:
            prefix: Prefix for the book number (default: "B")
            
        Returns:
            New unique book number
        """
        # Get the highest existing number with this prefix
        rows = self.db.execute_query(
            "SELECT book_number FROM books WHERE book_number LIKE ? ORDER BY book_number DESC LIMIT 1",
            (f"{prefix}%",)
        )
        
        if rows:
            last_number = rows[0]['book_number']
            try:
                # Extract numeric part and increment
                numeric_part = int(last_number[len(prefix):])
                new_number = numeric_part + 1
            except (ValueError, IndexError):
                # If can't parse, start from 1
                new_number = 1
        else:
            new_number = 1
        
        # Format with leading zeros (e.g., B001, B002, etc.)
        return f"{prefix}{new_number:03d}"