import unittest
import tempfile
import os
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.db_manager import DatabaseManager
from business.reader_service import ReaderService
from database.models import Reader

class TestReaderService(unittest.TestCase):
    """Unit tests for ReaderService class."""
    
    def setUp(self):
        """Set up test database and service before each test."""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.reader_service = ReaderService(self.db_manager)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_reader_success(self):
        """Test successful reader creation."""
        # Test data
        name = "Max Mustermann"
        address = "Musterstraße 1\n12345 Musterstadt"
        phone = "0123-456789"
        
        # Create reader
        reader = self.reader_service.create_reader(name, address, phone)
        
        # Assertions
        self.assertIsNotNone(reader.id)
        self.assertEqual(reader.reader_number, 1)  # First reader should get number 1
        self.assertEqual(reader.name, name)
        self.assertEqual(reader.address, address)
        self.assertEqual(reader.phone, phone)
        self.assertIsNotNone(reader.created_date)
    
    def test_create_reader_sequential_numbers(self):
        """Test that reader numbers are assigned sequentially."""
        # Create multiple readers
        reader1 = self.reader_service.create_reader("Reader 1", "Address 1", "Phone 1")
        reader2 = self.reader_service.create_reader("Reader 2", "Address 2", "Phone 2")
        reader3 = self.reader_service.create_reader("Reader 3", "Address 3", "Phone 3")
        
        # Check sequential numbering
        self.assertEqual(reader1.reader_number, 1)
        self.assertEqual(reader2.reader_number, 2)
        self.assertEqual(reader3.reader_number, 3)
    
    def test_create_reader_validation_errors(self):
        """Test validation errors during reader creation."""
        # Test empty name
        with self.assertRaises(ValueError):
            self.reader_service.create_reader("", "Address", "Phone")
        
        # Test empty address
        with self.assertRaises(ValueError):
            self.reader_service.create_reader("Name", "", "Phone")
        
        # Test empty phone
        with self.assertRaises(ValueError):
            self.reader_service.create_reader("Name", "Address", "")
        
        # Test whitespace-only fields
        with self.assertRaises(ValueError):
            self.reader_service.create_reader("   ", "Address", "Phone")
    
    def test_get_reader_by_id(self):
        """Test retrieving reader by ID."""
        # Create a reader
        created_reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Retrieve by ID
        retrieved_reader = self.reader_service.get_reader_by_id(created_reader.id)
        
        # Assertions
        self.assertIsNotNone(retrieved_reader)
        self.assertEqual(retrieved_reader.id, created_reader.id)
        self.assertEqual(retrieved_reader.name, created_reader.name)
        self.assertEqual(retrieved_reader.address, created_reader.address)
        self.assertEqual(retrieved_reader.phone, created_reader.phone)
    
    def test_get_reader_by_id_not_found(self):
        """Test retrieving non-existent reader by ID."""
        result = self.reader_service.get_reader_by_id(999)
        self.assertIsNone(result)
    
    def test_get_reader_by_number(self):
        """Test retrieving reader by reader number."""
        # Create a reader
        created_reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Retrieve by reader number
        retrieved_reader = self.reader_service.get_reader_by_number(created_reader.reader_number)
        
        # Assertions
        self.assertIsNotNone(retrieved_reader)
        self.assertEqual(retrieved_reader.reader_number, created_reader.reader_number)
        self.assertEqual(retrieved_reader.name, created_reader.name)
    
    def test_get_reader_by_number_not_found(self):
        """Test retrieving non-existent reader by number."""
        result = self.reader_service.get_reader_by_number(999)
        self.assertIsNone(result)
    
    def test_get_all_readers(self):
        """Test retrieving all readers."""
        # Initially should be empty
        readers = self.reader_service.get_all_readers()
        self.assertEqual(len(readers), 0)
        
        # Create some readers
        reader1 = self.reader_service.create_reader("Reader 1", "Address 1", "Phone 1")
        reader2 = self.reader_service.create_reader("Reader 2", "Address 2", "Phone 2")
        reader3 = self.reader_service.create_reader("Reader 3", "Address 3", "Phone 3")
        
        # Retrieve all
        readers = self.reader_service.get_all_readers()
        
        # Assertions
        self.assertEqual(len(readers), 3)
        # Should be ordered by reader number
        self.assertEqual(readers[0].reader_number, 1)
        self.assertEqual(readers[1].reader_number, 2)
        self.assertEqual(readers[2].reader_number, 3)
    
    def test_search_readers_by_name(self):
        """Test searching readers by name."""
        # Create test readers
        self.reader_service.create_reader("Max Mustermann", "Address 1", "Phone 1")
        self.reader_service.create_reader("Anna Schmidt", "Address 2", "Phone 2")
        self.reader_service.create_reader("Hans Müller", "Address 3", "Phone 3")
        self.reader_service.create_reader("Maximilian Weber", "Address 4", "Phone 4")
        
        # Test exact match
        results = self.reader_service.search_readers_by_name("Max Mustermann")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Max Mustermann")
        
        # Test partial match
        results = self.reader_service.search_readers_by_name("Max")
        self.assertEqual(len(results), 2)  # Max Mustermann and Maximilian Weber
        
        # Test case insensitive
        results = self.reader_service.search_readers_by_name("anna")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Anna Schmidt")
        
        # Test no matches
        results = self.reader_service.search_readers_by_name("xyz")
        self.assertEqual(len(results), 0)
        
        # Test empty query
        results = self.reader_service.search_readers_by_name("")
        self.assertEqual(len(results), 0)
    
    def test_update_reader_success(self):
        """Test successful reader update."""
        # Create a reader
        reader = self.reader_service.create_reader("Original Name", "Original Address", "Original Phone")
        
        # Update reader
        updated_reader = self.reader_service.update_reader(
            reader.id, 
            name="Updated Name",
            address="Updated Address",
            phone="Updated Phone"
        )
        
        # Assertions
        self.assertIsNotNone(updated_reader)
        self.assertEqual(updated_reader.id, reader.id)
        self.assertEqual(updated_reader.reader_number, reader.reader_number)  # Should not change
        self.assertEqual(updated_reader.name, "Updated Name")
        self.assertEqual(updated_reader.address, "Updated Address")
        self.assertEqual(updated_reader.phone, "Updated Phone")
    
    def test_update_reader_partial(self):
        """Test partial reader update."""
        # Create a reader
        reader = self.reader_service.create_reader("Original Name", "Original Address", "Original Phone")
        
        # Update only name
        updated_reader = self.reader_service.update_reader(reader.id, name="New Name")
        
        # Assertions
        self.assertEqual(updated_reader.name, "New Name")
        self.assertEqual(updated_reader.address, "Original Address")  # Should remain unchanged
        self.assertEqual(updated_reader.phone, "Original Phone")  # Should remain unchanged
    
    def test_update_reader_not_found(self):
        """Test updating non-existent reader."""
        result = self.reader_service.update_reader(999, name="New Name")
        self.assertIsNone(result)
    
    def test_update_reader_validation_error(self):
        """Test validation error during reader update."""
        # Create a reader
        reader = self.reader_service.create_reader("Original Name", "Original Address", "Original Phone")
        
        # Try to update with empty name
        with self.assertRaises(ValueError):
            self.reader_service.update_reader(reader.id, name="")
    
    def test_delete_reader_success(self):
        """Test successful reader deletion."""
        # Create a reader
        reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Delete reader
        result = self.reader_service.delete_reader(reader.id)
        self.assertTrue(result)
        
        # Verify deletion
        deleted_reader = self.reader_service.get_reader_by_id(reader.id)
        self.assertIsNone(deleted_reader)
    
    def test_delete_reader_not_found(self):
        """Test deleting non-existent reader."""
        result = self.reader_service.delete_reader(999)
        self.assertFalse(result)
    
    def test_delete_reader_with_active_loans(self):
        """Test that reader with active loans cannot be deleted."""
        # Create a reader
        reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Create a fake active loan (insert directly into database)
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title) VALUES (?, ?)",
            ("B001", "Test Book")
        )
        book_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B001",))[0]['id']
        
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader.id, book_id, "2024-01-01", "2024-01-15", "borrowed")
        )
        
        # Try to delete reader with active loan
        with self.assertRaises(ValueError) as context:
            self.reader_service.delete_reader(reader.id)
        
        self.assertIn("loan history", str(context.exception))
    
    def test_get_reader_with_loans(self):
        """Test getting reader information with loan history."""
        # Create a reader
        reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Create books and loans
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title, author) VALUES (?, ?, ?)",
            ("B001", "Book 1", "Author 1")
        )
        self.db_manager.execute_command(
            "INSERT INTO books (book_number, title, author) VALUES (?, ?, ?)",
            ("B002", "Book 2", "Author 2")
        )
        
        book1_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B001",))[0]['id']
        book2_id = self.db_manager.execute_query("SELECT id FROM books WHERE book_number = ?", ("B002",))[0]['id']
        
        # Create loans
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, return_date, status) VALUES (?, ?, ?, ?, ?, ?)",
            (reader.id, book1_id, "2024-01-01", "2024-01-15", "2024-01-15", "returned")
        )
        self.db_manager.execute_command(
            "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (reader.id, book2_id, "2024-02-01", "2024-02-15", "borrowed")
        )
        
        # Get reader with loans
        result = self.reader_service.get_reader_with_loans(reader.id)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['reader'].id, reader.id)
        self.assertEqual(len(result['loans']), 2)
        self.assertEqual(result['active_loans_count'], 1)
        self.assertEqual(result['total_loans_count'], 2)
        
        # Check loan details
        loans = result['loans']
        self.assertEqual(loans[0]['book_title'], "Book 2")  # Should be ordered by borrow_date DESC
        self.assertEqual(loans[0]['status'], "borrowed")
        self.assertEqual(loans[1]['book_title'], "Book 1")
        self.assertEqual(loans[1]['status'], "returned")
    
    def test_get_reader_with_loans_not_found(self):
        """Test getting loans for non-existent reader."""
        result = self.reader_service.get_reader_with_loans(999)
        self.assertIsNone(result)
    
    def test_validate_reader_number_unique(self):
        """Test reader number uniqueness validation."""
        # Create a reader
        reader = self.reader_service.create_reader("Test Reader", "Test Address", "Test Phone")
        
        # Test uniqueness check
        self.assertFalse(self.reader_service.validate_reader_number_unique(reader.reader_number))
        self.assertTrue(self.reader_service.validate_reader_number_unique(999))  # Non-existent number
        
        # Test excluding current reader from check (for updates)
        self.assertTrue(self.reader_service.validate_reader_number_unique(reader.reader_number, exclude_id=reader.id))

class TestReaderModel(unittest.TestCase):
    """Unit tests for Reader model class."""
    
    def test_reader_creation_success(self):
        """Test successful reader creation."""
        reader = Reader(
            id=1,
            reader_number=1,
            name="Test Reader",
            address="Test Address",
            phone="Test Phone",
            created_date=datetime.now()
        )
        
        self.assertEqual(reader.name, "Test Reader")
        self.assertEqual(reader.address, "Test Address")
        self.assertEqual(reader.phone, "Test Phone")
    
    def test_reader_validation_errors(self):
        """Test reader validation errors."""
        # Test empty name
        with self.assertRaises(ValueError):
            Reader(name="", address="Address", phone="Phone")
        
        # Test empty address
        with self.assertRaises(ValueError):
            Reader(name="Name", address="", phone="Phone")
        
        # Test empty phone
        with self.assertRaises(ValueError):
            Reader(name="Name", address="Address", phone="")
        
        # Test whitespace-only fields
        with self.assertRaises(ValueError):
            Reader(name="   ", address="Address", phone="Phone")
    
    def test_reader_to_dict(self):
        """Test converting reader to dictionary."""
        reader = Reader(
            reader_number=1,
            name="Test Reader",
            address="Test Address",
            phone="Test Phone"
        )
        
        result = reader.to_dict()
        expected = {
            'reader_number': 1,
            'name': "Test Reader",
            'address': "Test Address",
            'phone': "Test Phone"
        }
        
        self.assertEqual(result, expected)
    
    def test_reader_from_db_row(self):
        """Test creating reader from database row."""
        # Mock database row
        class MockRow:
            def __init__(self, data):
                self.data = data
            
            def __getitem__(self, key):
                return self.data[key]
        
        row_data = {
            'id': 1,
            'reader_number': 1,
            'name': "Test Reader",
            'address': "Test Address", 
            'phone': "Test Phone",
            'created_date': "2024-01-01 12:00:00"
        }
        
        row = MockRow(row_data)
        reader = Reader.from_db_row(row)
        
        self.assertEqual(reader.id, 1)
        self.assertEqual(reader.reader_number, 1)
        self.assertEqual(reader.name, "Test Reader")
        self.assertEqual(reader.address, "Test Address")
        self.assertEqual(reader.phone, "Test Phone")
        self.assertIsNotNone(reader.created_date)

if __name__ == '__main__':
    unittest.main()