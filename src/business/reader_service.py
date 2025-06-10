from typing import List, Optional
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import Reader

class ReaderService:
    """Service class for managing library readers with CRUD operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize reader service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def create_reader(self, name: str, address: str, phone: str) -> Reader:
        """
        Create a new library reader with automatic sequential number.
        
        Args:
            name: Reader's full name
            address: Reader's address
            phone: Reader's phone number
            
        Returns:
            Created Reader object with assigned ID and reader number
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Create reader object for validation
        reader = Reader(name=name.strip(), address=address.strip(), phone=phone.strip())
        
        # Get next sequential reader number
        reader.reader_number = self.db.get_next_reader_number()
        
        # Insert into database
        reader_id = self.db.execute_command(
            "INSERT INTO readers (reader_number, name, address, phone) VALUES (?, ?, ?, ?)",
            (reader.reader_number, reader.name, reader.address, reader.phone)
        )
        
        # Return created reader with ID
        reader.id = reader_id
        reader.created_date = datetime.now()
        
        return reader
    
    def get_reader_by_id(self, reader_id: int) -> Optional[Reader]:
        """
        Get reader by ID.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            Reader object if found, None otherwise
        """
        rows = self.db.execute_query(
            "SELECT * FROM readers WHERE id = ?",
            (reader_id,)
        )
        
        return Reader.from_db_row(rows[0]) if rows else None
    
    def get_reader_by_number(self, reader_number: int) -> Optional[Reader]:
        """
        Get reader by reader number.
        
        Args:
            reader_number: Reader's sequential number
            
        Returns:
            Reader object if found, None otherwise
        """
        rows = self.db.execute_query(
            "SELECT * FROM readers WHERE reader_number = ?",
            (reader_number,)
        )
        
        return Reader.from_db_row(rows[0]) if rows else None
    
    def get_all_readers(self) -> List[Reader]:
        """
        Get all readers ordered by reader number.
        
        Returns:
            List of all Reader objects
        """
        rows = self.db.execute_query(
            "SELECT * FROM readers ORDER BY reader_number"
        )
        
        return [Reader.from_db_row(row) for row in rows]
    
    def search_readers_by_name(self, name_query: str) -> List[Reader]:
        """
        Search readers by name (case-insensitive partial match).
        
        Args:
            name_query: Search query for reader name
            
        Returns:
            List of matching Reader objects
        """
        if not name_query.strip():
            return []
        
        search_term = f"%{name_query.strip()}%"
        rows = self.db.execute_query(
            "SELECT * FROM readers WHERE name LIKE ? ORDER BY reader_number",
            (search_term,)
        )
        
        return [Reader.from_db_row(row) for row in rows]
    
    def update_reader(self, reader_id: int, name: str = None, address: str = None, phone: str = None) -> Optional[Reader]:
        """
        Update reader information.
        
        Args:
            reader_id: Reader's database ID
            name: New name (optional)
            address: New address (optional)
            phone: New phone (optional)
            
        Returns:
            Updated Reader object if successful, None if reader not found
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Get existing reader
        existing_reader = self.get_reader_by_id(reader_id)
        if not existing_reader:
            return None
        
        # Prepare update values
        update_name = name.strip() if name is not None else existing_reader.name
        update_address = address.strip() if address is not None else existing_reader.address
        update_phone = phone.strip() if phone is not None else existing_reader.phone
        
        # Validate updated data
        updated_reader = Reader(
            id=existing_reader.id,
            reader_number=existing_reader.reader_number,
            name=update_name,
            address=update_address,
            phone=update_phone,
            created_date=existing_reader.created_date
        )
        
        # Update database
        affected_rows = self.db.execute_command(
            "UPDATE readers SET name = ?, address = ?, phone = ? WHERE id = ?",
            (update_name, update_address, update_phone, reader_id)
        )
        
        return updated_reader if affected_rows > 0 else None
    
    def delete_reader(self, reader_id: int) -> bool:
        """
        Delete a reader from the database.
        
        Note: This will only succeed if the reader has no active loans.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Check for any loan history
        any_loans = self.db.execute_query(
            "SELECT COUNT(*) as count FROM loans WHERE reader_id = ?",
            (reader_id,)
        )
        
        if any_loans and any_loans[0]['count'] > 0:
            raise ValueError("Cannot delete reader with loan history")
        
        # Delete reader
        affected_rows = self.db.execute_command(
            "DELETE FROM readers WHERE id = ?",
            (reader_id,)
        )
        
        return affected_rows > 0
    
    def get_reader_with_loans(self, reader_id: int) -> Optional[dict]:
        """
        Get reader information along with their loan history.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            Dictionary with reader info and loans, None if reader not found
        """
        reader = self.get_reader_by_id(reader_id)
        if not reader:
            return None
        
        # Get loan history with book information
        loan_rows = self.db.execute_query("""
            SELECT l.*, b.title, b.book_number 
            FROM loans l
            JOIN books b ON l.book_id = b.id
            WHERE l.reader_id = ?
            ORDER BY l.borrow_date DESC
        """, (reader_id,))
        
        loans = []
        for row in loan_rows:
            loan_data = {
                'id': row['id'],
                'book_title': row['title'],
                'book_number': row['book_number'],
                'borrow_date': row['borrow_date'],
                'return_date': row['return_date'],
                'status': row['status']
            }
            loans.append(loan_data)
        
        return {
            'reader': reader,
            'loans': loans,
            'active_loans_count': len([l for l in loans if l['status'] == 'borrowed']),
            'total_loans_count': len(loans)
        }
    
    def validate_reader_number_unique(self, reader_number: int, exclude_id: int = None) -> bool:
        """
        Check if reader number is unique.
        
        Args:
            reader_number: Reader number to check
            exclude_id: Reader ID to exclude from check (for updates)
            
        Returns:
            True if reader number is unique, False otherwise
        """
        query = "SELECT COUNT(*) as count FROM readers WHERE reader_number = ?"
        params = [reader_number]
        
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        
        result = self.db.execute_query(query, tuple(params))
        return result[0]['count'] == 0 if result else False