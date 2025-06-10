#!/usr/bin/env python3
"""
Database initialization script for the Library Management System.

This script initializes the SQLite database with the required schema
and can be run standalone or imported as a module.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager

def initialize_database(db_path: str = "library.db", force: bool = False) -> bool:
    """
    Initialize the library database with schema.
    
    Args:
        db_path: Path to the database file
        force: If True, recreate database even if it exists
        
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Check if database already exists
        if os.path.exists(db_path) and not force:
            print(f"Database already exists at {db_path}")
            print("Use --force to recreate the database")
            return False
        
        # Remove existing database if force is True
        if force and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Initialize database
        print(f"Initializing database: {db_path}")
        db_manager = DatabaseManager(db_path)
        
        # Create tables from schema
        db_manager.initialize_database()
        
        # Verify tables were created
        tables = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        
        table_names = [table['name'] for table in tables if not table['name'].startswith('sqlite_')]
        
        print("Database initialized successfully!")
        print(f"Created tables: {', '.join(table_names)}")
        
        # Create some indexes if they don't exist (they should be in schema.sql)
        indexes = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        
        if indexes:
            index_names = [idx['name'] for idx in indexes]
            print(f"Created indexes: {', '.join(index_names)}")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def add_sample_data(db_path: str = "library.db") -> bool:
    """
    Add sample data to the database for testing purposes.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if sample data was added successfully, False otherwise
    """
    try:
        db_manager = DatabaseManager(db_path)
        
        print("Adding sample data...")
        
        # Sample readers
        sample_readers = [
            (1, "Max Mustermann", "Musterstraße 1, 12345 Musterstadt", "0123-456789"),
            (2, "Anna Schmidt", "Hauptstraße 15, 12345 Musterstadt", "0123-987654"),
            (3, "Hans Müller", "Nebenstraße 22, 12345 Musterstadt", "0123-555666")
        ]
        
        for reader_num, name, address, phone in sample_readers:
            db_manager.execute_command(
                "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
                (reader_num, name, address, phone)
            )
        
        # Sample books
        sample_books = [
            ("B001", "Der kleine Prinz", "Antoine de Saint-Exupéry", "978-3-15-008010-0", 1943),
            ("B002", "1984", "George Orwell", "978-3-15-019108-4", 1949),
            ("B003", "Die Verwandlung", "Franz Kafka", "978-3-15-009900-3", 1915),
            ("B004", "Faust", "Johann Wolfgang von Goethe", "978-3-15-000001-0", 1808),
            ("B005", "Harry Potter und der Stein der Weisen", "J.K. Rowling", "978-3-551-55167-2", 1997)
        ]
        
        for book_num, title, author, isbn, year in sample_books:
            db_manager.execute_command(
                "INSERT INTO books (book_number, title, author, isbn, publication_year) VALUES (?, ?, ?, ?, ?)",
                (book_num, title, author, isbn, year)
            )
        
        # Sample loans (some active, some returned)
        sample_loans = [
            (1, 1, "2024-01-15", "2024-01-25", "returned"),
            (2, 2, "2024-02-01", None, "borrowed"),
            (3, 3, "2024-02-10", "2024-02-20", "returned"),
            (1, 4, "2024-02-15", None, "borrowed")
        ]
        
        for reader_id, book_id, borrow_date, return_date, status in sample_loans:
            db_manager.execute_command(
                "INSERT INTO loans (reader_id, book_id, borrow_date, return_date, status) VALUES (?, ?, ?, ?, ?)",
                (reader_id, book_id, borrow_date, return_date, status)
            )
        
        print("Sample data added successfully!")
        print(f"Added {len(sample_readers)} readers, {len(sample_books)} books, {len(sample_loans)} loans")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        return False

def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Library Management System database")
    parser.add_argument("--db-path", default="library.db", help="Database file path")
    parser.add_argument("--force", action="store_true", help="Force recreation of existing database")
    parser.add_argument("--sample-data", action="store_true", help="Add sample data after initialization")
    
    args = parser.parse_args()
    
    # Initialize database
    success = initialize_database(args.db_path, args.force)
    
    if not success:
        sys.exit(1)
    
    # Add sample data if requested
    if args.sample_data:
        success = add_sample_data(args.db_path)
        if not success:
            sys.exit(1)
    
    print("\nDatabase setup complete!")
    print(f"Database location: {os.path.abspath(args.db_path)}")

if __name__ == "__main__":
    main()