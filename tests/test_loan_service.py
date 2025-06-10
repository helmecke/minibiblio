import unittest
import tempfile
import os
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.db_manager import DatabaseManager
from business.loan_service import LoanService
from database.models import Loan, SearchResult, Reader, Book

class TestLoanService(unittest.TestCase):
    """Unit tests for LoanService class."""
    
    def setUp(self):
        """Set up test database and service before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.loan_service = LoanService(self.db_manager)
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_data(self):
        """Create test readers and books."""
        # Create test readers
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader 1", "Address 1", "Phone 1")
        )
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (2, "Test Reader 2", "Address 2", "Phone 2")
        )
        
        # Create test books
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title, author) VALUES (?, ?, ?)",
            ("B001", "Test Book 1", "Author 1")
        )
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title, author) VALUES (?, ?, ?)",
            ("B002", "Test Book 2", "Author 2")
        )
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title, author) VALUES (?, ?, ?)",
            ("B003", "Test Book 3", "Author 3")
        )
        
        # Get IDs for use in tests
        self.reader1_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (1,))[0]['id']
        self.reader2_id = self.db_manager.execute_query("SELECT id FROM readers WHERE reader_number = ?", (2,))[0]['id']
        self.book1_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B001",))[0]['id']
        self.book2_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B002",))[0]['id']
        self.book3_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B003",))[0]['id']
    
    def test_check_out_book_success(self):
        """Test successful book checkout."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Assertions
        self.assertIsNotNone(loan.id)
        self.assertEqual(loan.reader_id, self.reader1_id)
        self.assertEqual(loan.book_id, self.book1_id)
        self.assertEqual(loan.borrow_date, date.today())
        self.assertEqual(loan.status, "borrowed")
        self.assertIsNone(loan.return_date)
        self.assertIsNotNone(loan.created_date)
    
    def test_check_out_book_with_custom_date(self):
        """Test book checkout with custom borrow date."""
        custom_date = date(2024, 1, 15)
        
        # Check out book with custom date
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id, custom_date)
        
        # Assertions
        self.assertEqual(loan.borrow_date, custom_date)
        self.assertEqual(loan.status, "borrowed")
    
    def test_check_out_book_invalid_reader(self):
        """Test checkout with invalid reader ID."""
        with self.assertRaises(ValueError) as context:
            self.loan_service.check_out_book(999, self.book1_id)
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_check_out_book_invalid_book(self):
        """Test checkout with invalid book ID."""
        with self.assertRaises(ValueError) as context:
            self.loan_service.check_out_book(self.reader1_id, 999)
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_check_out_book_already_borrowed(self):
        """Test checkout of already borrowed book."""
        # First checkout
        self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Try to checkout same book to different reader
        with self.assertRaises(ValueError) as context:
            self.loan_service.check_out_book(self.reader2_id, self.book1_id)
        
        self.assertIn("already borrowed", str(context.exception))
    
    def test_return_book_success(self):
        """Test successful book return."""
        # Check out book first
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Return book
        returned_loan = self.loan_service.return_book(loan.id)
        
        # Assertions
        self.assertEqual(returned_loan.id, loan.id)
        self.assertEqual(returned_loan.status, "returned")
        self.assertEqual(returned_loan.return_date, date.today())
        self.assertIsNotNone(returned_loan.borrow_date)
    
    def test_return_book_with_custom_date(self):
        """Test book return with custom return date."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        custom_return_date = date.today() + timedelta(days=1)  # Tomorrow
        
        # Return book with custom date
        returned_loan = self.loan_service.return_book(loan.id, custom_return_date)
        
        # Assertions
        self.assertEqual(returned_loan.return_date, custom_return_date)
        self.assertEqual(returned_loan.status, "returned")
    
    def test_return_book_invalid_loan(self):
        """Test return with invalid loan ID."""
        with self.assertRaises(ValueError) as context:
            self.loan_service.return_book(999)
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_return_book_already_returned(self):
        """Test return of already returned book."""
        # Check out and return book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.return_book(loan.id)
        
        # Try to return again
        with self.assertRaises(ValueError) as context:
            self.loan_service.return_book(loan.id)
        
        self.assertIn("already been returned", str(context.exception))
    
    def test_return_book_invalid_date(self):
        """Test return with date before borrow date."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Try to return with date before borrow date
        invalid_return_date = loan.borrow_date - timedelta(days=1)
        
        with self.assertRaises(ValueError) as context:
            self.loan_service.return_book(loan.id, invalid_return_date)
        
        self.assertIn("cannot be before borrow date", str(context.exception))
    
    def test_return_book_by_book_id_success(self):
        """Test successful book return by book ID."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Return by book ID
        returned_loan = self.loan_service.return_book_by_book_id(self.book1_id)
        
        # Assertions
        self.assertEqual(returned_loan.id, loan.id)
        self.assertEqual(returned_loan.status, "returned")
    
    def test_return_book_by_book_id_no_active_loan(self):
        """Test return by book ID with no active loan."""
        with self.assertRaises(ValueError) as context:
            self.loan_service.return_book_by_book_id(self.book1_id)
        
        self.assertIn("No active loan found", str(context.exception))
    
    def test_get_loan_by_id(self):
        """Test getting loan by ID with reader and book info."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Get loan by ID
        retrieved_loan = self.loan_service.get_loan_by_id(loan.id)
        
        # Assertions
        self.assertIsNotNone(retrieved_loan)
        self.assertEqual(retrieved_loan.id, loan.id)
        self.assertEqual(retrieved_loan.reader_name, "Test Reader 1")
        self.assertEqual(retrieved_loan.book_title, "Test Book 1")
        self.assertEqual(retrieved_loan.book_number, "B001")
    
    def test_get_loan_by_id_not_found(self):
        """Test getting non-existent loan by ID."""
        result = self.loan_service.get_loan_by_id(999)
        self.assertIsNone(result)
    
    def test_get_active_loans(self):
        """Test getting all active loans."""
        # Initially no active loans
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 0)
        
        # Check out some books
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        # Get active loans
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 2)
        
        # Return one book
        self.loan_service.return_book(loan1.id)
        
        # Should now have only one active loan
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 1)
        self.assertEqual(active_loans[0].id, loan2.id)
    
    def test_get_loans_by_reader(self):
        """Test getting loans for specific reader."""
        # Check out books for reader 1
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader1_id, self.book2_id)
        
        # Return one book
        self.loan_service.return_book(loan1.id)
        
        # Check out book for reader 2
        self.loan_service.check_out_book(self.reader2_id, self.book3_id)
        
        # Get loans for reader 1
        reader1_loans = self.loan_service.get_loans_by_reader(self.reader1_id)
        self.assertEqual(len(reader1_loans), 2)  # Both loans (active and returned)
        
        # Get loans for reader 2
        reader2_loans = self.loan_service.get_loans_by_reader(self.reader2_id)
        self.assertEqual(len(reader2_loans), 1)
    
    def test_get_loans_by_book(self):
        """Test getting loans for specific book."""
        # Check out and return book multiple times
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.return_book(loan1.id)
        
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book1_id)
        
        # Get loans for book 1
        book1_loans = self.loan_service.get_loans_by_book(self.book1_id)
        self.assertEqual(len(book1_loans), 2)
        
        # Verify loan details
        self.assertIn(loan1.id, [loan.id for loan in book1_loans])
        self.assertIn(loan2.id, [loan.id for loan in book1_loans])
    
    def test_get_active_loans_by_reader(self):
        """Test getting active loans for specific reader."""
        # Check out books for reader 1
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader1_id, self.book2_id)
        
        # Return one book
        self.loan_service.return_book(loan1.id)
        
        # Get active loans for reader 1
        active_loans = self.loan_service.get_active_loans_by_reader(self.reader1_id)
        self.assertEqual(len(active_loans), 1)
        self.assertEqual(active_loans[0].id, loan2.id)
    
    def test_get_overdue_loans(self):
        """Test getting overdue loans."""
        # Create loan with past date
        past_date = date.today() - timedelta(days=20)  # 20 days ago
        
        # Insert overdue loan directly
        due_date = past_date + timedelta(days=14)
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (self.reader1_id, self.book1_id, past_date.isoformat(), due_date.isoformat(), "borrowed")
        )
        
        # Create recent loan
        self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        # Get overdue loans (default 14 days)
        overdue_loans = self.loan_service.get_overdue_loans()
        self.assertEqual(len(overdue_loans), 1)
        
        # The recent loan should not be overdue since it has a due date 14 days from today
    
    def test_extend_loan_success(self):
        """Test successful loan extension."""
        # Create loan
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        original_due_date = loan.due_date
        
        # Extend loan by 7 days
        extended_loan = self.loan_service.extend_loan(loan.id, 7)
        
        self.assertEqual(extended_loan.id, loan.id)
        self.assertEqual(extended_loan.due_date, original_due_date + timedelta(days=7))
        self.assertEqual(extended_loan.status, "borrowed")
    
    def test_extend_loan_invalid_id(self):
        """Test loan extension with invalid loan ID."""
        with self.assertRaises(ValueError) as context:
            self.loan_service.extend_loan(999, 7)
        self.assertIn("does not exist", str(context.exception))
    
    def test_extend_loan_already_returned(self):
        """Test extending already returned loan."""
        # Create and return loan
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.return_book(loan.id)
        
        # Try to extend returned loan
        with self.assertRaises(ValueError) as context:
            self.loan_service.extend_loan(loan.id, 7)
        self.assertIn("Cannot extend a returned loan", str(context.exception))
    
    def test_extend_loan_multiple_times(self):
        """Test extending loan multiple times."""
        # Create loan
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        original_due_date = loan.due_date
        
        # First extension
        extended_loan1 = self.loan_service.extend_loan(loan.id, 7)
        self.assertEqual(extended_loan1.due_date, original_due_date + timedelta(days=7))
        
        # Second extension
        extended_loan2 = self.loan_service.extend_loan(loan.id, 14)
        self.assertEqual(extended_loan2.due_date, original_due_date + timedelta(days=21))
    
    def test_extend_loan_custom_days(self):
        """Test loan extension with different day amounts."""
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        original_due_date = loan.due_date
        
        # Test different extension periods
        test_cases = [1, 3, 7, 14, 30]
        
        for days in test_cases:
            # Reset loan for each test
            current_loan = self.loan_service.get_loan_by_id(loan.id)
            current_due_date = current_loan.due_date
            
            extended_loan = self.loan_service.extend_loan(loan.id, days)
            self.assertEqual(extended_loan.due_date, current_due_date + timedelta(days=days))
    
    def test_extend_loan_with_overdue(self):
        """Test extending an overdue loan."""
        # Create loan with past due date
        past_date = date.today() - timedelta(days=20)
        past_due_date = past_date + timedelta(days=14)  # 6 days overdue
        
        # Insert overdue loan directly
        loan_id = self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (self.reader1_id, self.book1_id, past_date.isoformat(), past_due_date.isoformat(), "borrowed")
        )
        
        # Extend the overdue loan
        extended_loan = self.loan_service.extend_loan(loan_id, 14)
        
        self.assertEqual(extended_loan.due_date, past_due_date + timedelta(days=14))
        self.assertEqual(extended_loan.status, "borrowed")
        
        # Should no longer be overdue
        overdue_loans = self.loan_service.get_overdue_loans()
        self.assertEqual(len(overdue_loans), 0)
    
    def test_extend_loan_edge_cases(self):
        """Test loan extension edge cases."""
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Test with zero days (should work but not change date)
        original_due_date = loan.due_date
        extended_loan = self.loan_service.extend_loan(loan.id, 0)
        self.assertEqual(extended_loan.due_date, original_due_date)
        
        # Test with large number of days
        large_extension = self.loan_service.extend_loan(loan.id, 365)
        self.assertEqual(large_extension.due_date, original_due_date + timedelta(days=365))
    
    def test_loan_with_due_date_validation(self):
        """Test loan creation with proper due date validation."""
        # Test checkout with custom date and duration
        custom_date = date.today() + timedelta(days=5)
        custom_duration = 21
        
        loan = self.loan_service.check_out_book(
            self.reader1_id, 
            self.book1_id, 
            borrow_date=custom_date,
            loan_duration_days=custom_duration
        )
        
        expected_due_date = custom_date + timedelta(days=custom_duration)
        self.assertEqual(loan.borrow_date, custom_date)
        self.assertEqual(loan.due_date, expected_due_date)
    
    def test_overdue_loans_with_due_dates(self):
        """Test overdue loan detection using due dates."""
        today = date.today()
        
        # Create loans with different due dates
        # Overdue loan (due yesterday)
        overdue_loan = self.loan_service.check_out_book(
            self.reader1_id, 
            self.book1_id, 
            borrow_date=today - timedelta(days=15),
            loan_duration_days=14
        )
        
        # Due today (not overdue)
        due_today_loan = self.loan_service.check_out_book(
            self.reader2_id, 
            self.book2_id, 
            borrow_date=today - timedelta(days=14),
            loan_duration_days=14
        )
        
        # Get overdue loans
        overdue_loans = self.loan_service.get_overdue_loans()
        
        # Should find only the overdue loan
        self.assertEqual(len(overdue_loans), 1)
        self.assertEqual(overdue_loans[0].id, overdue_loan.id)
    
    def test_get_loan_history(self):
        """Test getting loan history."""
        # Check out and return some books
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        self.loan_service.return_book(loan1.id)
        
        # Get all loan history
        history = self.loan_service.get_loan_history()
        self.assertEqual(len(history), 2)
        
        # Get limited history
        limited_history = self.loan_service.get_loan_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_search_loans_by_reader_name(self):
        """Test searching loans by reader name."""
        # Check out books
        self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        # Search by reader name
        results = self.loan_service.search_loans_by_reader_name("Test Reader 1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].reader_name, "Test Reader 1")
        
        # Search with partial name
        results = self.loan_service.search_loans_by_reader_name("Reader")
        self.assertEqual(len(results), 2)
        
        # Search with no matches
        results = self.loan_service.search_loans_by_reader_name("xyz")
        self.assertEqual(len(results), 0)
    
    def test_search_loans_by_book_title(self):
        """Test searching loans by book title."""
        # Check out books
        self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        # Search by book title
        results = self.loan_service.search_loans_by_book_title("Test Book 1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book_title, "Test Book 1")
        
        # Search with partial title
        results = self.loan_service.search_loans_by_book_title("Book")
        self.assertEqual(len(results), 2)
    
    def test_search_loans_by_book_number(self):
        """Test searching loans by book number."""
        # Check out books
        self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        # Search by book number
        results = self.loan_service.search_loans_by_book_number("B001")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book_number, "B001")
        
        # Search with partial number
        results = self.loan_service.search_loans_by_book_number("B00")
        self.assertEqual(len(results), 2)
    
    def test_is_book_available(self):
        """Test checking book availability."""
        # Initially book should be available
        self.assertTrue(self.loan_service.is_book_available(self.book1_id))
        
        # Check out book
        self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Book should not be available
        self.assertFalse(self.loan_service.is_book_available(self.book1_id))
        
        # Other books should still be available
        self.assertTrue(self.loan_service.is_book_available(self.book2_id))
    
    def test_get_reader_loan_count(self):
        """Test getting loan counts for reader."""
        # Initially no loans
        counts = self.loan_service.get_reader_loan_count(self.reader1_id)
        self.assertEqual(counts['total_loans'], 0)
        self.assertEqual(counts['active_loans'], 0)
        self.assertEqual(counts['returned_loans'], 0)
        
        # Check out books
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader1_id, self.book2_id)
        
        # Return one book
        self.loan_service.return_book(loan1.id)
        
        # Check counts
        counts = self.loan_service.get_reader_loan_count(self.reader1_id)
        self.assertEqual(counts['total_loans'], 2)
        self.assertEqual(counts['active_loans'], 1)
        self.assertEqual(counts['returned_loans'], 1)
    
    def test_get_loan_statistics(self):
        """Test getting loan statistics."""
        # Check out and return some books
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        loan3 = self.loan_service.check_out_book(self.reader1_id, self.book3_id)
        
        # Return one book
        self.loan_service.return_book(loan1.id)
        
        # Get statistics
        stats = self.loan_service.get_loan_statistics()
        
        # Check basic counts
        self.assertEqual(stats['total_loans'], 3)
        self.assertEqual(stats['active_loans'], 2)
        self.assertEqual(stats['returned_loans'], 1)
        self.assertEqual(stats['overdue_loans'], 0)  # No overdue loans
        
        # Check most active readers
        self.assertGreater(len(stats['most_active_readers']), 0)
        self.assertEqual(stats['most_active_readers'][0]['name'], "Test Reader 1")  # 2 loans
        self.assertEqual(stats['most_active_readers'][0]['loan_count'], 2)
        
        # Check most borrowed books
        self.assertGreater(len(stats['most_borrowed_books']), 0)
    
    def test_delete_loan(self):
        """Test deleting a loan record."""
        # Check out book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Delete loan
        result = self.loan_service.delete_loan(loan.id)
        self.assertTrue(result)
        
        # Verify deletion
        deleted_loan = self.loan_service.get_loan_by_id(loan.id)
        self.assertIsNone(deleted_loan)
        
        # Try to delete non-existent loan
        result = self.loan_service.delete_loan(999)
        self.assertFalse(result)

class TestLoanModel(unittest.TestCase):
    """Unit tests for Loan model class."""
    
    def test_loan_creation_success(self):
        """Test successful loan creation."""
        loan = Loan(
            id=1,
            reader_id=1,
            book_id=1,
            borrow_date=date.today(),
            status="borrowed"
        )
        
        self.assertEqual(loan.reader_id, 1)
        self.assertEqual(loan.book_id, 1)
        self.assertEqual(loan.status, "borrowed")
        self.assertIsNone(loan.return_date)
    
    def test_loan_validation_errors(self):
        """Test loan validation errors."""
        # Test invalid reader ID
        with self.assertRaises(ValueError):
            Loan(reader_id=0, book_id=1, borrow_date=date.today())
        
        # Test invalid book ID
        with self.assertRaises(ValueError):
            Loan(reader_id=1, book_id=0, borrow_date=date.today())
        
        # Test invalid status
        with self.assertRaises(ValueError):
            Loan(reader_id=1, book_id=1, borrow_date=date.today(), status="invalid")
        
        # Test return date before borrow date
        with self.assertRaises(ValueError):
            Loan(
                reader_id=1, 
                book_id=1, 
                borrow_date=date.today(),
                return_date=date.today() - timedelta(days=1)
            )
    
    def test_loan_is_active(self):
        """Test checking if loan is active."""
        # Active loan
        active_loan = Loan(
            reader_id=1,
            book_id=1,
            borrow_date=date.today(),
            status="borrowed"
        )
        self.assertTrue(active_loan.is_active())
        
        # Returned loan
        returned_loan = Loan(
            reader_id=1,
            book_id=1,
            borrow_date=date.today(),
            return_date=date.today(),
            status="returned"
        )
        self.assertFalse(returned_loan.is_active())
    
    def test_loan_mark_returned(self):
        """Test marking loan as returned."""
        loan = Loan(
            reader_id=1,
            book_id=1,
            borrow_date=date.today(),
            status="borrowed"
        )
        
        # Mark as returned with default date
        loan.mark_returned()
        self.assertEqual(loan.status, "returned")
        self.assertEqual(loan.return_date, date.today())
        
        # Mark as returned with custom date
        custom_date = date(2024, 1, 20)
        loan2 = Loan(
            reader_id=1,
            book_id=2,
            borrow_date=date.today(),
            status="borrowed"
        )
        loan2.mark_returned(custom_date)
        self.assertEqual(loan2.return_date, custom_date)
    
    def test_loan_to_dict(self):
        """Test converting loan to dictionary."""
        loan = Loan(
            reader_id=1,
            book_id=1,
            borrow_date=date(2024, 1, 15),
            return_date=date(2024, 1, 20),
            status="returned"
        )
        
        result = loan.to_dict()
        expected = {
            'reader_id': 1,
            'book_id': 1,
            'borrow_date': '2024-01-15',
            'due_date': None,
            'return_date': '2024-01-20',
            'status': 'returned'
        }
        
        self.assertEqual(result, expected)
    
    def test_loan_from_db_row(self):
        """Test creating loan from database row."""
        # Mock database row
        class MockRow:
            def __init__(self, data):
                self.data = data
            
            def __getitem__(self, key):
                return self.data[key]
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        row_data = {
            'id': 1,
            'reader_id': 1,
            'book_id': 1,
            'borrow_date': "2024-01-15",
            'due_date': "2024-01-29",
            'return_date': "2024-01-20",
            'status': "returned",
            'created_date': "2024-01-15 12:00:00",
            'reader_name': "Test Reader",
            'book_title': "Test Book",
            'book_number': "B001"
        }
        
        row = MockRow(row_data)
        loan = Loan.from_db_row(row)
        
        self.assertEqual(loan.id, 1)
        self.assertEqual(loan.reader_id, 1)
        self.assertEqual(loan.book_id, 1)
        self.assertEqual(loan.borrow_date, date(2024, 1, 15))
        self.assertEqual(loan.due_date, date(2024, 1, 29))
        self.assertEqual(loan.return_date, date(2024, 1, 20))
        self.assertEqual(loan.status, "returned")
        self.assertEqual(loan.reader_name, "Test Reader")
        self.assertEqual(loan.book_title, "Test Book")
        self.assertEqual(loan.book_number, "B001")

class TestSearchResultModel(unittest.TestCase):
    """Unit tests for SearchResult model."""
    
    def test_search_result_reader_creation(self):
        """Test SearchResult creation with reader."""
        reader = Reader(name="Test Reader", address="Test Address", phone="123-456-7890")
        search_result = SearchResult(result_type="reader", reader=reader)
        
        self.assertEqual(search_result.result_type, "reader")
        self.assertEqual(search_result.reader, reader)
        self.assertIsNone(search_result.book)
        self.assertIsNone(search_result.loan)
    
    def test_search_result_book_creation(self):
        """Test SearchResult creation with book."""
        book = Book(book_number="B001", title="Test Book")
        search_result = SearchResult(result_type="book", book=book)
        
        self.assertEqual(search_result.result_type, "book")
        self.assertEqual(search_result.book, book)
        self.assertIsNone(search_result.reader)
        self.assertIsNone(search_result.loan)
    
    def test_search_result_loan_creation(self):
        """Test SearchResult creation with loan."""
        loan = Loan(reader_id=1, book_id=1, borrow_date=date.today(), due_date=date.today() + timedelta(days=14))
        search_result = SearchResult(result_type="loan", loan=loan)
        
        self.assertEqual(search_result.result_type, "loan")
        self.assertEqual(search_result.loan, loan)
        self.assertIsNone(search_result.reader)
        self.assertIsNone(search_result.book)
    
    def test_search_result_validation_errors(self):
        """Test SearchResult validation errors."""
        # Reader type without reader
        with self.assertRaises(ValueError) as context:
            SearchResult(result_type="reader")
        self.assertIn("Reader must be set for reader result type", str(context.exception))
        
        # Book type without book
        with self.assertRaises(ValueError) as context:
            SearchResult(result_type="book")
        self.assertIn("Book must be set for book result type", str(context.exception))
        
        # Loan type without loan
        with self.assertRaises(ValueError) as context:
            SearchResult(result_type="loan")
        self.assertIn("Loan must be set for loan result type", str(context.exception))

if __name__ == '__main__':
    unittest.main()