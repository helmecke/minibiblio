from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json

from database.db_manager import DatabaseManager
from database.models import AuditLog, Loan, Reader, Book

class AuditService:
    """Service class for managing audit log entries."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize audit service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def log_loan_activity(self, action: str, loan: Loan, description: str, 
                         old_values: Dict[str, Any] = None, 
                         new_values: Dict[str, Any] = None,
                         user_info: str = "System") -> AuditLog:
        """
        Log a loan-related activity.
        
        Args:
            action: The action performed (checkout, return, extend, delete)
            loan: The loan object involved
            description: Human-readable description of the action
            old_values: Dictionary of old values (for updates)
            new_values: Dictionary of new values (for updates)
            user_info: Information about who performed the action
            
        Returns:
            Created AuditLog object
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Create audit log entry
        audit_entry = AuditLog(
            loan_id=loan.id,
            reader_id=loan.reader_id,
            book_id=loan.book_id,
            action=action,
            description=description,
            user_info=user_info
        )
        
        # Set old and new values if provided
        if old_values:
            audit_entry.set_old_values_dict(old_values)
        if new_values:
            audit_entry.set_new_values_dict(new_values)
        
        # Insert into database
        audit_id = self.db.execute_command(
            """INSERT INTO audit_log (loan_id, reader_id, book_id, action, description, 
               old_values, new_values, user_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (audit_entry.loan_id, audit_entry.reader_id, audit_entry.book_id,
             audit_entry.action, audit_entry.description, audit_entry.old_values,
             audit_entry.new_values, audit_entry.user_info)
        )
        
        # Return created audit entry with ID
        audit_entry.id = audit_id
        audit_entry.timestamp = datetime.now()
        
        return audit_entry
    
    def log_checkout(self, loan: Loan, user_info: str = "System") -> AuditLog:
        """
        Log a book checkout activity.
        
        Args:
            loan: The loan object that was created
            user_info: Information about who performed the checkout
            
        Returns:
            Created AuditLog object
        """
        description = f"Buch '{loan.book_title or 'Unbekannt'}' ({loan.book_number or 'N/A'}) an '{loan.reader_name or 'Unbekannt'}' ausgeliehen"
        
        new_values = {
            'borrow_date': loan.borrow_date.isoformat() if loan.borrow_date else None,
            'due_date': loan.due_date.isoformat() if loan.due_date else None,
            'status': loan.status
        }
        
        return self.log_loan_activity('checkout', loan, description, 
                                    new_values=new_values, user_info=user_info)
    
    def log_return(self, loan: Loan, old_loan: Loan = None, user_info: str = "System") -> AuditLog:
        """
        Log a book return activity.
        
        Args:
            loan: The loan object after return
            old_loan: The loan object before return (for comparison)
            user_info: Information about who performed the return
            
        Returns:
            Created AuditLog object
        """
        description = f"Buch '{loan.book_title or 'Unbekannt'}' ({loan.book_number or 'N/A'}) von '{loan.reader_name or 'Unbekannt'}' zurückgegeben"
        
        old_values = {}
        if old_loan:
            old_values = {
                'status': old_loan.status,
                'return_date': old_loan.return_date.isoformat() if old_loan.return_date else None
            }
        
        new_values = {
            'status': loan.status,
            'return_date': loan.return_date.isoformat() if loan.return_date else None
        }
        
        return self.log_loan_activity('return', loan, description, 
                                    old_values=old_values, new_values=new_values, 
                                    user_info=user_info)
    
    def log_extension(self, loan: Loan, old_due_date: date, extension_days: int, 
                     user_info: str = "System") -> AuditLog:
        """
        Log a loan extension activity.
        
        Args:
            loan: The loan object after extension
            old_due_date: The original due date before extension
            extension_days: Number of days extended
            user_info: Information about who performed the extension
            
        Returns:
            Created AuditLog object
        """
        description = f"Ausleihe für Buch '{loan.book_title or 'Unbekannt'}' ({loan.book_number or 'N/A'}) um {extension_days} Tage verlängert"
        
        old_values = {
            'due_date': old_due_date.isoformat()
        }
        
        new_values = {
            'due_date': loan.due_date.isoformat() if loan.due_date else None,
            'extension_days': extension_days
        }
        
        return self.log_loan_activity('extend', loan, description, 
                                    old_values=old_values, new_values=new_values, 
                                    user_info=user_info)
    
    def log_deletion(self, loan: Loan, user_info: str = "System") -> AuditLog:
        """
        Log a loan deletion activity.
        
        Args:
            loan: The loan object that was deleted
            user_info: Information about who performed the deletion
            
        Returns:
            Created AuditLog object
        """
        description = f"Ausleihe für Buch '{loan.book_title or 'Unbekannt'}' ({loan.book_number or 'N/A'}) gelöscht"
        
        old_values = {
            'status': loan.status,
            'borrow_date': loan.borrow_date.isoformat() if loan.borrow_date else None,
            'due_date': loan.due_date.isoformat() if loan.due_date else None,
            'return_date': loan.return_date.isoformat() if loan.return_date else None
        }
        
        return self.log_loan_activity('delete', loan, description, 
                                    old_values=old_values, user_info=user_info)
    
    def get_audit_logs(self, limit: int = None, offset: int = 0) -> List[AuditLog]:
        """
        Get audit log entries with reader and book information.
        
        Args:
            limit: Maximum number of entries to return (optional)
            offset: Number of entries to skip (for pagination)
            
        Returns:
            List of AuditLog objects ordered by timestamp (newest first)
        """
        query = """
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            ORDER BY a.timestamp DESC
        """
        
        params = []
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            if offset > 0:
                query += " OFFSET ?"
                params.append(offset)
        
        if params:
            rows = self.db.execute_query(query, params)
        else:
            rows = self.db.execute_query(query)
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_logs_by_loan(self, loan_id: int) -> List[AuditLog]:
        """
        Get audit log entries for a specific loan.
        
        Args:
            loan_id: Loan's database ID
            
        Returns:
            List of AuditLog objects for the loan
        """
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.loan_id = ?
            ORDER BY a.timestamp DESC
        """, (loan_id,))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_logs_by_reader(self, reader_id: int) -> List[AuditLog]:
        """
        Get audit log entries for a specific reader.
        
        Args:
            reader_id: Reader's database ID
            
        Returns:
            List of AuditLog objects for the reader
        """
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.reader_id = ?
            ORDER BY a.timestamp DESC
        """, (reader_id,))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_logs_by_book(self, book_id: int) -> List[AuditLog]:
        """
        Get audit log entries for a specific book.
        
        Args:
            book_id: Book's database ID
            
        Returns:
            List of AuditLog objects for the book
        """
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.book_id = ?
            ORDER BY a.timestamp DESC
        """, (book_id,))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_logs_by_action(self, action: str) -> List[AuditLog]:
        """
        Get audit log entries for a specific action type.
        
        Args:
            action: Action type (checkout, return, extend, delete)
            
        Returns:
            List of AuditLog objects for the action
        """
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.action = ?
            ORDER BY a.timestamp DESC
        """, (action,))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_logs_by_date_range(self, start_date: date, end_date: date) -> List[AuditLog]:
        """
        Get audit log entries within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of AuditLog objects within the date range
        """
        # Convert dates to datetime strings for comparison
        start_datetime = f"{start_date.isoformat()} 00:00:00"
        end_datetime = f"{end_date.isoformat()} 23:59:59"
        
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.timestamp BETWEEN ? AND ?
            ORDER BY a.timestamp DESC
        """, (start_datetime, end_datetime))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def search_audit_logs(self, search_term: str) -> List[AuditLog]:
        """
        Search audit log entries by description, reader name, or book title.
        
        Args:
            search_term: Search term to look for
            
        Returns:
            List of matching AuditLog objects
        """
        if not search_term.strip():
            return []
        
        search_pattern = f"%{search_term.strip()}%"
        rows = self.db.execute_query("""
            SELECT a.*, r.name as reader_name, b.title as book_title, b.book_number
            FROM audit_log a
            LEFT JOIN readers r ON a.reader_id = r.id
            LEFT JOIN books b ON a.book_id = b.id
            WHERE a.description LIKE ? 
               OR r.name LIKE ? 
               OR b.title LIKE ?
               OR b.book_number LIKE ?
            ORDER BY a.timestamp DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        return [AuditLog.from_db_row(row) for row in rows]
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with audit statistics
        """
        # Total audit entries
        total_entries = self.db.execute_query(
            "SELECT COUNT(*) as count FROM audit_log"
        )[0]['count']
        
        # Entries by action
        action_counts = {}
        for action in ['checkout', 'return', 'extend', 'delete']:
            count = self.db.execute_query(
                "SELECT COUNT(*) as count FROM audit_log WHERE action = ?",
                (action,)
            )[0]['count']
            action_counts[action] = count
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_activity = self.db.execute_query(
            "SELECT COUNT(*) as count FROM audit_log WHERE timestamp >= ?",
            (week_ago,)
        )[0]['count']
        
        # Most active day (last 30 days)
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        daily_activity = self.db.execute_query("""
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM audit_log 
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp) 
            ORDER BY count DESC 
            LIMIT 1
        """, (month_ago,))
        
        most_active_day = None
        if daily_activity:
            most_active_day = {
                'date': daily_activity[0]['date'],
                'count': daily_activity[0]['count']
            }
        
        return {
            'total_entries': total_entries,
            'action_counts': action_counts,
            'recent_activity_7_days': recent_activity,
            'most_active_day_30_days': most_active_day
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 365) -> int:
        """
        Clean up old audit log entries.
        
        Args:
            days_to_keep: Number of days to keep (default 365)
            
        Returns:
            Number of entries deleted
        """
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        affected_rows = self.db.execute_command(
            "DELETE FROM audit_log WHERE timestamp < ?",
            (cutoff_date,)
        )
        
        return affected_rows