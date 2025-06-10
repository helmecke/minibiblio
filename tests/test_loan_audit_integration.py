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
from business.audit_service import AuditService
from database.models import Loan

class TestLoanAuditIntegration(unittest.TestCase):
    """Integration tests for loan service with audit logging."""
    
    def setUp(self):
        """Set up test database and services before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        
        # Create services
        self.audit_service = AuditService(self.db_manager)
        self.loan_service = LoanService(self.db_manager, self.audit_service)
        
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
        
        # Get IDs
        self.reader1_id = 1
        self.reader2_id = 2
        self.book1_id = 1
        self.book2_id = 2
    
    def test_checkout_creates_audit_log(self):
        """Test that checkout creates audit log entry."""
        # Verify no initial audit logs
        initial_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(initial_logs), 0)
        
        # Checkout book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Verify audit log was created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 1)
        
        audit_log = audit_logs[0]
        self.assertEqual(audit_log.action, "checkout")
        self.assertEqual(audit_log.loan_id, loan.id)
        self.assertEqual(audit_log.reader_id, self.reader1_id)
        self.assertEqual(audit_log.book_id, self.book1_id)
        self.assertIn("ausgeliehen", audit_log.description)
        self.assertIn("Test Reader 1", audit_log.description)
        self.assertIn("Test Book 1", audit_log.description)
        
        # Verify new values contain checkout info
        new_values = audit_log.get_new_values_dict()
        self.assertEqual(new_values['status'], 'borrowed')
        self.assertIsNotNone(new_values['borrow_date'])
        self.assertIsNotNone(new_values['due_date'])
    
    def test_return_creates_audit_log(self):
        """Test that return creates audit log entry."""
        # Checkout book first
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Clear audit logs to focus on return
        initial_audit_count = len(self.audit_service.get_audit_logs())
        
        # Return book
        return_date = date.today() + timedelta(days=1)
        returned_loan = self.loan_service.return_book(loan.id, return_date)
        
        # Verify new audit log was created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), initial_audit_count + 1)
        
        # Find the return audit log (should be first due to ordering)
        return_log = audit_logs[0]
        self.assertEqual(return_log.action, "return")
        self.assertEqual(return_log.loan_id, loan.id)
        self.assertIn("zurückgegeben", return_log.description)
        
        # Verify old and new values
        old_values = return_log.get_old_values_dict()
        new_values = return_log.get_new_values_dict()
        self.assertEqual(old_values['status'], 'borrowed')
        self.assertEqual(new_values['status'], 'returned')
        self.assertIsNotNone(new_values['return_date'])
    
    def test_extend_creates_audit_log(self):
        """Test that loan extension creates audit log entry."""
        # Checkout book first
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        original_due_date = loan.due_date
        
        initial_audit_count = len(self.audit_service.get_audit_logs())
        
        # Extend loan
        extension_days = 14
        extended_loan = self.loan_service.extend_loan(loan.id, extension_days)
        
        # Verify new audit log was created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), initial_audit_count + 1)
        
        # Find the extension audit log
        extend_log = audit_logs[0]
        self.assertEqual(extend_log.action, "extend")
        self.assertEqual(extend_log.loan_id, loan.id)
        self.assertIn("verlängert", extend_log.description)
        self.assertIn(str(extension_days), extend_log.description)
        
        # Verify old and new values
        old_values = extend_log.get_old_values_dict()
        new_values = extend_log.get_new_values_dict()
        self.assertEqual(old_values['due_date'], original_due_date.isoformat())
        self.assertEqual(new_values['due_date'], extended_loan.due_date.isoformat())
        self.assertEqual(new_values['extension_days'], extension_days)
    
    def test_delete_creates_audit_log(self):
        """Test that loan deletion creates audit log entry."""
        # Checkout and return book first
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        self.loan_service.return_book(loan.id)
        
        initial_audit_count = len(self.audit_service.get_audit_logs())
        
        # Delete loan
        delete_result = self.loan_service.delete_loan(loan.id)
        self.assertTrue(delete_result)
        
        # Verify new audit log was created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), initial_audit_count + 1)
        
        # Find the deletion audit log
        delete_log = audit_logs[0]
        self.assertEqual(delete_log.action, "delete")
        self.assertEqual(delete_log.loan_id, loan.id)
        self.assertIn("gelöscht", delete_log.description)
        
        # Verify old values contain loan state before deletion
        old_values = delete_log.get_old_values_dict()
        self.assertEqual(old_values['status'], 'returned')
        self.assertIsNotNone(old_values['borrow_date'])
        self.assertIsNotNone(old_values['due_date'])
        self.assertIsNotNone(old_values['return_date'])
    
    def test_loan_service_without_audit_service(self):
        """Test that loan service works without audit service."""
        # Create loan service without audit service
        loan_service_no_audit = LoanService(self.db_manager)
        
        # All operations should work normally
        loan = loan_service_no_audit.check_out_book(self.reader1_id, self.book1_id)
        self.assertIsNotNone(loan.id)
        
        extended_loan = loan_service_no_audit.extend_loan(loan.id, 7)
        self.assertIsNotNone(extended_loan.due_date)
        
        returned_loan = loan_service_no_audit.return_book(loan.id)
        self.assertEqual(returned_loan.status, "returned")
        
        delete_result = loan_service_no_audit.delete_loan(loan.id)
        self.assertTrue(delete_result)
        
        # No audit logs should be created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 0)
    
    def test_audit_failure_does_not_break_operations(self):
        """Test that audit logging failures don't break loan operations."""
        # Create a loan service with a deliberately broken audit service
        # (This simulates audit service failures)
        
        class BrokenAuditService:
            def log_checkout(self, *args, **kwargs):
                raise Exception("Audit service failed")
            
            def log_return(self, *args, **kwargs):
                raise Exception("Audit service failed")
            
            def log_extension(self, *args, **kwargs):
                raise Exception("Audit service failed")
            
            def log_deletion(self, *args, **kwargs):
                raise Exception("Audit service failed")
        
        broken_audit_service = BrokenAuditService()
        loan_service_broken_audit = LoanService(self.db_manager, broken_audit_service)
        
        # All operations should still work despite audit failures
        loan = loan_service_broken_audit.check_out_book(self.reader1_id, self.book1_id)
        self.assertIsNotNone(loan.id)
        
        extended_loan = loan_service_broken_audit.extend_loan(loan.id, 7)
        self.assertIsNotNone(extended_loan.due_date)
        
        returned_loan = loan_service_broken_audit.return_book(loan.id)
        self.assertEqual(returned_loan.status, "returned")
        
        delete_result = loan_service_broken_audit.delete_loan(loan.id)
        self.assertTrue(delete_result)
    
    def test_complete_audit_trail(self):
        """Test complete audit trail for loan lifecycle."""
        # Perform complete loan lifecycle
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        extended_loan = self.loan_service.extend_loan(loan.id, 7)
        returned_loan = self.loan_service.return_book(loan.id)
        
        # Verify complete audit trail
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), 3)
        
        # Verify order (newest first)
        self.assertEqual(audit_logs[0].action, "return")
        self.assertEqual(audit_logs[1].action, "extend")
        self.assertEqual(audit_logs[2].action, "checkout")
        
        # Verify all logs refer to same loan
        for log in audit_logs:
            self.assertEqual(log.loan_id, loan.id)
            self.assertEqual(log.reader_id, self.reader1_id)
            self.assertEqual(log.book_id, self.book1_id)
            self.assertIsNotNone(log.timestamp)
            self.assertEqual(log.user_info, "System")  # Default user
    
    def test_audit_with_custom_user_info(self):
        """Test audit logging with custom user information."""
        # We'll test this by directly calling audit methods with custom user info
        # since the current loan service doesn't expose user_info parameter
        
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        # Test direct audit service calls with custom user
        custom_loan = Loan(
            id=loan.id,
            reader_id=self.reader1_id,
            book_id=self.book1_id,
            borrow_date=loan.borrow_date,
            due_date=loan.due_date,
            status="borrowed",
            reader_name="Test Reader 1",
            book_title="Test Book 1",
            book_number="B001"
        )
        
        # Log custom extension
        self.audit_service.log_extension(custom_loan, loan.due_date, 7, "Librarian John")
        
        # Verify custom user info
        audit_logs = self.audit_service.get_audit_logs()
        extension_log = next(log for log in audit_logs if log.action == "extend")
        self.assertEqual(extension_log.user_info, "Librarian John")
    
    def test_audit_search_and_filtering(self):
        """Test audit log search and filtering functionality."""
        # Create multiple loans and operations
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        self.loan_service.extend_loan(loan1.id, 7)
        self.loan_service.return_book(loan2.id)
        
        # Test filtering by action
        checkout_logs = self.audit_service.get_audit_logs_by_action("checkout")
        self.assertEqual(len(checkout_logs), 2)
        
        extend_logs = self.audit_service.get_audit_logs_by_action("extend")
        self.assertEqual(len(extend_logs), 1)
        
        return_logs = self.audit_service.get_audit_logs_by_action("return")
        self.assertEqual(len(return_logs), 1)
        
        # Test filtering by loan
        loan1_logs = self.audit_service.get_audit_logs_by_loan(loan1.id)
        self.assertEqual(len(loan1_logs), 2)  # checkout + extend
        
        loan2_logs = self.audit_service.get_audit_logs_by_loan(loan2.id)
        self.assertEqual(len(loan2_logs), 2)  # checkout + return
        
        # Test filtering by reader
        reader1_logs = self.audit_service.get_audit_logs_by_reader(self.reader1_id)
        self.assertEqual(len(reader1_logs), 2)  # checkout + extend
        
        reader2_logs = self.audit_service.get_audit_logs_by_reader(self.reader2_id)
        self.assertEqual(len(reader2_logs), 2)  # checkout + return
        
        # Test filtering by book
        book1_logs = self.audit_service.get_audit_logs_by_book(self.book1_id)
        self.assertEqual(len(book1_logs), 2)  # checkout + extend
        
        book2_logs = self.audit_service.get_audit_logs_by_book(self.book2_id)
        self.assertEqual(len(book2_logs), 2)  # checkout + return
        
        # Test search functionality
        reader1_search = self.audit_service.search_audit_logs("Test Reader 1")
        self.assertEqual(len(reader1_search), 2)
        
        book1_search = self.audit_service.search_audit_logs("Test Book 1")
        self.assertEqual(len(book1_search), 2)
        
        extend_search = self.audit_service.search_audit_logs("verlängert")
        self.assertEqual(len(extend_search), 1)
    
    def test_audit_statistics_integration(self):
        """Test audit statistics with loan operations."""
        # Perform various operations
        loan1 = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        loan2 = self.loan_service.check_out_book(self.reader2_id, self.book2_id)
        
        self.loan_service.extend_loan(loan1.id, 7)
        self.loan_service.extend_loan(loan2.id, 14)
        
        self.loan_service.return_book(loan1.id)
        
        # Get statistics
        stats = self.audit_service.get_audit_statistics()
        
        # Verify counts
        self.assertEqual(stats['total_entries'], 5)
        self.assertEqual(stats['action_counts']['checkout'], 2)
        self.assertEqual(stats['action_counts']['extend'], 2)
        self.assertEqual(stats['action_counts']['return'], 1)
        self.assertEqual(stats['action_counts']['delete'], 0)
        
        # Should have recent activity
        self.assertGreater(stats['recent_activity_7_days'], 0)
        
        # Should have most active day
        self.assertIsNotNone(stats.get('most_active_day_30_days'))
    
    def test_return_by_book_id_audit_integration(self):
        """Test audit logging for return by book ID."""
        # Checkout book
        loan = self.loan_service.check_out_book(self.reader1_id, self.book1_id)
        
        initial_audit_count = len(self.audit_service.get_audit_logs())
        
        # Return by book ID
        returned_loan = self.loan_service.return_book_by_book_id(self.book1_id)
        
        # Verify audit log was created
        audit_logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(audit_logs), initial_audit_count + 1)
        
        return_log = audit_logs[0]
        self.assertEqual(return_log.action, "return")
        self.assertEqual(return_log.loan_id, loan.id)
        self.assertEqual(return_log.book_id, self.book1_id)

if __name__ == '__main__':
    unittest.main()