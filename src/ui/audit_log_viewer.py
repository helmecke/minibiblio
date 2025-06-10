import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.audit_service import AuditService
from database.models import AuditLog

class AuditLogViewer:
    """Audit log viewer for tracking loan activities."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """
        Initialize audit log viewer.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.audit_service = AuditService(db_manager)
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Current filter settings
        self.current_filter = "all"
        self.current_search = ""
        self.current_page = 0
        self.page_size = 50
        
        self._create_widgets()
        self._load_audit_logs()
    
    def _create_widgets(self):
        """Create the audit log viewer widgets."""
        # Title and controls frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(top_frame, text="Audit-Protokoll", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Statistics button
        stats_button = ttk.Button(button_frame, text="Statistiken", 
                                 command=self._show_statistics)
        stats_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Export button
        export_button = ttk.Button(button_frame, text="Exportieren", 
                                  command=self._export_logs)
        export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(button_frame, text="Aktualisieren", 
                                   command=self._load_audit_logs)
        refresh_button.pack(side=tk.LEFT)
        
        # Search and filter frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search
        ttk.Label(search_frame, text="Suchen:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Action filter
        ttk.Label(search_frame, text="Aktion:").pack(side=tk.LEFT, padx=(10, 0))
        self.action_var = tk.StringVar(value="all")
        action_combo = ttk.Combobox(search_frame, textvariable=self.action_var, 
                                   values=["all", "checkout", "return", "extend", "delete"], 
                                   state="readonly", width=12)
        action_combo.pack(side=tk.LEFT, padx=(5, 10))
        action_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Date filter frame
        date_frame = ttk.Frame(search_frame)
        date_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(date_frame, text="Zeitraum:").pack(side=tk.LEFT)
        self.date_filter_var = tk.StringVar(value="all")
        date_combo = ttk.Combobox(date_frame, textvariable=self.date_filter_var,
                                 values=["all", "today", "week", "month"], 
                                 state="readonly", width=10)
        date_combo.pack(side=tk.LEFT, padx=(5, 0))
        date_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Results info frame
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.results_label = ttk.Label(info_frame, text="")
        self.results_label.pack(side=tk.LEFT)
        
        # Pagination frame
        pagination_frame = ttk.Frame(info_frame)
        pagination_frame.pack(side=tk.RIGHT)
        
        self.prev_button = ttk.Button(pagination_frame, text="◀ Zurück", 
                                     command=self._prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_label = ttk.Label(pagination_frame, text="Seite 1")
        self.page_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_button = ttk.Button(pagination_frame, text="Weiter ▶", 
                                     command=self._next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("timestamp", "action", "reader", "book", "description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        self.tree.heading("timestamp", text="Zeit")
        self.tree.heading("action", text="Aktion")
        self.tree.heading("reader", text="Leser")
        self.tree.heading("book", text="Buch")
        self.tree.heading("description", text="Beschreibung")
        
        self.tree.column("timestamp", width=140, minwidth=120)
        self.tree.column("action", width=100, minwidth=80)
        self.tree.column("reader", width=150, minwidth=120)
        self.tree.column("book", width=200, minwidth=150)
        self.tree.column("description", width=300, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Details anzeigen", command=self._view_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Aktivitäten für diesen Leser", command=self._view_reader_activity)
        self.context_menu.add_command(label="Aktivitäten für dieses Buch", command=self._view_book_activity)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _load_audit_logs(self):
        """Load and display audit logs based on current filters."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Apply filters
            logs = self._get_filtered_logs()
            
            # Apply pagination
            start_idx = self.current_page * self.page_size
            end_idx = start_idx + self.page_size
            page_logs = logs[start_idx:end_idx]
            
            # Add logs to treeview
            for log in page_logs:
                # Format timestamp
                timestamp_str = ""
                if log.timestamp:
                    timestamp_str = log.timestamp.strftime('%d.%m.%Y %H:%M')
                
                # Format action
                action_map = {
                    'checkout': 'Ausleihe',
                    'return': 'Rückgabe',
                    'extend': 'Verlängerung',
                    'delete': 'Löschung'
                }
                action_display = action_map.get(log.action, log.action)
                
                # Format reader and book info
                reader_info = log.reader_name or "Unbekannt"
                book_info = log.book_title or "Unbekannt"
                if log.book_number:
                    book_info += f" ({log.book_number})"
                
                self.tree.insert("", tk.END, values=(
                    timestamp_str,
                    action_display,
                    reader_info,
                    book_info,
                    log.description
                ), tags=(log.id,))
            
            # Update results info
            total_results = len(logs)
            start_num = start_idx + 1 if page_logs else 0
            end_num = min(end_idx, total_results)
            
            self.results_label.config(text=f"Einträge {start_num}-{end_num} von {total_results}")
            
            # Update pagination
            total_pages = (total_results + self.page_size - 1) // self.page_size
            current_page_display = self.current_page + 1 if total_pages > 0 else 0
            self.page_label.config(text=f"Seite {current_page_display} von {total_pages}")
            
            self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if end_idx < total_results else tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Audit-Logs: {str(e)}")
    
    def _get_filtered_logs(self) -> List[AuditLog]:
        """Get logs based on current filter settings."""
        search_term = self.search_entry.get().strip()
        action_filter = self.action_var.get()
        date_filter = self.date_filter_var.get()
        
        # Start with all logs or search results
        if search_term:
            logs = self.audit_service.search_audit_logs(search_term)
        else:
            logs = self.audit_service.get_audit_logs()
        
        # Apply action filter
        if action_filter != "all":
            logs = [log for log in logs if log.action == action_filter]
        
        # Apply date filter
        if date_filter != "all":
            now = datetime.now()
            if date_filter == "today":
                start_date = now.date()
                end_date = start_date
            elif date_filter == "week":
                start_date = (now - timedelta(days=7)).date()
                end_date = now.date()
            elif date_filter == "month":
                start_date = (now - timedelta(days=30)).date()
                end_date = now.date()
            else:
                return logs
            
            logs = [log for log in logs if log.timestamp and 
                   start_date <= log.timestamp.date() <= end_date]
        
        return logs
    
    def _on_search(self, event):
        """Handle search input."""
        self.current_page = 0  # Reset to first page
        self._load_audit_logs()
    
    def _on_filter_change(self, event):
        """Handle filter change."""
        self.current_page = 0  # Reset to first page
        self._load_audit_logs()
    
    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_audit_logs()
    
    def _next_page(self):
        """Go to next page."""
        self.current_page += 1
        self._load_audit_logs()
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_log_id(self) -> Optional[int]:
        """Get the ID of the currently selected audit log."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return int(item['tags'][0])
        return None
    
    def _on_double_click(self, event):
        """Handle double-click on audit log item."""
        self._view_details()
    
    def _view_details(self):
        """View details of selected audit log entry."""
        log_id = self._get_selected_log_id()
        if not log_id:
            return
        
        try:
            # Get all logs to find the specific one (simple approach)
            all_logs = self.audit_service.get_audit_logs()
            selected_log = None
            for log in all_logs:
                if log.id == log_id:
                    selected_log = log
                    break
            
            if not selected_log:
                messagebox.showerror("Fehler", "Audit-Log-Eintrag nicht gefunden.")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title("Audit-Log Details")
            details_window.geometry("500x400")
            details_window.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Basic info
            info_frame = ttk.LabelFrame(main_frame, text="Grundinformationen", padding="10")
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Create info labels
            info_labels = [
                ("Zeit:", selected_log.timestamp.strftime('%d.%m.%Y %H:%M:%S') if selected_log.timestamp else "Unbekannt"),
                ("Aktion:", {'checkout': 'Ausleihe', 'return': 'Rückgabe', 'extend': 'Verlängerung', 'delete': 'Löschung'}.get(selected_log.action, selected_log.action)),
                ("Leser:", selected_log.reader_name or "Unbekannt"),
                ("Buch:", f"{selected_log.book_title or 'Unbekannt'} ({selected_log.book_number or 'N/A'})"),
                ("Beschreibung:", selected_log.description),
                ("Benutzer:", selected_log.user_info or "System")
            ]
            
            for label, value in info_labels:
                row_frame = ttk.Frame(info_frame)
                row_frame.pack(fill=tk.X, pady=2)
                ttk.Label(row_frame, text=label, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=value, wraplength=300).pack(side=tk.LEFT, padx=(10, 0))
            
            # Old values (if any)
            if selected_log.old_values:
                old_frame = ttk.LabelFrame(main_frame, text="Alte Werte", padding="10")
                old_frame.pack(fill=tk.X, pady=(0, 10))
                
                old_text = tk.Text(old_frame, height=4, wrap=tk.WORD)
                old_text.pack(fill=tk.BOTH, expand=True)
                old_text.insert(tk.END, selected_log.old_values)
                old_text.config(state=tk.DISABLED)
            
            # New values (if any)
            if selected_log.new_values:
                new_frame = ttk.LabelFrame(main_frame, text="Neue Werte", padding="10")
                new_frame.pack(fill=tk.X, pady=(0, 10))
                
                new_text = tk.Text(new_frame, height=4, wrap=tk.WORD)
                new_text.pack(fill=tk.BOTH, expand=True)
                new_text.insert(tk.END, selected_log.new_values)
                new_text.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Schließen", 
                      command=details_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Details: {str(e)}")
    
    def _view_reader_activity(self):
        """View all activities for the selected reader."""
        log_id = self._get_selected_log_id()
        if not log_id:
            return
        
        try:
            # Get the selected log to find reader_id
            all_logs = self.audit_service.get_audit_logs()
            selected_log = None
            for log in all_logs:
                if log.id == log_id:
                    selected_log = log
                    break
            
            if not selected_log or not selected_log.reader_id:
                messagebox.showinfo("Information", "Keine Leser-Information verfügbar.")
                return
            
            # Filter by reader
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, selected_log.reader_name or "")
            self.action_var.set("all")
            self.date_filter_var.set("all")
            self._load_audit_logs()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Filtern nach Leser: {str(e)}")
    
    def _view_book_activity(self):
        """View all activities for the selected book."""
        log_id = self._get_selected_log_id()
        if not log_id:
            return
        
        try:
            # Get the selected log to find book info
            all_logs = self.audit_service.get_audit_logs()
            selected_log = None
            for log in all_logs:
                if log.id == log_id:
                    selected_log = log
                    break
            
            if not selected_log or not selected_log.book_id:
                messagebox.showinfo("Information", "Keine Buch-Information verfügbar.")
                return
            
            # Filter by book
            self.search_entry.delete(0, tk.END)
            book_search = selected_log.book_title or selected_log.book_number or ""
            self.search_entry.insert(0, book_search)
            self.action_var.set("all")
            self.date_filter_var.set("all")
            self._load_audit_logs()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Filtern nach Buch: {str(e)}")
    
    def _show_statistics(self):
        """Show audit log statistics."""
        try:
            stats = self.audit_service.get_audit_statistics()
            
            # Create statistics window
            stats_window = tk.Toplevel(self.parent)
            stats_window.title("Audit-Log Statistiken")
            stats_window.geometry("400x300")
            stats_window.resizable(False, False)
            
            main_frame = ttk.Frame(stats_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            ttk.Label(main_frame, text="Audit-Log Statistiken", 
                     font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 20))
            
            # General stats
            general_frame = ttk.LabelFrame(main_frame, text="Allgemein", padding="10")
            general_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(general_frame, text=f"Gesamte Einträge: {stats['total_entries']}").pack(anchor=tk.W)
            ttk.Label(general_frame, text=f"Aktivität (7 Tage): {stats['recent_activity_7_days']}").pack(anchor=tk.W)
            
            # Action counts
            action_frame = ttk.LabelFrame(main_frame, text="Nach Aktion", padding="10")
            action_frame.pack(fill=tk.X, pady=(0, 10))
            
            action_names = {
                'checkout': 'Ausleihen',
                'return': 'Rückgaben',
                'extend': 'Verlängerungen',
                'delete': 'Löschungen'
            }
            
            for action, count in stats['action_counts'].items():
                display_name = action_names.get(action, action)
                ttk.Label(action_frame, text=f"{display_name}: {count}").pack(anchor=tk.W)
            
            # Most active day
            if stats.get('most_active_day_30_days'):
                active_day = stats['most_active_day_30_days']
                most_active_frame = ttk.LabelFrame(main_frame, text="Aktivster Tag (30 Tage)", padding="10")
                most_active_frame.pack(fill=tk.X, pady=(0, 10))
                
                ttk.Label(most_active_frame, 
                         text=f"Datum: {active_day['date']}").pack(anchor=tk.W)
                ttk.Label(most_active_frame, 
                         text=f"Aktivitäten: {active_day['count']}").pack(anchor=tk.W)
            
            # Close button
            ttk.Button(main_frame, text="Schließen", 
                      command=stats_window.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Statistiken: {str(e)}")
    
    def _export_logs(self):
        """Export audit logs to CSV file."""
        try:
            from tkinter import filedialog
            import csv
            
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                title="Audit-Logs exportieren",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Get logs based on current filters
            logs = self._get_filtered_logs()
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Zeitstempel', 'Aktion', 'Leser', 'Buch', 'Beschreibung', 
                               'Alte Werte', 'Neue Werte', 'Benutzer'])
                
                # Data rows
                for log in logs:
                    timestamp_str = log.timestamp.strftime('%d.%m.%Y %H:%M:%S') if log.timestamp else ""
                    book_info = f"{log.book_title or 'Unbekannt'} ({log.book_number or 'N/A'})"
                    
                    writer.writerow([
                        timestamp_str,
                        log.action,
                        log.reader_name or 'Unbekannt',
                        book_info,
                        log.description,
                        log.old_values or '',
                        log.new_values or '',
                        log.user_info or 'System'
                    ])
            
            messagebox.showinfo("Erfolg", f"Audit-Logs erfolgreich exportiert nach:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {str(e)}")

# Example usage/test function
def main():
    """Test the audit log viewer UI."""
    root = tk.Tk()
    root.title("Audit Log Viewer Test")
    root.geometry("1200x700")
    
    # Initialize database
    db_manager = DatabaseManager("test_library.db")
    db_manager.initialize_database()
    
    # Create audit log viewer
    audit_viewer = AuditLogViewer(root, db_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()