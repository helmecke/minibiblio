import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """Manages SQLite database connections and operations for the library system."""
    
    def __init__(self, db_path: str = "library.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self) -> sqlite3.Connection:
        """
        Create and return a database connection.
        
        Returns:
            SQLite connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return self.connection
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self) -> None:
        """
        Initialize the database by creating tables from schema.sql.
        """
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = self.connect()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to initialize database: {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows
        """
        conn = self.connect()
        try:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE command.
        
        Args:
            command: SQL command string
            params: Command parameters
            
        Returns:
            Number of affected rows or last row ID for INSERT
        """
        conn = self.connect()
        try:
            cursor = conn.execute(command, params)
            conn.commit()
            return cursor.lastrowid if command.strip().upper().startswith('INSERT') else cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Command execution failed: {e}")
    
    def execute_transaction(self, commands: List[tuple]) -> None:
        """
        Execute multiple commands in a single transaction.
        
        Args:
            commands: List of (command, params) tuples
        """
        conn = self.connect()
        try:
            for command, params in commands:
                conn.execute(command, params)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Transaction failed: {e}")
    
    def get_next_reader_number(self) -> int:
        """
        Get the next sequential reader number.
        
        Returns:
            Next available reader number
        """
        result = self.execute_query("SELECT MAX(reader_number) as max_num FROM readers")
        max_num = result[0]['max_num'] if result and result[0]['max_num'] is not None else 0
        return max_num + 1
    
    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for the backup file
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
        except Exception as e:
            raise RuntimeError(f"Backup failed: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()