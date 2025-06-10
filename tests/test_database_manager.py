import unittest
import tempfile
import os
import sqlite3
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Unit tests for DatabaseManager class."""
    
    def setUp(self):
        """Set up test database before each test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_manager = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db_manager.disconnect()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization."""
        self.assertEqual(self.db_manager.db_path, self.db_path)
        self.assertIsNone(self.db_manager.connection)
    
    def test_connect_creates_connection(self):
        """Test that connect creates a database connection."""
        connection = self.db_manager.connect()
        
        self.assertIsNotNone(connection)
        self.assertIsInstance(connection, sqlite3.Connection)
        self.assertEqual(self.db_manager.connection, connection)
        
        # Test that subsequent calls return the same connection
        connection2 = self.db_manager.connect()
        self.assertEqual(connection, connection2)
    
    def test_connect_sets_row_factory(self):
        """Test that connect sets the row factory."""
        connection = self.db_manager.connect()
        self.assertEqual(connection.row_factory, sqlite3.Row)
    
    def test_disconnect(self):
        """Test disconnecting from database."""
        self.db_manager.connect()
        self.assertIsNotNone(self.db_manager.connection)
        
        self.db_manager.disconnect()
        self.assertIsNone(self.db_manager.connection)
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when no connection exists."""
        # Should not raise an error
        self.db_manager.disconnect()
        self.assertIsNone(self.db_manager.connection)
    
    def test_initialize_database_success(self):
        """Test successful database initialization."""
        self.db_manager.initialize_database()
        
        # Verify tables were created
        connection = self.db_manager.connect()
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['readers', 'books', 'loans', 'audit_log']
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_initialize_database_missing_schema(self):
        """Test database initialization with missing schema file."""
        # Create a DatabaseManager with invalid schema path
        invalid_db_manager = DatabaseManager(self.db_path)
        
        # Temporarily move the schema file to test error handling
        schema_path = Path(__file__).parent.parent / "src" / "database" / "schema.sql"
        backup_path = schema_path.with_suffix('.sql.backup')
        
        if schema_path.exists():
            schema_path.rename(backup_path)
        
        try:
            with self.assertRaises(FileNotFoundError):
                invalid_db_manager.initialize_database()
        finally:
            # Restore schema file
            if backup_path.exists():
                backup_path.rename(schema_path)
    
    def test_execute_query_success(self):
        """Test successful query execution."""
        self.db_manager.initialize_database()
        
        # Insert test data
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "123-456-7890")
        )
        
        # Execute query
        results = self.db_manager.execute_query(
            "SELECT * FROM readers WHERE reader_number = ?",
            (1,)
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Test Reader")
        self.assertEqual(results[0]['reader_number'], 1)
    
    def test_execute_query_without_params(self):
        """Test query execution without parameters."""
        self.db_manager.initialize_database()
        
        results = self.db_manager.execute_query("SELECT COUNT(*) as count FROM readers")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['count'], 0)
    
    def test_execute_query_invalid_sql(self):
        """Test query execution with invalid SQL."""
        self.db_manager.initialize_database()
        
        with self.assertRaises(RuntimeError) as context:
            self.db_manager.execute_query("INVALID SQL STATEMENT")
        
        self.assertIn("Query execution failed", str(context.exception))
    
    def test_execute_query_connection_error(self):
        """Test query execution with connection error."""
        # Create manager with invalid database path
        invalid_path = "/invalid/path/database.db"
        invalid_db_manager = DatabaseManager(invalid_path)
        
        with self.assertRaises(RuntimeError) as context:
            invalid_db_manager.execute_query("SELECT 1")
        
        self.assertIn("Query execution failed", str(context.exception))
    
    def test_execute_command_success(self):
        """Test successful command execution."""
        self.db_manager.initialize_database()
        
        # Execute INSERT command
        row_id = self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "123-456-7890")
        )
        
        self.assertIsInstance(row_id, int)
        self.assertGreater(row_id, 0)
        
        # Verify insertion
        results = self.db_manager.execute_query("SELECT * FROM readers WHERE id = ?", (row_id,))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Test Reader")
    
    def test_execute_command_update(self):
        """Test UPDATE command execution."""
        self.db_manager.initialize_database()
        
        # Insert test data
        row_id = self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "123-456-7890")
        )
        
        # Execute UPDATE command
        affected_rows = self.db_manager.execute_command(
            "UPDATE readers SET name = ? WHERE id = ?",
            ("Updated Reader", row_id)
        )
        
        self.assertEqual(affected_rows, 1)
        
        # Verify update
        results = self.db_manager.execute_query("SELECT name FROM readers WHERE id = ?", (row_id,))
        self.assertEqual(results[0]['name'], "Updated Reader")
    
    def test_execute_command_delete(self):
        """Test DELETE command execution."""
        self.db_manager.initialize_database()
        
        # Insert test data
        row_id = self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "123-456-7890")
        )
        
        # Execute DELETE command
        affected_rows = self.db_manager.execute_command(
            "DELETE FROM readers WHERE id = ?",
            (row_id,)
        )
        
        self.assertEqual(affected_rows, 1)
        
        # Verify deletion
        results = self.db_manager.execute_query("SELECT * FROM readers WHERE id = ?", (row_id,))
        self.assertEqual(len(results), 0)
    
    def test_execute_command_without_params(self):
        """Test command execution without parameters."""
        self.db_manager.initialize_database()
        
        # Execute command without parameters
        affected_rows = self.db_manager.execute_command("DELETE FROM readers")
        
        self.assertEqual(affected_rows, 0)  # No rows to delete initially
    
    def test_execute_command_invalid_sql(self):
        """Test command execution with invalid SQL."""
        self.db_manager.initialize_database()
        
        with self.assertRaises(RuntimeError) as context:
            self.db_manager.execute_command("INVALID SQL COMMAND")
        
        self.assertIn("Command execution failed", str(context.exception))
    
    def test_execute_command_constraint_violation(self):
        """Test command execution with constraint violation."""
        self.db_manager.initialize_database()
        
        # Insert first reader
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader 1", "Address 1", "123-456-7890")
        )
        
        # Try to insert reader with duplicate reader_number
        with self.assertRaises(RuntimeError) as context:
            self.db_manager.execute_command(
                "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
                (1, "Test Reader 2", "Address 2", "123-456-7891")
            )
        
        self.assertIn("Command execution failed", str(context.exception))
    
    def test_execute_command_foreign_key_violation(self):
        """Test command execution with foreign key violation."""
        self.db_manager.initialize_database()
        
        # Enable foreign key constraints
        self.db_manager.execute_command("PRAGMA foreign_keys = ON")
        
        # Try to insert loan with non-existent reader_id and book_id
        with self.assertRaises(RuntimeError) as context:
            self.db_manager.execute_command(
                "INSERT INTO loans (reader_id, book_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
                (999, 999, "2024-01-01", "2024-01-15", "borrowed")
            )
        
        self.assertIn("Command execution failed", str(context.exception))
    
    def test_transaction_rollback_on_error(self):
        """Test that transactions are rolled back on error."""
        self.db_manager.initialize_database()
        
        # Insert valid reader first
        self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, "Test Reader", "Test Address", "123-456-7890")
        )
        
        # Try batch operation with one invalid command
        try:
            # This should fail due to duplicate reader_number
            self.db_manager.execute_command(
                "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
                (1, "Duplicate Reader", "Address", "Phone")
            )
        except RuntimeError:
            pass  # Expected
        
        # Verify first reader is still there (transaction not affected)
        results = self.db_manager.execute_query("SELECT COUNT(*) as count FROM readers")
        self.assertEqual(results[0]['count'], 1)
    
    def test_database_file_permissions(self):
        """Test database file creation and permissions."""
        # Test with custom database path
        custom_path = tempfile.mktemp(suffix='.db')
        custom_db_manager = DatabaseManager(custom_path)
        
        try:
            custom_db_manager.initialize_database()
            
            # Verify file was created
            self.assertTrue(os.path.exists(custom_path))
            
            # Verify it's a valid SQLite database
            connection = custom_db_manager.connect()
            self.assertIsInstance(connection, sqlite3.Connection)
            
        finally:
            custom_db_manager.disconnect()
            if os.path.exists(custom_path):
                os.unlink(custom_path)
    
    def test_large_query_result(self):
        """Test handling of large query results."""
        self.db_manager.initialize_database()
        
        # Insert multiple records
        for i in range(100):
            self.db_manager.execute_command(
                "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
                (i + 1, f"Reader {i + 1}", f"Address {i + 1}", f"Phone {i + 1}")
            )
        
        # Query all records
        results = self.db_manager.execute_query("SELECT * FROM readers ORDER BY reader_number")
        
        self.assertEqual(len(results), 100)
        self.assertEqual(results[0]['reader_number'], 1)
        self.assertEqual(results[99]['reader_number'], 100)
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        self.db_manager.initialize_database()
        
        # Insert reader with Unicode characters
        unicode_name = "Тест Читатель"  # Cyrillic
        unicode_address = "测试地址"  # Chinese
        unicode_phone = "123-456-7890"
        
        row_id = self.db_manager.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (1, unicode_name, unicode_address, unicode_phone)
        )
        
        # Query and verify Unicode data
        results = self.db_manager.execute_query("SELECT * FROM readers WHERE id = ?", (row_id,))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], unicode_name)
        self.assertEqual(results[0]['address'], unicode_address)
        self.assertEqual(results[0]['phone'], unicode_phone)

if __name__ == '__main__':
    unittest.main()