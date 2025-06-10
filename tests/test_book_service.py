import unittest
import tempfile
import os
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.db_manager import DatabaseManager
from business.book_service import BookService
from database.models import Book

class TestBookService(unittest.TestCase):
    """Unit tests for BookService class."""
    
    def setUp(self):
        """Set up test database and service before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.book_service = BookService(self.db_manager)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_book_success(self):
        """Test successful book creation."""
        # Test data
        book_number = "B001"
        title = "Test Book"
        author = "Test Author"
        isbn = "978-3-123456-78-9"
        publication_year = 2024
        
        # Create book
        book = self.book_service.create_book(book_number, title, author, isbn, publication_year)
        
        # Assertions
        self.assertIsNotNone(book.id)
        self.assertEqual(book.book_number, book_number)
        self.assertEqual(book.title, title)
        self.assertEqual(book.author, author)
        self.assertEqual(book.isbn, isbn)
        self.assertEqual(book.publication_year, publication_year)
        self.assertIsNotNone(book.created_date)
    
    def test_create_book_minimal_data(self):
        """Test book creation with only required fields."""
        # Create book with minimal data
        book = self.book_service.create_book("B001", "Test Book")
        
        # Assertions
        self.assertIsNotNone(book.id)
        self.assertEqual(book.book_number, "B001")
        self.assertEqual(book.title, "Test Book")
        self.assertIsNone(book.author)
        self.assertIsNone(book.isbn)
        self.assertIsNone(book.publication_year)
    
    def test_create_book_validation_errors(self):
        """Test validation errors during book creation."""
        # Test empty book number
        with self.assertRaises(ValueError):
            self.book_service.create_book("", "Title")
        
        # Test empty title
        with self.assertRaises(ValueError):
            self.book_service.create_book("B001", "")
        
        # Test whitespace-only fields
        with self.assertRaises(ValueError):
            self.book_service.create_book("   ", "Title")
        
        # Test negative publication year
        with self.assertRaises(ValueError):
            self.book_service.create_book("B001", "Title", publication_year=-1)
    
    def test_create_book_duplicate_number(self):
        """Test error when creating book with duplicate number."""
        # Create first book
        self.book_service.create_book("B001", "First Book")
        
        # Try to create second book with same number
        with self.assertRaises(ValueError) as context:
            self.book_service.create_book("B001", "Second Book")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_get_book_by_id(self):
        """Test retrieving book by ID."""
        # Create a book
        created_book = self.book_service.create_book("B001", "Test Book", "Test Author")
        
        # Retrieve by ID
        retrieved_book = self.book_service.get_book_by_id(created_book.id)
        
        # Assertions
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.id, created_book.id)
        self.assertEqual(retrieved_book.book_number, created_book.book_number)
        self.assertEqual(retrieved_book.title, created_book.title)
        self.assertEqual(retrieved_book.author, created_book.author)
    
    def test_get_book_by_id_not_found(self):
        """Test retrieving non-existent book by ID."""
        result = self.book_service.get_book_by_id(999)
        self.assertIsNone(result)
    
    def test_get_book_by_number(self):
        """Test retrieving book by book number."""
        # Create a book
        created_book = self.book_service.create_book("B001", "Test Book")
        
        # Retrieve by book number
        retrieved_book = self.book_service.get_book_by_number("B001")
        
        # Assertions
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.book_number, created_book.book_number)
        self.assertEqual(retrieved_book.title, created_book.title)
    
    def test_get_book_by_number_not_found(self):
        """Test retrieving non-existent book by number."""
        result = self.book_service.get_book_by_number("B999")
        self.assertIsNone(result)
    
    def test_get_all_books(self):
        """Test retrieving all books."""
        # Initially should be empty
        books = self.book_service.get_all_books()
        self.assertEqual(len(books), 0)
        
        # Create some books
        book1 = self.book_service.create_book("B003", "Book 3")
        book2 = self.book_service.create_book("B001", "Book 1")
        book3 = self.book_service.create_book("B002", "Book 2")
        
        # Retrieve all
        books = self.book_service.get_all_books()
        
        # Assertions
        self.assertEqual(len(books), 3)
        # Should be ordered by book number
        self.assertEqual(books[0].book_number, "B001")
        self.assertEqual(books[1].book_number, "B002")
        self.assertEqual(books[2].book_number, "B003")
    
    def test_search_books_by_title(self):
        """Test searching books by title."""
        # Create test books
        self.book_service.create_book("B001", "Python Programming", "John Doe")
        self.book_service.create_book("B002", "Java Development", "Jane Smith")
        self.book_service.create_book("B003", "Python for Beginners", "Bob Wilson")
        self.book_service.create_book("B004", "Web Development", "Alice Brown")
        
        # Test exact match
        results = self.book_service.search_books_by_title("Python Programming")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Programming")
        
        # Test partial match
        results = self.book_service.search_books_by_title("Python")
        self.assertEqual(len(results), 2)
        
        # Test case insensitive
        results = self.book_service.search_books_by_title("development")
        self.assertEqual(len(results), 2)  # Java Development and Web Development
        
        # Test no matches
        results = self.book_service.search_books_by_title("xyz")
        self.assertEqual(len(results), 0)
        
        # Test empty query
        results = self.book_service.search_books_by_title("")
        self.assertEqual(len(results), 0)
    
    def test_search_books_by_author(self):
        """Test searching books by author."""
        # Create test books
        self.book_service.create_book("B001", "Book 1", "John Smith")
        self.book_service.create_book("B002", "Book 2", "Jane Doe")
        self.book_service.create_book("B003", "Book 3", "John Wilson")
        
        # Test partial match
        results = self.book_service.search_books_by_author("John")
        self.assertEqual(len(results), 2)
        
        # Test case insensitive
        results = self.book_service.search_books_by_author("doe")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].author, "Jane Doe")
    
    def test_search_books_by_number(self):
        """Test searching books by book number."""
        # Create test books
        self.book_service.create_book("B001", "Book 1")
        self.book_service.create_book("B002", "Book 2")
        self.book_service.create_book("C001", "Book 3")
        
        # Test prefix search
        results = self.book_service.search_books_by_number("B00")
        self.assertEqual(len(results), 2)
        
        # Test exact match
        results = self.book_service.search_books_by_number("C001")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book_number, "C001")
    
    def test_search_books_general(self):
        """Test general search across all fields."""
        # Create test books
        self.book_service.create_book("B001", "Python Programming", "John Doe")
        self.book_service.create_book("B002", "Java Development", "Jane Smith")
        
        # Search by title
        results = self.book_service.search_books("Python")
        self.assertEqual(len(results), 1)
        
        # Search by author
        results = self.book_service.search_books("John")
        self.assertEqual(len(results), 1)
        
        # Search by book number
        results = self.book_service.search_books("B002")
        self.assertEqual(len(results), 1)
    
    def test_update_book_success(self):
        """Test successful book update."""
        # Create a book
        book = self.book_service.create_book("B001", "Original Title", "Original Author")
        
        # Update book
        updated_book = self.book_service.update_book(
            book.id,
            book_number="B002",
            title="Updated Title",
            author="Updated Author",
            isbn="978-3-123456-78-9",
            publication_year=2024
        )
        
        # Assertions
        self.assertIsNotNone(updated_book)
        self.assertEqual(updated_book.id, book.id)
        self.assertEqual(updated_book.book_number, "B002")
        self.assertEqual(updated_book.title, "Updated Title")
        self.assertEqual(updated_book.author, "Updated Author")
        self.assertEqual(updated_book.isbn, "978-3-123456-78-9")
        self.assertEqual(updated_book.publication_year, 2024)
    
    def test_update_book_partial(self):
        """Test partial book update."""
        # Create a book
        book = self.book_service.create_book("B001", "Original Title", "Original Author")
        
        # Update only title
        updated_book = self.book_service.update_book(book.id, title="New Title")
        
        # Assertions
        self.assertEqual(updated_book.title, "New Title")
        self.assertEqual(updated_book.book_number, "B001")  # Should remain unchanged
        self.assertEqual(updated_book.author, "Original Author")  # Should remain unchanged
    
    def test_update_book_not_found(self):
        """Test updating non-existent book."""
        result = self.book_service.update_book(999, title="New Title")
        self.assertIsNone(result)
    
    def test_update_book_duplicate_number(self):
        """Test updating book with duplicate number."""
        # Create two books
        book1 = self.book_service.create_book("B001", "Book 1")
        book2 = self.book_service.create_book("B002", "Book 2")
        
        # Try to update book2 with book1's number
        with self.assertRaises(ValueError) as context:
            self.book_service.update_book(book2.id, book_number="B001")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_delete_book_success(self):
        """Test successful book deletion."""
        # Create a book
        book = self.book_service.create_book("B001", "Test Book")
        
        # Delete book
        result = self.book_service.delete_book(book.id)
        self.assertTrue(result)
        
        # Verify deletion
        deleted_book = self.book_service.get_book_by_id(book.id)
        self.assertIsNone(deleted_book)
    
    def test_delete_book_not_found(self):
        """Test deleting non-existent book."""
        result = self.book_service.delete_book(999)
        self.assertFalse(result)
    
    def test_delete_book_with_active_loans(self):
        """Test that book with active loans cannot be deleted."""
        # Create a book and reader
        book = self.book_service.create_book("B001", "Test Book")
        
        # Create a fake reader and active loan (insert directly into database)
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "Test Phone")
        )
        reader_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (1,))[0]['id']
        
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader_id, book.id, "2024-01-01", "2024-01-15", "borrowed")
        )
        
        # Try to delete book with active loan
        with self.assertRaises(ValueError) as context:
            self.book_service.delete_book(book.id)
        
        self.assertIn("loan history", str(context.exception))
    
    def test_get_book_with_loans(self):
        """Test getting book information with loan history."""
        # Create a book
        book = self.book_service.create_book("B001", "Test Book", "Test Author")
        
        # Create readers and loans
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Reader 1", "Address 1", "Phone 1")
        )
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (2, "Reader 2", "Address 2", "Phone 2")
        )
        
        reader1_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (1,))[0]['id']
        reader2_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (2,))[0]['id']
        
        # Create loans
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, return_date, status) VALUES (?, ?, ?, ?, ?, ?)",
            (reader1_id, book.id, "2024-01-01", "2024-01-15", "2024-01-15", "returned")
        )
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader2_id, book.id, "2024-02-01", "2024-02-15", "borrowed")
        )
        
        # Get book with loans
        result = self.book_service.get_book_with_loans(book.id)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['book'].id, book.id)
        self.assertEqual(len(result['loans']), 2)
        self.assertEqual(result['active_loans_count'], 1)
        self.assertEqual(result['total_loans_count'], 2)
        self.assertFalse(result['is_available'])  # Book is currently borrowed
        
        # Check loan details
        loans = result['loans']
        self.assertEqual(loans[0]['reader_name'], "Reader 2")  # Should be ordered by borrow_date DESC
        self.assertEqual(loans[0]['status'], "borrowed")
        self.assertEqual(loans[1]['reader_name'], "Reader 1")
        self.assertEqual(loans[1]['status'], "returned")
    
    def test_get_book_with_loans_not_found(self):
        """Test getting loans for non-existent book."""
        result = self.book_service.get_book_with_loans(999)
        self.assertIsNone(result)
    
    def test_get_available_books(self):
        """Test getting available books."""
        # Create books
        book1 = self.book_service.create_book("B001", "Available Book 1")
        book2 = self.book_service.create_book("B002", "Borrowed Book")
        book3 = self.book_service.create_book("B003", "Available Book 2")
        
        # Create reader and loan for book2
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "Test Phone")
        )
        reader_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (1,))[0]['id']
        
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader_id, book2.id, "2024-01-01", "2024-01-15", "borrowed")
        )
        
        # Get available books
        available_books = self.book_service.get_available_books()
        
        # Should only return book1 and book3
        self.assertEqual(len(available_books), 2)
        available_ids = {book.id for book in available_books}
        self.assertIn(book1.id, available_ids)
        self.assertIn(book3.id, available_ids)
        self.assertNotIn(book2.id, available_ids)
    
    def test_get_borrowed_books(self):
        """Test getting borrowed books."""
        # Create books
        book1 = self.book_service.create_book("B001", "Available Book")
        book2 = self.book_service.create_book("B002", "Borrowed Book")
        
        # Create reader and loan
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "Test Phone")
        )
        reader_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (1,))[0]['id']
        
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader_id, book2.id, "2024-01-01", "2024-01-15", "borrowed")
        )
        
        # Get borrowed books
        borrowed_books = self.book_service.get_borrowed_books()
        
        # Should only return book2
        self.assertEqual(len(borrowed_books), 1)
        self.assertEqual(borrowed_books[0]['book'].id, book2.id)
        self.assertEqual(borrowed_books[0]['reader_name'], "Test Reader")
        self.assertEqual(borrowed_books[0]['reader_number'], 1)
        self.assertEqual(borrowed_books[0]['borrow_date'], "2024-01-01")
    
    def test_validate_book_number_unique(self):
        """Test book number uniqueness validation."""
        # Create a book
        book = self.book_service.create_book("B001", "Test Book")
        
        # Test uniqueness check
        self.assertFalse(self.book_service.validate_book_number_unique("B001"))
        self.assertTrue(self.book_service.validate_book_number_unique("B999"))  # Non-existent number
        
        # Test excluding current book from check (for updates)
        self.assertTrue(self.book_service.validate_book_number_unique("B001", exclude_id=book.id))
    
    def test_generate_book_number(self):
        """Test automatic book number generation."""
        # Test initial generation
        book_number1 = self.book_service.generate_book_number()
        self.assertEqual(book_number1, "B001")
        
        # Create a book with this number
        self.book_service.create_book(book_number1, "Test Book 1")
        
        # Generate next number
        book_number2 = self.book_service.generate_book_number()
        self.assertEqual(book_number2, "B002")
        
        # Test custom prefix
        book_number3 = self.book_service.generate_book_number("C")
        self.assertEqual(book_number3, "C001")
        
        # Create book with custom prefix and generate next
        self.book_service.create_book(book_number3, "Test Book C1")
        book_number4 = self.book_service.generate_book_number("C")
        self.assertEqual(book_number4, "C002")

class TestBookModel(unittest.TestCase):
    """Unit tests for Book model class."""
    
    def test_book_creation_success(self):
        """Test successful book creation."""
        book = Book(
            id=1,
            book_number="B001",
            title="Test Book",
            author="Test Author",
            isbn="978-3-123456-78-9",
            publication_year=2024,
            created_date=datetime.now()
        )
        
        self.assertEqual(book.book_number, "B001")
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.isbn, "978-3-123456-78-9")
        self.assertEqual(book.publication_year, 2024)
    
    def test_book_validation_errors(self):
        """Test book validation errors."""
        # Test empty book number
        with self.assertRaises(ValueError):
            Book(book_number="", title="Title")
        
        # Test empty title
        with self.assertRaises(ValueError):
            Book(book_number="B001", title="")
        
        # Test whitespace-only fields
        with self.assertRaises(ValueError):
            Book(book_number="   ", title="Title")
        
        # Test negative publication year
        with self.assertRaises(ValueError):
            Book(book_number="B001", title="Title", publication_year=-1)
    
    def test_book_to_dict(self):
        """Test converting book to dictionary."""
        book = Book(
            book_number="B001",
            title="Test Book",
            author="Test Author",
            isbn="978-3-123456-78-9",
            publication_year=2024
        )
        
        result = book.to_dict()
        expected = {
            'book_number': "B001",
            'title': "Test Book",
            'author': "Test Author",
            'isbn': "978-3-123456-78-9",
            'publication_year': 2024
        }
        
        self.assertEqual(result, expected)
    
    def test_book_from_db_row(self):
        """Test creating book from database row."""
        # Mock database row
        class MockRow:
            def __init__(self, data):
                self.data = data
            
            def __getitem__(self, key):
                return self.data[key]
        
        row_data = {
            'id': 1,
            'book_number': "B001",
            'title': "Test Book",
            'author': "Test Author",
            'isbn': "978-3-123456-78-9",
            'publication_year': 2024,
            'created_date': "2024-01-01 12:00:00"
        }
        
        row = MockRow(row_data)
        book = Book.from_db_row(row)
        
        self.assertEqual(book.id, 1)
        self.assertEqual(book.book_number, "B001")
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.isbn, "978-3-123456-78-9")
        self.assertEqual(book.publication_year, 2024)
        self.assertIsNotNone(book.created_date)

if __name__ == '__main__':
    unittest.main()