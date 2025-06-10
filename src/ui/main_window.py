import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.audit_service import AuditService
from ui.reader_management import ReaderListView
from ui.book_management import BookListView
from ui.lending_operations import ActiveLoansView
from ui.search_interface import SearchInterface
from ui.audit_log_viewer import AuditLogViewer

class MainWindow:
    """Main application window with navigation menu for the library management system."""
    
    def __init__(self):
        """Initialize the main application window."""
        self.root = tk.Tk()
        self.root.title("MiniBiblio - Bibliotheksverwaltung")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize database and services
        self.db_manager = None
        self.audit_service = None
        self._init_database()
        
        # Create main interface
        self._create_menu_bar()
        self._create_main_interface()
        
        # Load default view
        self._show_loans_view()
        
        # Center window on screen
        self._center_window()
    
    def _init_database(self):
        """Initialize the database connection and services."""
        try:
            self.db_manager = DatabaseManager("library.db")
            self.db_manager.initialize_database()
            self.audit_service = AuditService(self.db_manager)
        except Exception as e:
            messagebox.showerror("Datenbankfehler", 
                               f"Fehler beim Initialisieren der Datenbank:\n{str(e)}")
            self.root.quit()
    
    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Datenbank initialisieren", command=self._reinit_database)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self._on_closing)
        
        # Navigation menu
        nav_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigation", menu=nav_menu)
        nav_menu.add_command(label="Ausleihen", command=self._show_loans_view)
        nav_menu.add_command(label="Leser", command=self._show_readers_view)
        nav_menu.add_command(label="Bücher", command=self._show_books_view)
        nav_menu.add_command(label="Suchen", command=self._show_search_view)
        nav_menu.add_separator()
        nav_menu.add_command(label="Audit-Protokoll", command=self._show_audit_view)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Extras", menu=tools_menu)
        tools_menu.add_command(label="Statistiken", command=self._show_statistics)
        tools_menu.add_command(label="Überfällige Bücher", command=self._show_overdue_books)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über MiniBiblio", command=self._show_about)
    
    def _create_main_interface(self):
        """Create the main interface with toolbar and content area."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self._create_toolbar(main_container)
        
        # Content area
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self._create_status_bar(main_container)
    
    def _create_toolbar(self, parent):
        """Create the application toolbar."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Navigation buttons
        ttk.Button(toolbar, text="Ausleihen", command=self._show_loans_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Leser", command=self._show_readers_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Bücher", command=self._show_books_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Suchen", command=self._show_search_view).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Quick action buttons
        ttk.Button(toolbar, text="Buch ausleihen", command=self._quick_checkout).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Neuer Leser", command=self._quick_add_reader).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Neues Buch", command=self._quick_add_book).pack(side=tk.LEFT, padx=2)
        
        # Right side buttons
        ttk.Button(toolbar, text="Statistiken", command=self._show_statistics).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Aktualisieren", command=self._refresh_current_view).pack(side=tk.RIGHT, padx=2)
    
    def _create_status_bar(self, parent):
        """Create the status bar."""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label
        self.status_label = ttk.Label(self.status_bar, text="Bereit")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Database status
        self.db_status_label = ttk.Label(self.status_bar, text="Datenbank: Verbunden")
        self.db_status_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _clear_content_frame(self):
        """Clear the content frame for new view."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_loans_view(self):
        """Show the loans management view."""
        self._clear_content_frame()
        self.current_view = "loans"
        
        try:
            self.loans_view = ActiveLoansView(self.content_frame, self.db_manager)
            self._update_status("Ausleihen-Ansicht geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Ausleihen-Ansicht: {str(e)}")
    
    def _show_readers_view(self):
        """Show the readers management view."""
        self._clear_content_frame()
        self.current_view = "readers"
        
        try:
            self.readers_view = ReaderListView(self.content_frame, self.db_manager)
            self._update_status("Leser-Ansicht geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Leser-Ansicht: {str(e)}")
    
    def _show_books_view(self):
        """Show the books management view."""
        self._clear_content_frame()
        self.current_view = "books"
        
        try:
            self.books_view = BookListView(self.content_frame, self.db_manager)
            self._update_status("Bücher-Ansicht geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Bücher-Ansicht: {str(e)}")
    
    def _show_search_view(self):
        """Show the search interface."""
        self._clear_content_frame()
        self.current_view = "search"
        
        try:
            self.search_view = SearchInterface(self.content_frame, self.db_manager)
            self._update_status("Such-Ansicht geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Such-Ansicht: {str(e)}")
    
    def _show_audit_view(self):
        """Show the audit log viewer."""
        self._clear_content_frame()
        self.current_view = "audit"
        
        try:
            self.audit_view = AuditLogViewer(self.content_frame, self.db_manager)
            self._update_status("Audit-Protokoll geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Audit-Protokolls: {str(e)}")
    
    def _quick_checkout(self):
        """Quick book checkout action."""
        from ui.lending_operations import BookCheckoutDialog
        try:
            dialog = BookCheckoutDialog(self.root, self.db_manager, 
                                       on_success=self._on_checkout_success)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Ausleihe: {str(e)}")
    
    def _quick_add_reader(self):
        """Quick add reader action."""
        from ui.reader_management import ReaderRegistrationDialog
        try:
            dialog = ReaderRegistrationDialog(self.root, self.db_manager,
                                             on_success=self._on_reader_added)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen eines Lesers: {str(e)}")
    
    def _quick_add_book(self):
        """Quick add book action."""
        from ui.book_management import BookRegistrationDialog
        try:
            dialog = BookRegistrationDialog(self.root, self.db_manager,
                                           on_success=self._on_book_added)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen eines Buchs: {str(e)}")
    
    def _on_checkout_success(self, loan):
        """Callback for successful checkout."""
        self._update_status(f"Buch erfolgreich ausgeliehen")
        self._refresh_current_view()
    
    def _on_reader_added(self, reader):
        """Callback for successful reader addition."""
        self._update_status(f"Leser '{reader.name}' hinzugefügt")
        self._refresh_current_view()
    
    def _on_book_added(self, book):
        """Callback for successful book addition."""
        self._update_status(f"Buch '{book.title}' hinzugefügt")
        self._refresh_current_view()
    
    def _refresh_current_view(self):
        """Refresh the current view."""
        if hasattr(self, 'current_view'):
            if self.current_view == "loans":
                self._show_loans_view()
            elif self.current_view == "readers":
                self._show_readers_view()
            elif self.current_view == "books":
                self._show_books_view()
            elif self.current_view == "search":
                self._show_search_view()
    
    def _show_statistics(self):
        """Show library statistics."""
        try:
            from business.loan_service import LoanService
            loan_service = LoanService(self.db_manager)
            stats = loan_service.get_loan_statistics()
            
            # Create statistics window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Bibliotheksstatistiken")
            stats_window.geometry("500x600")
            stats_window.transient(self.root)
            
            # Statistics content
            main_frame = ttk.Frame(stats_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            ttk.Label(main_frame, text="Bibliotheksstatistiken", 
                     font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 20))
            
            # Basic statistics
            basic_frame = ttk.LabelFrame(main_frame, text="Allgemeine Statistiken", padding="10")
            basic_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(basic_frame, text=f"Gesamtanzahl Ausleihen: {stats['total_loans']}").pack(anchor=tk.W)
            ttk.Label(basic_frame, text=f"Aktive Ausleihen: {stats['active_loans']}").pack(anchor=tk.W)
            ttk.Label(basic_frame, text=f"Zurückgegebene Bücher: {stats['returned_loans']}").pack(anchor=tk.W)
            ttk.Label(basic_frame, text=f"Überfällige Bücher: {stats['overdue_loans']}").pack(anchor=tk.W)
            
            # Most active readers
            if stats['most_active_readers']:
                readers_frame = ttk.LabelFrame(main_frame, text="Aktivste Leser", padding="10")
                readers_frame.pack(fill=tk.X, pady=(0, 10))
                
                for i, reader in enumerate(stats['most_active_readers'][:5], 1):
                    ttk.Label(readers_frame, 
                             text=f"{i}. {reader['name']} ({reader['reader_number']}) - {reader['loan_count']} Ausleihen").pack(anchor=tk.W)
            
            # Most borrowed books
            if stats['most_borrowed_books']:
                books_frame = ttk.LabelFrame(main_frame, text="Meistgeliehene Bücher", padding="10")
                books_frame.pack(fill=tk.X, pady=(0, 10))
                
                for i, book in enumerate(stats['most_borrowed_books'][:5], 1):
                    ttk.Label(books_frame, 
                             text=f"{i}. {book['title']} ({book['book_number']}) - {book['loan_count']} Ausleihen").pack(anchor=tk.W)
            
            # Close button
            ttk.Button(main_frame, text="Schließen", 
                      command=stats_window.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Statistiken: {str(e)}")
    
    def _show_overdue_books(self):
        """Show overdue books window."""
        try:
            from business.loan_service import LoanService
            loan_service = LoanService(self.db_manager)
            overdue_loans = loan_service.get_overdue_loans(14)  # 14 days default
            
            # Create overdue books window
            overdue_window = tk.Toplevel(self.root)
            overdue_window.title("Überfällige Bücher")
            overdue_window.geometry("800x500")
            overdue_window.transient(self.root)
            
            # Content frame
            main_frame = ttk.Frame(overdue_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            ttk.Label(main_frame, text=f"Überfällige Bücher ({len(overdue_loans)} Einträge)", 
                     font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 20))
            
            if overdue_loans:
                # Treeview for overdue loans
                tree_frame = ttk.Frame(main_frame)
                tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
                
                columns = ("reader", "book", "borrow_date", "days_overdue")
                tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
                
                tree.heading("reader", text="Leser")
                tree.heading("book", text="Buch")
                tree.heading("borrow_date", text="Ausleihdatum")
                tree.heading("days_overdue", text="Tage überfällig")
                
                # Add overdue loans
                for loan in overdue_loans:
                    days_overdue = (date.today() - loan.borrow_date).days if loan.borrow_date else 0
                    tree.insert("", tk.END, values=(
                        loan.reader_name if hasattr(loan, 'reader_name') else "Unbekannt",
                        f"{loan.book_title} ({loan.book_number})" if hasattr(loan, 'book_title') else "Unbekannt",
                        loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else "",
                        days_overdue
                    ))
                
                # Scrollbar
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                ttk.Label(main_frame, text="Keine überfälligen Bücher gefunden!",
                         font=("TkDefaultFont", 12)).pack(pady=50)
            
            # Close button
            ttk.Button(main_frame, text="Schließen", 
                      command=overdue_window.destroy).pack()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der überfälligen Bücher: {str(e)}")
    
    def _reinit_database(self):
        """Reinitialize the database."""
        result = messagebox.askyesno("Datenbank initialisieren", 
                                   "Möchten Sie die Datenbank neu initialisieren?\n\n"
                                   "Dies erstellt die Tabellen neu, aber löscht keine vorhandenen Daten.")
        if result:
            try:
                self.db_manager.initialize_database()
                messagebox.showinfo("Erfolg", "Datenbank erfolgreich initialisiert.")
                self._update_status("Datenbank neu initialisiert")
                self._refresh_current_view()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Initialisieren der Datenbank: {str(e)}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """MiniBiblio - Bibliotheksverwaltung

Ein einfaches Bibliotheksverwaltungssystem für kleine Bibliotheken.

Funktionen:
• Leserdatenverwaltung
• Buchkatalog
• Ausleihe und Rückgabe
• Suchfunktionen
• Statistiken

Version: 1.0
Entwickelt mit Python und tkinter

🤖 Generated with Claude Code"""
        
        messagebox.showinfo("Über MiniBiblio", about_text)
    
    def _update_status(self, message):
        """Update the status bar message."""
        self.status_label.config(text=message)
        # Clear status after 5 seconds
        self.root.after(5000, lambda: self.status_label.config(text="Bereit"))
    
    def _on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Beenden", "Möchten Sie MiniBiblio wirklich beenden?"):
            if self.db_manager:
                self.db_manager.disconnect()
            self.root.quit()
    
    def run(self):
        """Start the application."""
        # Set window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main function to start the application."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        # Fallback error handling
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Kritischer Fehler", 
                           f"Ein kritischer Fehler ist aufgetreten:\n{str(e)}")
        root.quit()

if __name__ == "__main__":
    main()