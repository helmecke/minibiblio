import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from datetime import date
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.loan_service import LoanService
from business.reader_service import ReaderService
from business.book_service import BookService
from business.audit_service import AuditService
from database.models import Loan, Reader, Book

class BookCheckoutDialog:
    """Dialog for checking out books to readers."""
    
    def __init__(self, parent, db_manager: DatabaseManager, on_success: Optional[Callable] = None):
        """
        Initialize book checkout dialog.
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
            on_success: Callback function called when checkout is successful
        """
        self.parent = parent
        self.audit_service = AuditService(db_manager)
        self.loan_service = LoanService(db_manager, self.audit_service)
        self.reader_service = ReaderService(db_manager)
        self.book_service = BookService(db_manager)
        self.on_success = on_success
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Buch ausleihen")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self._center_dialog()
        
        # Create form
        self._create_form()
        
        # Load data
        self._load_readers()
        self._load_available_books()
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate dialog position
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_form(self):
        """Create the checkout form."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Buch ausleihen", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Reader selection
        reader_frame = ttk.LabelFrame(main_frame, text="Leser auswählen", padding="10")
        reader_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        reader_frame.columnconfigure(1, weight=1)
        
        # Reader search
        ttk.Label(reader_frame, text="Suchen:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reader_search_entry = ttk.Entry(reader_frame, width=30)
        self.reader_search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.reader_search_entry.bind('<KeyRelease>', self._on_reader_search)
        
        # Reader list
        reader_list_frame = ttk.Frame(reader_frame)
        reader_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        reader_list_frame.columnconfigure(0, weight=1)
        
        # Reader treeview
        reader_columns = ("number", "name", "address")
        self.reader_tree = ttk.Treeview(reader_list_frame, columns=reader_columns, show="headings", height=6)
        
        self.reader_tree.heading("number", text="Nr.")
        self.reader_tree.heading("name", text="Name")
        self.reader_tree.heading("address", text="Adresse")
        
        self.reader_tree.column("number", width=60, minwidth=50)
        self.reader_tree.column("name", width=150, minwidth=120)
        self.reader_tree.column("address", width=200, minwidth=150)
        
        # Reader scrollbar
        reader_scrollbar = ttk.Scrollbar(reader_list_frame, orient=tk.VERTICAL, command=self.reader_tree.yview)
        self.reader_tree.configure(yscrollcommand=reader_scrollbar.set)
        
        self.reader_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reader_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind reader selection
        self.reader_tree.bind('<<TreeviewSelect>>', self._on_reader_select)
        
        # Book selection
        book_frame = ttk.LabelFrame(main_frame, text="Verfügbares Buch auswählen", padding="10")
        book_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        book_frame.columnconfigure(1, weight=1)
        
        # Book search
        ttk.Label(book_frame, text="Suchen:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.book_search_entry = ttk.Entry(book_frame, width=30)
        self.book_search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.book_search_entry.bind('<KeyRelease>', self._on_book_search)
        
        # Book list
        book_list_frame = ttk.Frame(book_frame)
        book_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        book_list_frame.columnconfigure(0, weight=1)
        
        # Book treeview
        book_columns = ("number", "title", "author")
        self.book_tree = ttk.Treeview(book_list_frame, columns=book_columns, show="headings", height=6)
        
        self.book_tree.heading("number", text="Buchnummer")
        self.book_tree.heading("title", text="Titel")
        self.book_tree.heading("author", text="Autor")
        
        self.book_tree.column("number", width=100, minwidth=80)
        self.book_tree.column("title", width=200, minwidth=150)
        self.book_tree.column("author", width=150, minwidth=120)
        
        # Book scrollbar
        book_scrollbar = ttk.Scrollbar(book_list_frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=book_scrollbar.set)
        
        self.book_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        book_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind book selection
        self.book_tree.bind('<<TreeviewSelect>>', self._on_book_select)
        
        # Selected items display
        selection_frame = ttk.LabelFrame(main_frame, text="Ausgewählte Ausleihe", padding="10")
        selection_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.selection_text = tk.Text(selection_frame, height=3, state=tk.DISABLED)
        self.selection_text.pack(fill=tk.X)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Checkout button
        self.checkout_button = ttk.Button(button_frame, text="Ausleihen", 
                                         command=self._checkout_book, state=tk.DISABLED)
        self.checkout_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Abbrechen", 
                                  command=self._cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to checkout
        self.dialog.bind('<Return>', lambda event: self._checkout_book() if self.checkout_button['state'] == tk.NORMAL else None)
        self.dialog.bind('<Escape>', lambda event: self._cancel())
        
        # Selected items
        self.selected_reader = None
        self.selected_book = None
    
    def _load_readers(self):
        """Load all readers into the reader tree."""
        try:
            # Clear existing items
            for item in self.reader_tree.get_children():
                self.reader_tree.delete(item)
            
            # Load readers
            readers = self.reader_service.get_all_readers()
            
            # Add readers to treeview
            for reader in readers:
                self.reader_tree.insert("", tk.END, values=(
                    reader.reader_number,
                    reader.name,
                    reader.address.replace('\n', ' ')  # Single line for display
                ), tags=(reader.id,))
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Leser: {str(e)}")
    
    def _load_available_books(self):
        """Load available books into the book tree."""
        try:
            # Clear existing items
            for item in self.book_tree.get_children():
                self.book_tree.delete(item)
            
            # Load available books
            books = self.book_service.get_available_books()
            
            # Add books to treeview
            for book in books:
                self.book_tree.insert("", tk.END, values=(
                    book.book_number,
                    book.title,
                    book.author or ""
                ), tags=(book.id,))
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Bücher: {str(e)}")
    
    def _on_reader_search(self, event):
        """Handle reader search input."""
        search_term = self.reader_search_entry.get().strip()
        
        try:
            # Clear existing items
            for item in self.reader_tree.get_children():
                self.reader_tree.delete(item)
            
            if search_term:
                # Search readers
                readers = self.reader_service.search_readers_by_name(search_term)
            else:
                # Load all readers
                readers = self.reader_service.get_all_readers()
            
            # Add readers to treeview
            for reader in readers:
                self.reader_tree.insert("", tk.END, values=(
                    reader.reader_number,
                    reader.name,
                    reader.address.replace('\n', ' ')
                ), tags=(reader.id,))
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Lesersuche: {str(e)}")
    
    def _on_book_search(self, event):
        """Handle book search input."""
        search_term = self.book_search_entry.get().strip()
        
        try:
            # Clear existing items
            for item in self.book_tree.get_children():
                self.book_tree.delete(item)
            
            if search_term:
                # Search books and filter for available ones
                all_books = self.book_service.search_books(search_term)
                books = [book for book in all_books if self.loan_service.is_book_available(book.id)]
            else:
                # Load all available books
                books = self.book_service.get_available_books()
            
            # Add books to treeview
            for book in books:
                self.book_tree.insert("", tk.END, values=(
                    book.book_number,
                    book.title,
                    book.author or ""
                ), tags=(book.id,))
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Buchsuche: {str(e)}")
    
    def _on_reader_select(self, event):
        """Handle reader selection."""
        selection = self.reader_tree.selection()
        if selection:
            item = self.reader_tree.item(selection[0])
            reader_id = int(item['tags'][0])
            try:
                self.selected_reader = self.reader_service.get_reader_by_id(reader_id)
                self._update_selection_display()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Lesers: {str(e)}")
    
    def _on_book_select(self, event):
        """Handle book selection."""
        selection = self.book_tree.selection()
        if selection:
            item = self.book_tree.item(selection[0])
            book_id = int(item['tags'][0])
            try:
                self.selected_book = self.book_service.get_book_by_id(book_id)
                self._update_selection_display()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Buchs: {str(e)}")
    
    def _update_selection_display(self):
        """Update the selection display and enable/disable checkout button."""
        self.selection_text.config(state=tk.NORMAL)
        self.selection_text.delete(1.0, tk.END)
        
        if self.selected_reader and self.selected_book:
            text = f"Leser: {self.selected_reader.name} (Nr. {self.selected_reader.reader_number})\n"
            text += f"Buch: {self.selected_book.title} ({self.selected_book.book_number})\n"
            text += f"Ausleihdatum: {date.today().strftime('%d.%m.%Y')}"
            
            self.selection_text.insert(1.0, text)
            self.checkout_button.config(state=tk.NORMAL)
        elif self.selected_reader:
            text = f"Leser: {self.selected_reader.name} (Nr. {self.selected_reader.reader_number})\n"
            text += "Buch: Noch nicht ausgewählt"
            self.selection_text.insert(1.0, text)
            self.checkout_button.config(state=tk.DISABLED)
        elif self.selected_book:
            text = f"Leser: Noch nicht ausgewählt\n"
            text += f"Buch: {self.selected_book.title} ({self.selected_book.book_number})"
            self.selection_text.insert(1.0, text)
            self.checkout_button.config(state=tk.DISABLED)
        else:
            self.selection_text.insert(1.0, "Bitte wählen Sie einen Leser und ein Buch aus.")
            self.checkout_button.config(state=tk.DISABLED)
        
        self.selection_text.config(state=tk.DISABLED)
    
    def _checkout_book(self):
        """Process the book checkout."""
        if not self.selected_reader or not self.selected_book:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Leser und ein Buch aus.")
            return
        
        try:
            # Check out the book
            loan = self.loan_service.check_out_book(
                reader_id=self.selected_reader.id,
                book_id=self.selected_book.id,
                borrow_date=date.today()
            )
            
            # Show success message
            messagebox.showinfo("Erfolg", 
                              f"Buch erfolgreich ausgeliehen!\n\n"
                              f"Leser: {self.selected_reader.name}\n"
                              f"Buch: {self.selected_book.title}\n"
                              f"Ausleihdatum: {loan.borrow_date.strftime('%d.%m.%Y')}")
            
            # Store result and call success callback
            self.result = loan
            if self.on_success:
                self.on_success(loan)
            
            # Close dialog
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Validierungsfehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Ausleihen: {str(e)}")
    
    def _cancel(self):
        """Cancel checkout and close dialog."""
        self.dialog.destroy()

class ActiveLoansView:
    """View for displaying active loans and processing returns."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """
        Initialize active loans view.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.audit_service = AuditService(db_manager)
        self.loan_service = LoanService(db_manager, self.audit_service)
        self.reader_service = ReaderService(db_manager)
        self.book_service = BookService(db_manager)
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_widgets()
        self._load_active_loans()
    
    def _create_widgets(self):
        """Create the active loans view widgets."""
        # Title and controls frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(top_frame, text="Aktive Ausleihen", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Checkout button
        checkout_button = ttk.Button(button_frame, text="Neues Buch ausleihen", 
                                    command=self._checkout_book)
        checkout_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(button_frame, text="Aktualisieren", 
                                   command=self._load_active_loans)
        refresh_button.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Suchen:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Filter frame
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="active")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["active", "overdue", "all"], 
                                   state="readonly", width=12)
        filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("reader", "book", "borrow_date", "due_date", "days_borrowed", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        self.tree.heading("reader", text="Leser")
        self.tree.heading("book", text="Buch")
        self.tree.heading("borrow_date", text="Ausleihdatum")
        self.tree.heading("due_date", text="Fälligkeitsdatum")
        self.tree.heading("days_borrowed", text="Tage")
        self.tree.heading("status", text="Status")
        
        self.tree.column("reader", width=180, minwidth=130)
        self.tree.column("book", width=220, minwidth=180)
        self.tree.column("borrow_date", width=110, minwidth=90)
        self.tree.column("due_date", width=110, minwidth=90)
        self.tree.column("days_borrowed", width=70, minwidth=50)
        self.tree.column("status", width=90, minwidth=70)
        
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
        
        # Context menu for return
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Buch zurückgeben", command=self._return_selected_book)
        self.context_menu.add_command(label="Ausleihe verlängern", command=self._extend_selected_loan)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Details anzeigen", command=self._view_loan_details)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _checkout_book(self):
        """Show checkout dialog."""
        dialog = BookCheckoutDialog(self.parent, self.db_manager, 
                                   on_success=self._on_checkout_success)
    
    def _on_checkout_success(self, loan: Loan):
        """Callback when a book is successfully checked out."""
        self._load_active_loans()
    
    def _load_active_loans(self):
        """Load and display active loans based on current filter."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            filter_value = self.filter_var.get()
            
            # Load loans based on filter
            if filter_value == "overdue":
                loans = self.loan_service.get_overdue_loans()
            elif filter_value == "all":
                loans = self.loan_service.get_loan_history()
            else:  # active
                loans = self.loan_service.get_active_loans()
            
            # Add loans to treeview
            for loan in loans:
                # Calculate days borrowed
                if loan.borrow_date:
                    days_borrowed = (date.today() - loan.borrow_date).days
                else:
                    days_borrowed = 0
                
                # Determine status
                if loan.status == "returned":
                    status = "Zurückgegeben"
                elif loan.due_date and date.today() > loan.due_date:
                    status = "Überfällig"
                else:
                    status = "Ausgeliehen"
                
                # Format reader and book info
                reader_info = f"{loan.reader_name}" if hasattr(loan, 'reader_name') and loan.reader_name else "Unbekannt"
                book_info = f"{loan.book_title}" if hasattr(loan, 'book_title') and loan.book_title else "Unbekannt"
                if hasattr(loan, 'book_number') and loan.book_number:
                    book_info += f" ({loan.book_number})"
                
                self.tree.insert("", tk.END, values=(
                    reader_info,
                    book_info,
                    loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else "",
                    loan.due_date.strftime('%d.%m.%Y') if loan.due_date else "",
                    days_borrowed,
                    status
                ), tags=(loan.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Ausleihen: {str(e)}")
    
    def _on_search(self, event):
        """Handle search input."""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._load_active_loans()
            return
        
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Search loans by reader name and book title
            reader_loans = self.loan_service.search_loans_by_reader_name(search_term)
            book_loans = self.loan_service.search_loans_by_book_title(search_term)
            
            # Combine and deduplicate
            all_loans = reader_loans + book_loans
            seen_ids = set()
            unique_loans = []
            for loan in all_loans:
                if loan.id not in seen_ids:
                    unique_loans.append(loan)
                    seen_ids.add(loan.id)
            
            # Add matching loans to treeview
            for loan in unique_loans:
                days_borrowed = (date.today() - loan.borrow_date).days if loan.borrow_date else 0
                
                if loan.status == "returned":
                    status = "Zurückgegeben"
                elif loan.due_date and date.today() > loan.due_date:
                    status = "Überfällig"
                else:
                    status = "Ausgeliehen"
                
                reader_info = f"{loan.reader_name}" if hasattr(loan, 'reader_name') and loan.reader_name else "Unbekannt"
                book_info = f"{loan.book_title}" if hasattr(loan, 'book_title') and loan.book_title else "Unbekannt"
                if hasattr(loan, 'book_number') and loan.book_number:
                    book_info += f" ({loan.book_number})"
                
                self.tree.insert("", tk.END, values=(
                    reader_info,
                    book_info,
                    loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else "",
                    loan.due_date.strftime('%d.%m.%Y') if loan.due_date else "",
                    days_borrowed,
                    status
                ), tags=(loan.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Suche: {str(e)}")
    
    def _on_filter_change(self, event):
        """Handle filter change."""
        self._load_active_loans()
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_loan_id(self) -> Optional[int]:
        """Get the ID of the currently selected loan."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return int(item['tags'][0])
        return None
    
    def _on_double_click(self, event):
        """Handle double-click on loan item."""
        loan_id = self._get_selected_loan_id()
        if loan_id:
            self._return_book(loan_id)
    
    def _return_selected_book(self):
        """Return selected book."""
        loan_id = self._get_selected_loan_id()
        if loan_id:
            self._return_book(loan_id)
    
    def _return_book(self, loan_id: int):
        """Process book return."""
        try:
            # Get loan details
            loan = self.loan_service.get_loan_by_id(loan_id)
            if not loan:
                messagebox.showerror("Fehler", "Ausleihe nicht gefunden.")
                return
            
            if loan.status == "returned":
                messagebox.showinfo("Information", "Dieses Buch wurde bereits zurückgegeben.")
                return
            
            # Confirm return
            result = messagebox.askyesno("Buch zurückgeben", 
                                       f"Möchten Sie das Buch zurückgeben?\n\n"
                                       f"Leser: {loan.reader_name}\n"
                                       f"Buch: {loan.book_title}\n"
                                       f"Ausgeliehen am: {loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else 'Unbekannt'}")
            
            if result:
                # Process return
                returned_loan = self.loan_service.return_book(loan_id, date.today())
                
                messagebox.showinfo("Erfolg", 
                                  f"Buch erfolgreich zurückgegeben!\n\n"
                                  f"Rückgabedatum: {returned_loan.return_date.strftime('%d.%m.%Y')}")
                
                # Refresh the list
                self._load_active_loans()
                
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Rückgabe: {str(e)}")
    
    def _extend_selected_loan(self):
        """Extend selected loan."""
        loan_id = self._get_selected_loan_id()
        if loan_id:
            self._extend_loan(loan_id)
    
    def _extend_loan(self, loan_id: int):
        """Process loan extension."""
        try:
            # Get loan details
            loan = self.loan_service.get_loan_by_id(loan_id)
            if not loan:
                messagebox.showerror("Fehler", "Ausleihe nicht gefunden.")
                return
            
            if loan.status == "returned":
                messagebox.showinfo("Information", "Dieses Buch wurde bereits zurückgegeben und kann nicht verlängert werden.")
                return
            
            # Create extension dialog
            extension_dialog = tk.Toplevel(self.parent)
            extension_dialog.title("Ausleihe verlängern")
            extension_dialog.geometry("400x300")
            extension_dialog.resizable(False, False)
            extension_dialog.transient(self.parent)
            extension_dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(extension_dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Loan info
            info_frame = ttk.LabelFrame(main_frame, text="Ausleiheinformationen", padding="10")
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(info_frame, text=f"Leser: {loan.reader_name}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Buch: {loan.book_title} ({loan.book_number})").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Ausleihdatum: {loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else 'Unbekannt'}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Aktuell fällig am: {loan.due_date.strftime('%d.%m.%Y') if loan.due_date else 'Unbekannt'}").pack(anchor=tk.W)
            
            # Extension options
            extension_frame = ttk.LabelFrame(main_frame, text="Verlängerung", padding="10")
            extension_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(extension_frame, text="Verlängerung um Tage:").pack(anchor=tk.W)
            
            days_var = tk.StringVar(value="14")
            days_entry = ttk.Entry(extension_frame, textvariable=days_var, width=10)
            days_entry.pack(anchor=tk.W, pady=5)
            
            # Calculate new due date preview
            preview_label = ttk.Label(extension_frame, text="")
            preview_label.pack(anchor=tk.W, pady=5)
            
            def update_preview(*args):
                try:
                    days = int(days_var.get())
                    if loan.due_date:
                        from datetime import timedelta
                        new_due_date = loan.due_date + timedelta(days=days)
                        preview_label.config(text=f"Neue Fälligkeit: {new_due_date.strftime('%d.%m.%Y')}")
                    else:
                        preview_label.config(text="")
                except ValueError:
                    preview_label.config(text="Ungültige Eingabe")
            
            days_var.trace('w', update_preview)
            update_preview()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def confirm_extension():
                try:
                    days = int(days_var.get())
                    if days <= 0:
                        messagebox.showerror("Fehler", "Anzahl Tage muss positiv sein.")
                        return
                    
                    # Process extension
                    extended_loan = self.loan_service.extend_loan(loan_id, days)
                    
                    messagebox.showinfo("Erfolg", 
                                      f"Ausleihe erfolgreich verlängert!\n\n"
                                      f"Neue Fälligkeit: {extended_loan.due_date.strftime('%d.%m.%Y')}")
                    
                    extension_dialog.destroy()
                    
                    # Refresh the list
                    self._load_active_loans()
                    
                except ValueError as e:
                    if "positiv sein" not in str(e):
                        messagebox.showerror("Fehler", "Ungültige Eingabe für Anzahl Tage.")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler bei der Verlängerung: {str(e)}")
            
            ttk.Button(button_frame, text="Verlängern", command=confirm_extension).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Abbrechen", command=extension_dialog.destroy).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Verlängerung: {str(e)}")
    
    def _view_loan_details(self):
        """View details of selected loan."""
        loan_id = self._get_selected_loan_id()
        if loan_id:
            try:
                loan = self.loan_service.get_loan_by_id(loan_id)
                if loan:
                    # Create details window
                    details_window = tk.Toplevel(self.parent)
                    details_window.title("Ausleihe Details")
                    details_window.geometry("400x300")
                    
                    # Loan info
                    info_frame = ttk.LabelFrame(details_window, text="Ausleiheinformationen", padding="10")
                    info_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    ttk.Label(info_frame, text=f"Leser: {loan.reader_name}").pack(anchor=tk.W)
                    ttk.Label(info_frame, text=f"Buch: {loan.book_title} ({loan.book_number})").pack(anchor=tk.W)
                    ttk.Label(info_frame, text=f"Ausleihdatum: {loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else 'Unbekannt'}").pack(anchor=tk.W)
                    
                    if loan.due_date:
                        ttk.Label(info_frame, text=f"Fälligkeitsdatum: {loan.due_date.strftime('%d.%m.%Y')}").pack(anchor=tk.W)
                    
                    if loan.return_date:
                        ttk.Label(info_frame, text=f"Rückgabedatum: {loan.return_date.strftime('%d.%m.%Y')}").pack(anchor=tk.W)
                    else:
                        days_borrowed = (date.today() - loan.borrow_date).days if loan.borrow_date else 0
                        ttk.Label(info_frame, text=f"Tage ausgeliehen: {days_borrowed}").pack(anchor=tk.W)
                        
                        if loan.due_date:
                            days_until_due = (loan.due_date - date.today()).days
                            if days_until_due < 0:
                                ttk.Label(info_frame, text=f"Überfällig seit: {abs(days_until_due)} Tagen", foreground="red").pack(anchor=tk.W)
                            else:
                                ttk.Label(info_frame, text=f"Fällig in: {days_until_due} Tagen").pack(anchor=tk.W)
                    
                    ttk.Label(info_frame, text=f"Status: {'Zurückgegeben' if loan.status == 'returned' else 'Ausgeliehen'}").pack(anchor=tk.W)
                    
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Details: {str(e)}")

# Example usage/test function
def main():
    """Test the lending operations UI."""
    root = tk.Tk()
    root.title("Lending Operations Test")
    root.geometry("1000x700")
    
    # Initialize database
    db_manager = DatabaseManager("test_library.db")
    db_manager.initialize_database()
    
    # Create active loans view
    loans_view = ActiveLoansView(root, db_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()