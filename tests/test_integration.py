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
from business.reader_service import ReaderService
from business.book_service import BookService
from business.audit_service import AuditService
from database.models import Reader, Book, Loan

class TestLoanWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete loan workflows."""
    
    def setUp(self):
        """Set up test database and services before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        
        # Initialize services
        self.audit_service = AuditService(self.db_manager)
        self.loan_service = LoanService(self.db_manager, self.audit_service)
        self.reader_service = ReaderService(self.db_manager)
        self.book_service = BookService(self.db_manager)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_complete_loan_lifecycle(self):
        """Test complete loan lifecycle: checkout -> extend -> return."""
        # Create reader
        reader = self.reader_service.create_reader(
            "Max Mustermann", 
            "Musterstraße 1, 12345 Musterstadt", 
            "0123-456789"
        )
        
        # Create book
        book = self.book_service.create_book(
            book_number="TB001",
            title="Testbuch", 
            author="Test Autor",
            isbn="978-3-16-148410-0",
            publication_year=2024
        )
        
        # Verify initial state
        self.assertEqual(len(self.loan_service.get_active_loans()), 0)
        self.assertTrue(self.loan_service.is_book_available(book.id))
        
        # 1. CHECKOUT
        checkout_date = date.today()
        loan = self.loan_service.check_out_book(reader.id, book.id, checkout_date)
        
        # Verify checkout
        self.assertIsNotNone(loan.id)
        self.assertEqual(loan.reader_id, reader.id)
        self.assertEqual(loan.book_id, book.id)
        self.assertEqual(loan.borrow_date, checkout_date)
        self.assertEqual(loan.due_date, checkout_date + timedelta(days=14))
        self.assertEqual(loan.status, "borrowed")
        self.assertIsNone(loan.return_date)
        
        # Verify side effects
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 1)
        self.assertFalse(self.loan_service.is_book_available(book.id))
        
        # Verify audit log
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 1)
        self.assertEqual(audit_logs[0].action, "checkout")
        
        # 2. EXTEND LOAN
        original_due_date = loan.due_date
        extension_days = 7
        extended_loan = self.loan_service.extend_loan(loan.id, extension_days)
        
        # Verify extension
        self.assertEqual(extended_loan.id, loan.id)
        self.assertEqual(extended_loan.due_date, original_due_date + timedelta(days=extension_days))
        self.assertEqual(extended_loan.status, "borrowed")
        
        # Verify audit log for extension
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 2)
        self.assertEqual(audit_logs[0].action, "extend")
        
        # 3. RETURN BOOK
        return_date = date.today() + timedelta(days=1)
        returned_loan = self.loan_service.return_book(loan.id, return_date)
        
        # Verify return
        self.assertEqual(returned_loan.id, loan.id)
        self.assertEqual(returned_loan.return_date, return_date)
        self.assertEqual(returned_loan.status, "returned")
        
        # Verify side effects
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 0)
        self.assertTrue(self.loan_service.is_book_available(book.id))
        
        # Verify final audit log
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 3)
        self.assertEqual(audit_logs[0].action, "return")
        
        # Verify loan history
        loan_history = self.loan_service.get_loan_history()
        self.assertEqual(len(loan_history), 1)
        self.assertEqual(loan_history[0].status, "returned")
    
    def test_multiple_readers_multiple_books(self):
        """Test multiple readers borrowing multiple books."""
        # Create readers
        reader1 = self.reader_service.create_reader("Reader 1", "Address 1", "Phone 1")
        reader2 = self.reader_service.create_reader("Reader 2", "Address 2", "Phone 2")
        
        # Create books
        book1 = self.book_service.create_book(book_number="B001", title="Book 1")
        book2 = self.book_service.create_book(book_number="B002", title="Book 2")
        book3 = self.book_service.create_book(book_number="B003", title="Book 3")
        
        # Reader 1 borrows Book 1 and Book 2
        loan1 = self.loan_service.check_out_book(reader1.id, book1.id)
        loan2 = self.loan_service.check_out_book(reader1.id, book2.id)
        
        # Reader 2 borrows Book 3
        loan3 = self.loan_service.check_out_book(reader2.id, book3.id)
        
        # Verify active loans
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 3)
        
        # Verify book availability
        self.assertFalse(self.loan_service.is_book_available(book1.id))
        self.assertFalse(self.loan_service.is_book_available(book2.id))
        self.assertFalse(self.loan_service.is_book_available(book3.id))
        
        # Verify reader-specific loans
        reader1_loans = self.loan_service.get_active_loans_by_reader(reader1.id)
        reader2_loans = self.loan_service.get_active_loans_by_reader(reader2.id)
        
        self.assertEqual(len(reader1_loans), 2)
        self.assertEqual(len(reader2_loans), 1)
        
        # Return one book from Reader 1
        self.loan_service.return_book(loan1.id)
        
        # Verify updated state
        active_loans = self.loan_service.get_active_loans()
        self.assertEqual(len(active_loans), 2)
        self.assertTrue(self.loan_service.is_book_available(book1.id))
        
        # Book 1 should be available for new loan
        loan4 = self.loan_service.check_out_book(reader2.id, book1.id)
        self.assertIsNotNone(loan4.id)
    
    def test_overdue_loan_management(self):
        """Test overdue loan detection and management."""
        # Create test data
        reader = self.reader_service.create_reader("Test Reader", "Address", "Phone")
        book = self.book_service.create_book(book_number="TB001", title="Test Book")
        
        # Create loan with past due date
        past_date = date.today() - timedelta(days=20)
        past_due_date = past_date + timedelta(days=14)
        
        # Insert loan directly with past date
        loan_id = self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader.id, book.id, past_date.isoformat(), past_due_date.isoformat(), "borrowed")
        )
        
        # Check overdue loans
        overdue_loans = self.loan_service.get_overdue_loans()
        self.assertEqual(len(overdue_loans), 1)
        self.assertEqual(overdue_loans[0].id, loan_id)
        
        # Extend overdue loan
        extended_loan = self.loan_service.extend_loan(loan_id, 14)
        new_due_date = past_due_date + timedelta(days=14)
        self.assertEqual(extended_loan.due_date, new_due_date)
        
        # Should no longer be overdue
        overdue_loans = self.loan_service.get_overdue_loans()
        self.assertEqual(len(overdue_loans), 0)
        
        # Return the loan
        returned_loan = self.loan_service.return_book(loan_id)
        self.assertEqual(returned_loan.status, "returned")
    
    def test_reader_statistics_integration(self):
        """Test reader statistics across multiple operations."""
        # Create reader and books
        reader = self.reader_service.create_reader("Active Reader", "Address", "Phone")
        book1 = self.book_service.create_book(book_number="B001", title="Book 1")
        book2 = self.book_service.create_book(book_number="B002", title="Book 2")
        
        # Initial stats
        stats = self.loan_service.get_reader_loan_count(reader.id)
        self.assertEqual(stats['total_loans'], 0)
        self.assertEqual(stats['active_loans'], 0)
        self.assertEqual(stats['returned_loans'], 0)
        
        # Borrow first book
        loan1 = self.loan_service.check_out_book(reader.id, book1.id)
        
        stats = self.loan_service.get_reader_loan_count(reader.id)
        self.assertEqual(stats['total_loans'], 1)
        self.assertEqual(stats['active_loans'], 1)
        self.assertEqual(stats['returned_loans'], 0)
        
        # Borrow second book
        loan2 = self.loan_service.check_out_book(reader.id, book2.id)
        
        stats = self.loan_service.get_reader_loan_count(reader.id)
        self.assertEqual(stats['total_loans'], 2)
        self.assertEqual(stats['active_loans'], 2)
        self.assertEqual(stats['returned_loans'], 0)
        
        # Return first book
        self.loan_service.return_book(loan1.id)
        
        stats = self.loan_service.get_reader_loan_count(reader.id)
        self.assertEqual(stats['total_loans'], 2)
        self.assertEqual(stats['active_loans'], 1)
        self.assertEqual(stats['returned_loans'], 1)
        
        # Return second book
        self.loan_service.return_book(loan2.id)
        
        stats = self.loan_service.get_reader_loan_count(reader.id)
        self.assertEqual(stats['total_loans'], 2)
        self.assertEqual(stats['active_loans'], 0)
        self.assertEqual(stats['returned_loans'], 2)
    
    def test_book_history_integration(self):
        """Test book loan history across multiple readers."""
        # Create readers and book
        reader1 = self.reader_service.create_reader("Reader 1", "Address 1", "Phone 1")
        reader2 = self.reader_service.create_reader("Reader 2", "Address 2", "Phone 2")
        book = self.book_service.create_book(book_number="PB001", title="Popular Book")
        
        # Initial history
        history = self.loan_service.get_loans_by_book(book.id)
        self.assertEqual(len(history), 0)
        
        # Reader 1 borrows and returns
        loan1 = self.loan_service.check_out_book(reader1.id, book.id)
        history = self.loan_service.get_loans_by_book(book.id)
        self.assertEqual(len(history), 1)
        
        self.loan_service.return_book(loan1.id)
        
        # Reader 2 borrows
        loan2 = self.loan_service.check_out_book(reader2.id, book.id)
        history = self.loan_service.get_loans_by_book(book.id)
        self.assertEqual(len(history), 2)
        
        # Verify history order (most recent first)
        self.assertEqual(history[0].reader_id, reader2.id)
        self.assertEqual(history[1].reader_id, reader1.id)
        
        # Verify statuses
        self.assertEqual(history[0].status, "borrowed")  # Current loan
        self.assertEqual(history[1].status, "returned")  # Previous loan
    
    def test_error_handling_integration(self):
        """Test error handling in integrated workflows."""
        # Create test data
        reader = self.reader_service.create_reader("Test Reader", "Address", "Phone")
        book = self.book_service.create_book(book_number="TB001", title="Test Book")
        
        # Test borrowing non-existent book
        with self.assertRaises(ValueError):
            self.loan_service.check_out_book(reader.id, 999)
        
        # Test borrowing with non-existent reader
        with self.assertRaises(ValueError):
            self.loan_service.check_out_book(999, book.id)
        
        # Borrow book
        loan = self.loan_service.check_out_book(reader.id, book.id)
        
        # Test borrowing already borrowed book
        with self.assertRaises(ValueError):
            self.loan_service.check_out_book(reader.id, book.id)
        
        # Test returning non-existent loan
        with self.assertRaises(ValueError):
            self.loan_service.return_book(999)
        
        # Test extending non-existent loan
        with self.assertRaises(ValueError):
            self.loan_service.extend_loan(999, 7)
        
        # Return book
        self.loan_service.return_book(loan.id)
        
        # Test returning already returned book
        with self.assertRaises(ValueError):
            self.loan_service.return_book(loan.id)
        
        # Test extending returned loan
        with self.assertRaises(ValueError):
            self.loan_service.extend_loan(loan.id, 7)
    
    def test_audit_trail_completeness(self):
        """Test that audit trail captures all operations."""
        # Create test data
        reader = self.reader_service.create_reader("Test Reader", "Address", "Phone")
        book = self.book_service.create_book(book_number="TB001", title="Test Book")
        
        # Verify no initial audit logs
        initial_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(initial_logs), 0)
        
        # Perform loan operations
        loan = self.loan_service.check_out_book(reader.id, book.id)
        extended_loan = self.loan_service.extend_loan(loan.id, 7)
        returned_loan = self.loan_service.return_book(loan.id)
        
        # Verify audit trail
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 3)
        
        # Verify order (newest first)
        self.assertEqual(audit_logs[0].action, "return")
        self.assertEqual(audit_logs[1].action, "extend")
        self.assertEqual(audit_logs[2].action, "checkout")
        
        # Verify all refer to same loan
        for log in audit_logs:
            self.assertEqual(log.loan_id, loan.id)
            self.assertEqual(log.reader_id, reader.id)
            self.assertEqual(log.book_id, book.id)
        
        # Test audit search functionality
        reader_logs = self.audit_service.get_audit_logs_by_reader(reader.id)
        self.assertEqual(len(reader_logs), 3)
        
        book_logs = self.audit_service.get_audit_logs_by_book(book.id)
        self.assertEqual(len(book_logs), 3)
        
        loan_logs = self.audit_service.get_audit_logs_by_loan(loan.id)
        self.assertEqual(len(loan_logs), 3)
        
        # Test audit statistics
        stats = self.audit_service.get_audit_statistics()
        self.assertEqual(stats['total_entries'], 3)
        self.assertEqual(stats['action_counts']['checkout'], 1)
        self.assertEqual(stats['action_counts']['extend'], 1)
        self.assertEqual(stats['action_counts']['return'], 1)
        self.assertEqual(stats['action_counts']['delete'], 0)

class TestCrossServiceIntegration(unittest.TestCase):
    """Integration tests across multiple services."""
    
    def setUp(self):
        """Set up test database and services before each test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        
        self.audit_service = AuditService(self.db_manager)
        self.loan_service = LoanService(self.db_manager, self.audit_service)
        self.reader_service = ReaderService(self.db_manager)
        self.book_service = BookService(self.db_manager)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_reader_deletion_with_loan_history(self):
        """Test that readers with loan history cannot be deleted."""
        # Create reader and book
        reader = self.reader_service.create_reader("Test Reader", "Address", "Phone")
        book = self.book_service.create_book(book_number="TB001", title="Test Book")
        
        # Reader can be deleted initially
        readers_before = len(self.reader_service.get_all_readers())
        
        # Borrow and return book
        loan = self.loan_service.check_out_book(reader.id, book.id)
        self.loan_service.return_book(loan.id)
        
        # Now reader should not be deletable due to loan history
        with self.assertRaises(ValueError):
            self.reader_service.delete_reader(reader.id)
        
        # Verify reader still exists
        readers_after = len(self.reader_service.get_all_readers())
        self.assertEqual(readers_before, readers_after)
    
    def test_book_deletion_with_loan_history(self):
        """Test that books with loan history cannot be deleted."""
        # Create reader and book
        reader = self.reader_service.create_reader("Test Reader", "Address", "Phone")
        book = self.book_service.create_book(book_number="TB001", title="Test Book")
        
        # Book can be deleted initially
        books_before = len(self.book_service.get_all_books())
        
        # Borrow and return book
        loan = self.loan_service.check_out_book(reader.id, book.id)
        self.loan_service.return_book(loan.id)
        
        # Now book should not be deletable due to loan history
        with self.assertRaises(ValueError):
            self.book_service.delete_book(book.id)
        
        # Verify book still exists
        books_after = len(self.book_service.get_all_books())
        self.assertEqual(books_before, books_after)
    
    def test_search_functionality_integration(self):
        """Test search functionality across all services."""
        # Create test data
        reader = self.reader_service.create_reader("John Doe", "123 Main St", "555-0123")
        book = self.book_service.create_book(book_number="PY001", title="Python Programming", author="Jane Smith")
        
        # Create loan
        loan = self.loan_service.check_out_book(reader.id, book.id)
        
        # Test reader search
        reader_results = self.reader_service.search_readers_by_name("John")
        self.assertEqual(len(reader_results), 1)
        self.assertEqual(reader_results[0].name, "John Doe")
        
        # Test book search
        book_results = self.book_service.search_books_by_title("Python")
        self.assertEqual(len(book_results), 1)
        self.assertEqual(book_results[0].title, "Python Programming")
        
        author_results = self.book_service.search_books_by_author("Jane")
        self.assertEqual(len(author_results), 1)
        
        # Test loan search
        loan_by_reader = self.loan_service.search_loans_by_reader_name("John")
        self.assertEqual(len(loan_by_reader), 1)
        
        loan_by_book = self.loan_service.search_loans_by_book_title("Python")
        self.assertEqual(len(loan_by_book), 1)
        
        # Test audit search
        audit_results = self.audit_service.search_audit_logs("Python")
        self.assertEqual(len(audit_results), 1)
        self.assertEqual(audit_results[0].action, "checkout")

if __name__ == '__main__':
    unittest.main()