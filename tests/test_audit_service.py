import unittest
import tempfile
import os
from datetime import date, datetime, timedelta
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.db_manager import DatabaseManager
from business.audit_service import AuditService
from database.models import AuditLog, Loan

class TestAuditLogModel(unittest.TestCase):
    """Unit tests for AuditLog model."""
    
    def test_audit_log_creation_success(self):
        """Test successful audit log creation."""
        audit = AuditLog(
            loan_id=1,
            reader_id=1,
            book_id=1,
            action="checkout",
            description="Test checkout",
            user_info="Test User"
        )
        
        self.assertEqual(audit.loan_id, 1)
        self.assertEqual(audit.reader_id, 1)
        self.assertEqual(audit.book_id, 1)
        self.assertEqual(audit.action, "checkout")
        self.assertEqual(audit.description, "Test checkout")
        self.assertEqual(audit.user_info, "Test User")
    
    def test_audit_log_validation_errors(self):
        """Test audit log validation errors."""
        # Missing action
        with self.assertRaises(ValueError) as context:
            AuditLog(description="Test")
        self.assertIn("Action is required", str(context.exception))
        
        # Invalid action
        with self.assertRaises(ValueError) as context:
            AuditLog(action="invalid", description="Test")
        self.assertIn("Action must be one of", str(context.exception))
        
        # Missing description
        with self.assertRaises(ValueError) as context:
            AuditLog(action="checkout", description="")
        self.assertIn("Description is required", str(context.exception))
    
    def test_audit_log_from_db_row(self):
        """Test creating audit log from database row."""
        # Mock database row
        class MockRow:
            def __init__(self, data):
                self.data = data
            
            def __getitem__(self, key):
                return self.data[key]
        
        row_data = {
            'id': 1,
            'loan_id': 2,
            'reader_id': 3,
            'book_id': 4,
            'action': 'checkout',
            'description': 'Test description',
            'old_values': '{"status": "available"}',
            'new_values': '{"status": "borrowed"}',
            'user_info': 'Test User',
            'timestamp': '2024-01-15 12:00:00',
            'reader_name': 'Test Reader',
            'book_title': 'Test Book',
            'book_number': 'B001'
        }
        
        row = MockRow(row_data)
        audit = AuditLog.from_db_row(row)
        
        self.assertEqual(audit.id, 1)
        self.assertEqual(audit.loan_id, 2)
        self.assertEqual(audit.reader_id, 3)
        self.assertEqual(audit.book_id, 4)
        self.assertEqual(audit.action, 'checkout')
        self.assertEqual(audit.description, 'Test description')
        self.assertEqual(audit.old_values, '{"status": "available"}')
        self.assertEqual(audit.new_values, '{"status": "borrowed"}')
        self.assertEqual(audit.user_info, 'Test User')
        self.assertEqual(audit.reader_name, 'Test Reader')
        self.assertEqual(audit.book_title, 'Test Book')
        self.assertEqual(audit.book_number, 'B001')
    
    def test_audit_log_to_dict(self):
        """Test converting audit log to dictionary."""
        audit = AuditLog(
            loan_id=1,
            reader_id=2,
            book_id=3,
            action="return",
            description="Test return",
            old_values='{"status": "borrowed"}',
            new_values='{"status": "returned"}',
            user_info="Admin"
        )
        
        result = audit.to_dict()
        expected = {
            'loan_id': 1,
            'reader_id': 2,
            'book_id': 3,
            'action': 'return',
            'description': 'Test return',
            'old_values': '{"status": "borrowed"}',
            'new_values': '{"status": "returned"}',
            'user_info': 'Admin'
        }
        
        self.assertEqual(result, expected)
    
    def test_audit_log_json_helpers(self):
        """Test JSON helper methods."""
        audit = AuditLog(
            action="extend",
            description="Test extend"
        )
        
        # Test setting and getting old values
        old_values = {"due_date": "2024-01-15", "status": "borrowed"}
        audit.set_old_values_dict(old_values)
        self.assertEqual(audit.get_old_values_dict(), old_values)
        
        # Test setting and getting new values
        new_values = {"due_date": "2024-01-29", "status": "borrowed"}
        audit.set_new_values_dict(new_values)
        self.assertEqual(audit.get_new_values_dict(), new_values)
        
        # Test with None values
        audit.set_old_values_dict(None)
        self.assertEqual(audit.get_old_values_dict(), {})
        
        # Test with empty dict
        audit.set_new_values_dict({})
        self.assertIsNone(audit.new_values)
    
    def test_audit_log_json_error_handling(self):
        """Test JSON error handling."""
        audit = AuditLog(
            action="checkout",
            description="Test",
            old_values="invalid json",
            new_values="also invalid"
        )
        
        # Should return empty dict for invalid JSON
        self.assertEqual(audit.get_old_values_dict(), {})
        self.assertEqual(audit.get_new_values_dict(), {})

class TestAuditService(unittest.TestCase):
    """Unit tests for AuditService class."""
    
    def setUp(self):
        """Set up test database and service before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.audit_service = AuditService(self.db_manager)
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_data(self):
        """Create test readers, books, and loans."""
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
        
        # Create test loans
        today = date.today()
        due_date = today + timedelta(days=14)
        
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (1, 1, today.isoformat(), due_date.isoformat(), "borrowed")
        )
        self.loan_id = 1
        
        # Get reader and book IDs
        self.reader1_id = 1
        self.reader2_id = 2
        self.book1_id = 1
        self.book2_id = 2
    
    def _create_test_loan(self):
        """Create a test loan object."""
        return Loan(
            id=self.loan_id,
            reader_id=self.reader1_id,
            book_id=self.book1_id,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status="borrowed",
            reader_name="Test Reader 1",
            book_title="Test Book 1",
            book_number="B001"
        )
    
    def test_log_loan_activity_success(self):
        """Test successful loan activity logging."""
        loan = self._create_test_loan()
        
        old_values = {"status": "available"}
        new_values = {"status": "borrowed"}
        
        audit_entry = self.audit_service.log_loan_activity(
            action="checkout",
            loan=loan,
            description="Test checkout",
            old_values=old_values,
            new_values=new_values,
            user_info="Test User"
        )
        
        self.assertIsNotNone(audit_entry.id)
        self.assertEqual(audit_entry.action, "checkout")
        self.assertEqual(audit_entry.description, "Test checkout")
        self.assertEqual(audit_entry.loan_id, loan.id)
        self.assertEqual(audit_entry.reader_id, loan.reader_id)
        self.assertEqual(audit_entry.book_id, loan.book_id)
        self.assertEqual(audit_entry.user_info, "Test User")
        
        # Check JSON values
        self.assertEqual(audit_entry.get_old_values_dict(), old_values)
        self.assertEqual(audit_entry.get_new_values_dict(), new_values)
    
    def test_log_checkout(self):
        """Test logging checkout activity."""
        loan = self._create_test_loan()
        
        audit_entry = self.audit_service.log_checkout(loan, "Librarian")
        
        self.assertEqual(audit_entry.action, "checkout")
        self.assertIn("ausgeliehen", audit_entry.description)
        self.assertIn(loan.book_title, audit_entry.description)
        self.assertIn(loan.reader_name, audit_entry.description)
        self.assertEqual(audit_entry.user_info, "Librarian")
        
        new_values = audit_entry.get_new_values_dict()
        self.assertEqual(new_values['status'], 'borrowed')
        self.assertIsNotNone(new_values['borrow_date'])
        self.assertIsNotNone(new_values['due_date'])
    
    def test_log_return(self):
        """Test logging return activity."""
        loan = self._create_test_loan()
        loan.status = "returned"
        loan.return_date = date.today()
        
        old_loan = self._create_test_loan()
        
        audit_entry = self.audit_service.log_return(loan, old_loan, "Librarian")
        
        self.assertEqual(audit_entry.action, "return")
        self.assertIn("zurückgegeben", audit_entry.description)
        self.assertIn(loan.book_title, audit_entry.description)
        self.assertIn(loan.reader_name, audit_entry.description)
        
        old_values = audit_entry.get_old_values_dict()
        new_values = audit_entry.get_new_values_dict()
        self.assertEqual(old_values['status'], 'borrowed')
        self.assertEqual(new_values['status'], 'returned')
    
    def test_log_extension(self):
        """Test logging extension activity."""
        loan = self._create_test_loan()
        old_due_date = date.today() + timedelta(days=14)
        loan.due_date = old_due_date + timedelta(days=7)
        extension_days = 7
        
        audit_entry = self.audit_service.log_extension(loan, old_due_date, extension_days, "Librarian")
        
        self.assertEqual(audit_entry.action, "extend")
        self.assertIn("verlängert", audit_entry.description)
        self.assertIn(str(extension_days), audit_entry.description)
        
        old_values = audit_entry.get_old_values_dict()
        new_values = audit_entry.get_new_values_dict()
        self.assertEqual(old_values['due_date'], old_due_date.isoformat())
        self.assertEqual(new_values['due_date'], loan.due_date.isoformat())
        self.assertEqual(new_values['extension_days'], extension_days)
    
    def test_log_deletion(self):
        """Test logging deletion activity."""
        loan = self._create_test_loan()
        
        audit_entry = self.audit_service.log_deletion(loan, "Admin")
        
        self.assertEqual(audit_entry.action, "delete")
        self.assertIn("gelöscht", audit_entry.description)
        self.assertEqual(audit_entry.user_info, "Admin")
        
        old_values = audit_entry.get_old_values_dict()
        self.assertEqual(old_values['status'], 'borrowed')
        self.assertIsNotNone(old_values['borrow_date'])
        self.assertIsNotNone(old_values['due_date'])
    
    def test_get_audit_logs(self):
        """Test getting audit logs."""
        # Create some audit entries
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        self.audit_service.log_extension(loan, loan.due_date, 7)
        self.audit_service.log_return(loan)
        
        # Get all logs
        logs = self.audit_service.get_audit_logs()
        self.assertEqual(len(logs), 3)
        
        # Check ordering (newest first)
        self.assertEqual(logs[0].action, "return")
        self.assertEqual(logs[1].action, "extend")
        self.assertEqual(logs[2].action, "checkout")
        
        # Test with limit
        limited_logs = self.audit_service.get_audit_logs(limit=2)
        self.assertEqual(len(limited_logs), 2)
        
        # Test with offset
        offset_logs = self.audit_service.get_audit_logs(limit=2, offset=1)
        self.assertEqual(len(offset_logs), 2)
        self.assertEqual(offset_logs[0].action, "extend")
    
    def test_get_audit_logs_by_loan(self):
        """Test getting audit logs for specific loan."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        self.audit_service.log_extension(loan, loan.due_date, 7)
        
        logs = self.audit_service.get_audit_logs_by_loan(self.loan_id)
        self.assertEqual(len(logs), 2)
        
        for log in logs:
            self.assertEqual(log.loan_id, self.loan_id)
    
    def test_get_audit_logs_by_reader(self):
        """Test getting audit logs for specific reader."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        
        logs = self.audit_service.get_audit_logs_by_reader(self.reader1_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].reader_id, self.reader1_id)
    
    def test_get_audit_logs_by_book(self):
        """Test getting audit logs for specific book."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        
        logs = self.audit_service.get_audit_logs_by_book(self.book1_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].book_id, self.book1_id)
    
    def test_get_audit_logs_by_action(self):
        """Test getting audit logs by action type."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        self.audit_service.log_extension(loan, loan.due_date, 7)
        
        checkout_logs = self.audit_service.get_audit_logs_by_action("checkout")
        extend_logs = self.audit_service.get_audit_logs_by_action("extend")
        
        self.assertEqual(len(checkout_logs), 1)
        self.assertEqual(len(extend_logs), 1)
        self.assertEqual(checkout_logs[0].action, "checkout")
        self.assertEqual(extend_logs[0].action, "extend")
    
    def test_get_audit_logs_by_date_range(self):
        """Test getting audit logs by date range."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Logs within range
        logs_today = self.audit_service.get_audit_logs_by_date_range(today, today)
        self.assertEqual(len(logs_today), 1)
        
        # Logs outside range
        logs_yesterday = self.audit_service.get_audit_logs_by_date_range(yesterday, yesterday)
        self.assertEqual(len(logs_yesterday), 0)
        
        # Wide range
        logs_wide = self.audit_service.get_audit_logs_by_date_range(yesterday, tomorrow)
        self.assertEqual(len(logs_wide), 1)
    
    def test_search_audit_logs(self):
        """Test searching audit logs."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        
        # Search by reader name
        reader_logs = self.audit_service.search_audit_logs("Test Reader 1")
        self.assertEqual(len(reader_logs), 1)
        
        # Search by book title
        book_logs = self.audit_service.search_audit_logs("Test Book 1")
        self.assertEqual(len(book_logs), 1)
        
        # Search by description
        desc_logs = self.audit_service.search_audit_logs("ausgeliehen")
        self.assertEqual(len(desc_logs), 1)
        
        # Search with no results
        no_logs = self.audit_service.search_audit_logs("NonExistent")
        self.assertEqual(len(no_logs), 0)
        
        # Empty search
        empty_logs = self.audit_service.search_audit_logs("")
        self.assertEqual(len(empty_logs), 0)
    
    def test_get_audit_statistics(self):
        """Test getting audit statistics."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        self.audit_service.log_extension(loan, loan.due_date, 7)
        self.audit_service.log_return(loan)
        
        stats = self.audit_service.get_audit_statistics()
        
        self.assertEqual(stats['total_entries'], 3)
        self.assertEqual(stats['action_counts']['checkout'], 1)
        self.assertEqual(stats['action_counts']['extend'], 1)
        self.assertEqual(stats['action_counts']['return'], 1)
        self.assertEqual(stats['action_counts']['delete'], 0)
        self.assertIsInstance(stats['recent_activity_7_days'], int)
        
        # Should have most active day since we have entries today
        self.assertIsNotNone(stats.get('most_active_day_30_days'))
    
    def test_cleanup_old_logs(self):
        """Test cleaning up old audit logs."""
        loan = self._create_test_loan()
        self.audit_service.log_checkout(loan)
        
        # Should not delete recent logs
        deleted_count = self.audit_service.cleanup_old_logs(days_to_keep=1)
        self.assertEqual(deleted_count, 0)
        
        logs_after = self.audit_service.get_audit_logs()
        self.assertEqual(len(logs_after), 1)
        
        # Test with very short retention (would delete everything)
        # Note: This test depends on timing, so we just verify the method runs
        deleted_count = self.audit_service.cleanup_old_logs(days_to_keep=0)
        self.assertIsInstance(deleted_count, int)

if __name__ == '__main__':
    unittest.main()