import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.book_service import BookService
from database.models import Book

class BookRegistrationDialog:
    """Dialog for registering new library books."""
    
    def __init__(self, parent, db_manager: DatabaseManager, on_success: Optional[Callable] = None):
        """
        Initialize book registration dialog.
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
            on_success: Callback function called when book is successfully created
        """
        self.parent = parent
        self.book_service = BookService(db_manager)
        self.on_success = on_success
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Neues Buch registrieren")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self._center_dialog()
        
        # Create form
        self._create_form()
        
        # Focus on book number field
        self.book_number_entry.focus()
    
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
        """Create the registration form."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Neues Buch registrieren", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Book Number field
        ttk.Label(main_frame, text="Buchnummer*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.book_number_entry = ttk.Entry(main_frame, width=20)
        self.book_number_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 5))
        
        # Auto-generate button
        auto_gen_button = ttk.Button(main_frame, text="Auto", width=8,
                                    command=self._auto_generate_number)
        auto_gen_button.grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # Title field
        ttk.Label(main_frame, text="Titel*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=40)
        self.title_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Author field
        ttk.Label(main_frame, text="Autor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(main_frame, width=40)
        self.author_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # ISBN field
        ttk.Label(main_frame, text="ISBN:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.isbn_entry = ttk.Entry(main_frame, width=40)
        self.isbn_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Publication Year field
        ttk.Label(main_frame, text="Erscheinungsjahr:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.year_entry = ttk.Entry(main_frame, width=10)
        self.year_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Add validation for year entry (numbers only)
        year_vcmd = (self.dialog.register(self._validate_year), '%P')
        self.year_entry.config(validate='key', validatecommand=year_vcmd)
        
        # Required fields note
        note_label = ttk.Label(main_frame, text="* Pflichtfelder", 
                              font=("TkDefaultFont", 8), foreground="gray")
        note_label.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(20, 0))
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Speichern", 
                                     command=self._save_book)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Abbrechen", 
                                  command=self._cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self._save_book())
        self.dialog.bind('<Escape>', lambda event: self._cancel())
    
    def _validate_year(self, value):
        """Validate publication year input (numbers only)."""
        if value == "":
            return True
        try:
            year = int(value)
            return 0 <= year <= 9999
        except ValueError:
            return False
    
    def _auto_generate_number(self):
        """Auto-generate book number."""
        try:
            book_number = self.book_service.generate_book_number("B")
            self.book_number_entry.delete(0, tk.END)
            self.book_number_entry.insert(0, book_number)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Generieren der Buchnummer: {str(e)}")
    
    def _save_book(self):
        """Save the new book."""
        try:
            # Get form data
            book_number = self.book_number_entry.get().strip()
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            isbn = self.isbn_entry.get().strip()
            year_str = self.year_entry.get().strip()
            
            # Validate required fields
            if not book_number:
                messagebox.showerror("Fehler", "Buchnummer ist erforderlich.")
                self.book_number_entry.focus()
                return
            
            if not title:
                messagebox.showerror("Fehler", "Titel ist erforderlich.")
                self.title_entry.focus()
                return
            
            # Parse publication year
            publication_year = None
            if year_str:
                try:
                    publication_year = int(year_str)
                except ValueError:
                    messagebox.showerror("Fehler", "Erscheinungsjahr muss eine Zahl sein.")
                    self.year_entry.focus()
                    return
            
            # Create book
            book = self.book_service.create_book(
                book_number=book_number,
                title=title,
                author=author if author else None,
                isbn=isbn if isbn else None,
                publication_year=publication_year
            )
            
            # Show success message
            messagebox.showinfo("Erfolg", 
                              f"Buch erfolgreich registriert!\n"
                              f"Buchnummer: {book.book_number}\n"
                              f"Titel: {book.title}")
            
            # Store result and call success callback
            self.result = book
            if self.on_success:
                self.on_success(book)
            
            # Close dialog
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Validierungsfehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def _cancel(self):
        """Cancel registration and close dialog."""
        self.dialog.destroy()

class BookListView:
    """View for displaying and managing list of books."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """
        Initialize book list view.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
        """
        self.parent = parent
        self.book_service = BookService(db_manager)
        self.db_manager = db_manager
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_widgets()
        self._load_books()
    
    def _create_widgets(self):
        """Create the list view widgets."""
        # Title and controls frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(top_frame, text="Buchkatalog", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Add book button
        add_button = ttk.Button(button_frame, text="Neues Buch", 
                               command=self._add_book)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(button_frame, text="Aktualisieren", 
                                   command=self._load_books)
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
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["all", "available", "borrowed"], 
                                   state="readonly", width=12)
        filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("number", "title", "author", "isbn", "year", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        self.tree.heading("number", text="Buchnummer")
        self.tree.heading("title", text="Titel")
        self.tree.heading("author", text="Autor")
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("year", text="Jahr")
        self.tree.heading("status", text="Status")
        
        self.tree.column("number", width=100, minwidth=80)
        self.tree.column("title", width=250, minwidth=200)
        self.tree.column("author", width=180, minwidth=150)
        self.tree.column("isbn", width=130, minwidth=100)
        self.tree.column("year", width=70, minwidth=50)
        self.tree.column("status", width=100, minwidth=80)
        
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
        
        # Context menu for edit/delete
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Details anzeigen", command=self._view_selected_book)
        self.context_menu.add_command(label="Bearbeiten", command=self._edit_selected_book)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Löschen", command=self._delete_selected_book)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _add_book(self):
        """Show add book dialog."""
        dialog = BookRegistrationDialog(self.parent, self.db_manager, 
                                       on_success=self._on_book_added)
    
    def _on_book_added(self, book: Book):
        """Callback when a book is successfully added."""
        self._load_books()
    
    def _load_books(self):
        """Load and display books based on current filter."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            filter_value = self.filter_var.get()
            
            # Load books based on filter
            if filter_value == "available":
                books = self.book_service.get_available_books()
                book_status = {}
                for book in books:
                    book_status[book.id] = "Verfügbar"
            elif filter_value == "borrowed":
                borrowed_data = self.book_service.get_borrowed_books()
                books = [item['book'] for item in borrowed_data]
                book_status = {}
                for item in borrowed_data:
                    book_status[item['book'].id] = f"Ausgeliehen an {item['reader_name']}"
            else:  # all
                books = self.book_service.get_all_books()
                # Get status for each book
                borrowed_books = self.book_service.get_borrowed_books()
                borrowed_ids = {item['book'].id for item in borrowed_books}
                book_status = {}
                for book in books:
                    if book.id in borrowed_ids:
                        reader_info = next(item for item in borrowed_books if item['book'].id == book.id)
                        book_status[book.id] = f"Ausgeliehen an {reader_info['reader_name']}"
                    else:
                        book_status[book.id] = "Verfügbar"
            
            # Add books to treeview
            for book in books:
                self.tree.insert("", tk.END, values=(
                    book.book_number,
                    book.title,
                    book.author or "",
                    book.isbn or "",
                    book.publication_year or "",
                    book_status.get(book.id, "")
                ), tags=(book.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Bücher: {str(e)}")
    
    def _on_search(self, event):
        """Handle search input."""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._load_books()
            return
        
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Search books
            books = self.book_service.search_books(search_term)
            
            # Get status for filtered books
            borrowed_books = self.book_service.get_borrowed_books()
            borrowed_ids = {item['book'].id for item in borrowed_books}
            
            # Add matching books to treeview
            for book in books:
                if book.id in borrowed_ids:
                    reader_info = next(item for item in borrowed_books if item['book'].id == book.id)
                    status = f"Ausgeliehen an {reader_info['reader_name']}"
                else:
                    status = "Verfügbar"
                
                self.tree.insert("", tk.END, values=(
                    book.book_number,
                    book.title,
                    book.author or "",
                    book.isbn or "",
                    book.publication_year or "",
                    status
                ), tags=(book.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Suche: {str(e)}")
    
    def _on_filter_change(self, event):
        """Handle filter change."""
        self._load_books()
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_book_id(self) -> Optional[int]:
        """Get the ID of the currently selected book."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return int(item['tags'][0])
        return None
    
    def _on_double_click(self, event):
        """Handle double-click on book item."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            book_id = int(item['tags'][0])
            self._show_book_details(book_id)
    
    def _view_selected_book(self):
        """View details of selected book."""
        book_id = self._get_selected_book_id()
        if book_id:
            self._show_book_details(book_id)
    
    def _edit_selected_book(self):
        """Edit selected book."""
        book_id = self._get_selected_book_id()
        if book_id:
            try:
                book = self.book_service.get_book_by_id(book_id)
                if book:
                    dialog = BookEditDialog(self.parent, self.db_manager, book, 
                                          on_success=self._on_book_updated)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Buchs: {str(e)}")
    
    def _delete_selected_book(self):
        """Delete selected book."""
        book_id = self._get_selected_book_id()
        if book_id:
            try:
                book = self.book_service.get_book_by_id(book_id)
                if book:
                    # Confirm deletion
                    result = messagebox.askyesno("Buch löschen", 
                                               f"Sind Sie sicher, dass Sie das Buch '{book.title}' löschen möchten?\n\n"
                                               "Diese Aktion kann nicht rückgängig gemacht werden.")
                    if result:
                        self.book_service.delete_book(book_id)
                        messagebox.showinfo("Erfolg", "Buch wurde erfolgreich gelöscht.")
                        self._load_books()
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")
    
    def _on_book_updated(self, book: Book):
        """Callback when a book is successfully updated."""
        self._load_books()
    
    def _show_book_details(self, book_id: int):
        """Show detailed book information."""
        try:
            book_info = self.book_service.get_book_with_loans(book_id)
            if book_info:
                book = book_info['book']
                loans = book_info['loans']
                
                # Create details window
                details_window = tk.Toplevel(self.parent)
                details_window.title(f"Buch Details - {book.title}")
                details_window.geometry("600x450")
                
                # Book info
                info_frame = ttk.LabelFrame(details_window, text="Buchinformationen", padding="10")
                info_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(info_frame, text=f"Buchnummer: {book.book_number}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Titel: {book.title}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Autor: {book.author or 'Nicht angegeben'}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"ISBN: {book.isbn or 'Nicht angegeben'}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Erscheinungsjahr: {book.publication_year or 'Nicht angegeben'}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Status: {'Verfügbar' if book_info['is_available'] else 'Ausgeliehen'}").pack(anchor=tk.W)
                
                # Loan history
                loans_frame = ttk.LabelFrame(details_window, text=f"Ausleihhistorie ({len(loans)} Einträge)", padding="10")
                loans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                if loans:
                    # Create treeview for loans
                    loan_columns = ("reader", "borrow_date", "return_date", "status")
                    loan_tree = ttk.Treeview(loans_frame, columns=loan_columns, show="headings", height=10)
                    
                    loan_tree.heading("reader", text="Leser")
                    loan_tree.heading("borrow_date", text="Ausgeliehen")
                    loan_tree.heading("return_date", text="Zurückgegeben")
                    loan_tree.heading("status", text="Status")
                    
                    for loan in loans:
                        loan_tree.insert("", tk.END, values=(
                            f"{loan['reader_name']} ({loan['reader_number']})",
                            loan['borrow_date'] or "",
                            loan['return_date'] or "",
                            "Ausgeliehen" if loan['status'] == 'borrowed' else "Zurückgegeben"
                        ))
                    
                    loan_tree.pack(fill=tk.BOTH, expand=True)
                else:
                    ttk.Label(loans_frame, text="Keine Ausleihhistorie vorhanden.").pack()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Details: {str(e)}")

class BookEditDialog:
    """Dialog for editing existing library books."""
    
    def __init__(self, parent, db_manager: DatabaseManager, book: Book, on_success: Optional[Callable] = None):
        """
        Initialize book edit dialog.
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
            book: Book object to edit
            on_success: Callback function called when book is successfully updated
        """
        self.parent = parent
        self.book_service = BookService(db_manager)
        self.book = book
        self.on_success = on_success
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Buch bearbeiten - {book.title}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self._center_dialog()
        
        # Create form
        self._create_form()
        
        # Focus on title field
        self.title_entry.focus()
    
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
        """Create the edit form."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Buch bearbeiten", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Book Number field
        ttk.Label(main_frame, text="Buchnummer*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.book_number_entry = ttk.Entry(main_frame, width=30)
        self.book_number_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.book_number_entry.insert(0, self.book.book_number)
        
        # Title field
        ttk.Label(main_frame, text="Titel*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=30)
        self.title_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.title_entry.insert(0, self.book.title)
        
        # Author field
        ttk.Label(main_frame, text="Autor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(main_frame, width=30)
        self.author_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.author_entry.insert(0, self.book.author or "")
        
        # ISBN field
        ttk.Label(main_frame, text="ISBN:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.isbn_entry = ttk.Entry(main_frame, width=30)
        self.isbn_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.isbn_entry.insert(0, self.book.isbn or "")
        
        # Publication Year field
        ttk.Label(main_frame, text="Erscheinungsjahr:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.year_entry = ttk.Entry(main_frame, width=10)
        self.year_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.year_entry.insert(0, str(self.book.publication_year) if self.book.publication_year else "")
        
        # Add validation for year entry (numbers only)
        year_vcmd = (self.dialog.register(self._validate_year), '%P')
        self.year_entry.config(validate='key', validatecommand=year_vcmd)
        
        # Required fields note
        note_label = ttk.Label(main_frame, text="* Pflichtfelder", 
                              font=("TkDefaultFont", 8), foreground="gray")
        note_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Speichern", 
                                     command=self._save_book)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Abbrechen", 
                                  command=self._cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self._save_book())
        self.dialog.bind('<Escape>', lambda event: self._cancel())
    
    def _validate_year(self, value):
        """Validate publication year input (numbers only)."""
        if value == "":
            return True
        try:
            year = int(value)
            return 0 <= year <= 9999
        except ValueError:
            return False
    
    def _save_book(self):
        """Save the updated book."""
        try:
            # Get form data
            book_number = self.book_number_entry.get().strip()
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            isbn = self.isbn_entry.get().strip()
            year_str = self.year_entry.get().strip()
            
            # Validate required fields
            if not book_number:
                messagebox.showerror("Fehler", "Buchnummer ist erforderlich.")
                self.book_number_entry.focus()
                return
            
            if not title:
                messagebox.showerror("Fehler", "Titel ist erforderlich.")
                self.title_entry.focus()
                return
            
            # Parse publication year
            publication_year = None
            if year_str:
                try:
                    publication_year = int(year_str)
                except ValueError:
                    messagebox.showerror("Fehler", "Erscheinungsjahr muss eine Zahl sein.")
                    self.year_entry.focus()
                    return
            
            # Update book
            updated_book = self.book_service.update_book(
                self.book.id,
                book_number=book_number,
                title=title,
                author=author if author else None,
                isbn=isbn if isbn else None,
                publication_year=publication_year
            )
            
            if updated_book:
                # Show success message
                messagebox.showinfo("Erfolg", 
                                  f"Buch erfolgreich aktualisiert!\n"
                                  f"Buchnummer: {updated_book.book_number}\n"
                                  f"Titel: {updated_book.title}")
                
                # Store result and call success callback
                self.result = updated_book
                if self.on_success:
                    self.on_success(updated_book)
                
                # Close dialog
                self.dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Buch konnte nicht gefunden oder aktualisiert werden.")
            
        except ValueError as e:
            messagebox.showerror("Validierungsfehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def _cancel(self):
        """Cancel edit and close dialog."""
        self.dialog.destroy()

# Example usage/test function
def main():
    """Test the book management UI."""
    root = tk.Tk()
    root.title("Book Management Test")
    root.geometry("1000x700")
    
    # Initialize database
    db_manager = DatabaseManager("test_library.db")
    db_manager.initialize_database()
    
    # Create book list view
    book_view = BookListView(root, db_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()