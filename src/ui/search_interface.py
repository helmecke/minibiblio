import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.reader_service import ReaderService
from business.book_service import BookService
from business.loan_service import LoanService
from database.models import Reader, Book, Loan

class SearchInterface:
    """Universal search interface for readers, books, and loans."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """
        Initialize search interface.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
        """
        self.parent = parent
        self.reader_service = ReaderService(db_manager)
        self.book_service = BookService(db_manager)
        self.loan_service = LoanService(db_manager)
        self.db_manager = db_manager
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search results storage
        self.current_results = []
        self.current_search_type = "all"
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the search interface widgets."""
        # Title
        title_label = ttk.Label(self.main_frame, text="Universelle Suche", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Search controls frame
        search_frame = ttk.LabelFrame(self.main_frame, text="Suchoptionen", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search type selection
        type_frame = ttk.Frame(search_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="Suchen in:").pack(side=tk.LEFT)
        
        self.search_type_var = tk.StringVar(value="all")
        search_types = [
            ("all", "Alles"),
            ("readers", "Leser"),
            ("books", "Bücher"),
            ("loans", "Ausleihen")
        ]
        
        for value, text in search_types:
            ttk.Radiobutton(type_frame, text=text, variable=self.search_type_var, 
                           value=value, command=self._on_search_type_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # Search input frame
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Suchbegriff:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(input_frame, width=40, font=("TkDefaultFont", 12))
        self.search_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self._on_search_input)
        self.search_entry.bind('<Return>', self._perform_search)
        
        # Search button
        self.search_button = ttk.Button(input_frame, text="Suchen", command=self._perform_search)
        self.search_button.pack(side=tk.LEFT)
        
        # Clear button
        clear_button = ttk.Button(input_frame, text="Löschen", command=self._clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Advanced search options
        advanced_frame = ttk.Frame(search_frame)
        advanced_frame.pack(fill=tk.X)
        
        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Groß-/Kleinschreibung beachten", 
                       variable=self.case_sensitive_var).pack(side=tk.LEFT)
        
        self.exact_match_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Exakte Übereinstimmung", 
                       variable=self.exact_match_var).pack(side=tk.LEFT, padx=(20, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Suchergebnisse", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results info
        self.results_info_frame = ttk.Frame(results_frame)
        self.results_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.results_count_label = ttk.Label(self.results_info_frame, text="Bereit für Suche...")
        self.results_count_label.pack(side=tk.LEFT)
        
        # Export button
        self.export_button = ttk.Button(self.results_info_frame, text="Exportieren", 
                                       command=self._export_results, state=tk.DISABLED)
        self.export_button.pack(side=tk.RIGHT)
        
        # Results treeview
        self._create_results_treeview(results_frame)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.main_frame, text="Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.details_text = tk.Text(details_frame, height=6, state=tk.DISABLED, wrap=tk.WORD)
        self.details_text.pack(fill=tk.X)
        
        # Focus on search entry
        self.search_entry.focus()
    
    def _create_results_treeview(self, parent):
        """Create the results treeview."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with dynamic columns
        self.results_tree = ttk.Treeview(tree_frame, show="headings", height=15)
        
        # Configure columns (will be updated based on search type)
        self._update_treeview_columns()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.results_tree.bind('<<TreeviewSelect>>', self._on_result_select)
        self.results_tree.bind('<Double-1>', self._on_result_double_click)
        
        # Context menu
        self.context_menu = tk.Menu(self.results_tree, tearoff=0)
        self.context_menu.add_command(label="Details anzeigen", command=self._show_selected_details)
        self.context_menu.add_command(label="Bearbeiten", command=self._edit_selected_item)
        self.results_tree.bind('<Button-3>', self._show_context_menu)
    
    def _update_treeview_columns(self):
        """Update treeview columns based on search type."""
        search_type = self.search_type_var.get()
        
        # Clear existing columns
        self.results_tree["columns"] = ()
        
        if search_type == "readers":
            columns = ("number", "name", "address", "phone", "loans")
            headings = ("Nr.", "Name", "Adresse", "Telefon", "Ausleihen")
            widths = (80, 200, 250, 150, 100)
        elif search_type == "books":
            columns = ("number", "title", "author", "year", "status")
            headings = ("Buchnr.", "Titel", "Autor", "Jahr", "Status")
            widths = (100, 300, 200, 80, 120)
        elif search_type == "loans":
            columns = ("reader", "book", "borrow_date", "return_date", "status")
            headings = ("Leser", "Buch", "Ausleihdatum", "Rückgabe", "Status")
            widths = (200, 250, 120, 120, 100)
        else:  # all
            columns = ("type", "item", "details", "status")
            headings = ("Typ", "Element", "Details", "Status")
            widths = (100, 300, 300, 120)
        
        self.results_tree["columns"] = columns
        
        for i, (col, heading, width) in enumerate(zip(columns, headings, widths)):
            self.results_tree.heading(col, text=heading)
            self.results_tree.column(col, width=width, minwidth=80)
    
    def _on_search_type_change(self):
        """Handle search type change."""
        self._update_treeview_columns()
        self._clear_results()
        
        # Update placeholder text
        search_type = self.search_type_var.get()
        if search_type == "readers":
            placeholder = "Lesername eingeben..."
        elif search_type == "books":
            placeholder = "Buchtitel, Autor oder Buchnummer eingeben..."
        elif search_type == "loans":
            placeholder = "Lesername oder Buchtitel eingeben..."
        else:
            placeholder = "Suchbegriff eingeben..."
        
        # Update search entry placeholder (via tooltip or label)
        self.results_count_label.config(text=f"Bereit für Suche in: {self._get_search_type_display_name()}")
    
    def _get_search_type_display_name(self):
        """Get display name for current search type."""
        search_type = self.search_type_var.get()
        type_names = {
            "all": "Alles",
            "readers": "Leser",
            "books": "Bücher",
            "loans": "Ausleihen"
        }
        return type_names.get(search_type, "Alles")
    
    def _on_search_input(self, event):
        """Handle search input changes (real-time search)."""
        # Perform search automatically after a short delay
        if hasattr(self, '_search_timer'):
            self.main_frame.after_cancel(self._search_timer)
        
        # Only search if there's meaningful input
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 2:  # Minimum 2 characters
            self._search_timer = self.main_frame.after(500, self._perform_search)  # 500ms delay
        elif len(search_term) == 0:
            self._clear_results()
    
    def _perform_search(self, event=None):
        """Perform the search based on current settings."""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._clear_results()
            return
        
        try:
            search_type = self.search_type_var.get()
            self.current_results = []
            
            if search_type == "readers" or search_type == "all":
                readers = self._search_readers(search_term)
                self.current_results.extend(readers)
            
            if search_type == "books" or search_type == "all":
                books = self._search_books(search_term)
                self.current_results.extend(books)
            
            if search_type == "loans" or search_type == "all":
                loans = self._search_loans(search_term)
                self.current_results.extend(loans)
            
            self._display_results()
            
        except Exception as e:
            messagebox.showerror("Suchfehler", f"Fehler bei der Suche: {str(e)}")
    
    def _search_readers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for readers."""
        readers = self.reader_service.search_readers_by_name(search_term)
        results = []
        
        for reader in readers:
            # Get loan count for reader
            loan_counts = self.loan_service.get_reader_loan_count(reader.id)
            
            results.append({
                'type': 'reader',
                'id': reader.id,
                'data': reader,
                'display_data': {
                    'number': reader.reader_number,
                    'name': reader.name,
                    'address': reader.address.replace('\n', ' '),
                    'phone': reader.phone,
                    'loans': f"{loan_counts['active_loans']}/{loan_counts['total_loans']}"
                }
            })
        
        return results
    
    def _search_books(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for books."""
        books = self.book_service.search_books(search_term)
        results = []
        
        for book in books:
            # Check availability
            is_available = self.loan_service.is_book_available(book.id)
            status = "Verfügbar" if is_available else "Ausgeliehen"
            
            results.append({
                'type': 'book',
                'id': book.id,
                'data': book,
                'display_data': {
                    'number': book.book_number,
                    'title': book.title,
                    'author': book.author or "",
                    'year': book.publication_year or "",
                    'status': status
                }
            })
        
        return results
    
    def _search_loans(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for loans."""
        # Search by reader name and book title
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
        
        results = []
        for loan in unique_loans:
            status = "Zurückgegeben" if loan.status == "returned" else "Ausgeliehen"
            
            results.append({
                'type': 'loan',
                'id': loan.id,
                'data': loan,
                'display_data': {
                    'reader': getattr(loan, 'reader_name', 'Unbekannt'),
                    'book': f"{getattr(loan, 'book_title', 'Unbekannt')} ({getattr(loan, 'book_number', '')})",
                    'borrow_date': loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else "",
                    'return_date': loan.return_date.strftime('%d.%m.%Y') if loan.return_date else "",
                    'status': status
                }
            })
        
        return results
    
    def _display_results(self):
        """Display search results in the treeview."""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Update results count
        count = len(self.current_results)
        search_type_name = self._get_search_type_display_name()
        self.results_count_label.config(text=f"{count} Ergebnisse in {search_type_name} gefunden")
        
        # Enable/disable export button
        self.export_button.config(state=tk.NORMAL if count > 0 else tk.DISABLED)
        
        if not self.current_results:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, "Keine Ergebnisse gefunden.")
            self.details_text.config(state=tk.DISABLED)
            return
        
        # Display results based on search type
        search_type = self.search_type_var.get()
        
        for result in self.current_results:
            if search_type == "all":
                # Mixed results display
                item_type = result['type']
                if item_type == 'reader':
                    item_text = f"{result['data'].name} (Nr. {result['data'].reader_number})"
                    details = f"Adresse: {result['data'].address.replace(chr(10), ' ')}"
                    status = f"{result['display_data']['loans']} Ausleihen"
                elif item_type == 'book':
                    item_text = f"{result['data'].title}"
                    details = f"Autor: {result['data'].author or 'Unbekannt'}, Nr: {result['data'].book_number}"
                    status = result['display_data']['status']
                else:  # loan
                    item_text = f"{result['display_data']['reader']} → {result['display_data']['book']}"
                    details = f"Ausgeliehen: {result['display_data']['borrow_date']}"
                    status = result['display_data']['status']
                
                values = (
                    item_type.capitalize(),
                    item_text,
                    details,
                    status
                )
            else:
                # Specific type display
                values = tuple(result['display_data'].values())
            
            self.results_tree.insert("", tk.END, values=values, tags=(result['type'], result['id']))
        
        # Clear details initially
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "Wählen Sie ein Ergebnis aus, um Details anzuzeigen.")
        self.details_text.config(state=tk.DISABLED)
    
    def _clear_search(self):
        """Clear the search."""
        self.search_entry.delete(0, tk.END)
        self._clear_results()
    
    def _clear_results(self):
        """Clear search results."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = []
        self.results_count_label.config(text=f"Bereit für Suche in: {self._get_search_type_display_name()}")
        self.export_button.config(state=tk.DISABLED)
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
    
    def _on_result_select(self, event):
        """Handle result selection."""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        tags = item['tags']
        
        if len(tags) >= 2:
            result_type = tags[0]
            result_id = int(tags[1])
            
            # Find the result data
            result_data = None
            for result in self.current_results:
                if result['type'] == result_type and result['id'] == result_id:
                    result_data = result['data']
                    break
            
            if result_data:
                self._show_details(result_type, result_data)
    
    def _show_details(self, result_type: str, data):
        """Show detailed information for selected result."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        if result_type == 'reader':
            details = f"Leser Details:\n\n"
            details += f"Lesernummer: {data.reader_number}\n"
            details += f"Name: {data.name}\n"
            details += f"Adresse: {data.address}\n"
            details += f"Telefon: {data.phone}\n"
            
            # Add loan information
            try:
                loan_counts = self.loan_service.get_reader_loan_count(data.id)
                details += f"\nAusleihen: {loan_counts['active_loans']} aktiv, {loan_counts['total_loans']} gesamt"
            except:
                pass
                
        elif result_type == 'book':
            details = f"Buch Details:\n\n"
            details += f"Buchnummer: {data.book_number}\n"
            details += f"Titel: {data.title}\n"
            details += f"Autor: {data.author or 'Nicht angegeben'}\n"
            details += f"ISBN: {data.isbn or 'Nicht angegeben'}\n"
            details += f"Erscheinungsjahr: {data.publication_year or 'Nicht angegeben'}\n"
            
            # Add availability information
            try:
                is_available = self.loan_service.is_book_available(data.id)
                details += f"\nStatus: {'Verfügbar' if is_available else 'Ausgeliehen'}"
            except:
                pass
                
        elif result_type == 'loan':
            details = f"Ausleihe Details:\n\n"
            details += f"Leser: {getattr(data, 'reader_name', 'Unbekannt')}\n"
            details += f"Buch: {getattr(data, 'book_title', 'Unbekannt')} ({getattr(data, 'book_number', '')})\n"
            details += f"Ausleihdatum: {data.borrow_date.strftime('%d.%m.%Y') if data.borrow_date else 'Unbekannt'}\n"
            details += f"Rückgabedatum: {data.return_date.strftime('%d.%m.%Y') if data.return_date else 'Noch nicht zurückgegeben'}\n"
            details += f"Status: {'Zurückgegeben' if data.status == 'returned' else 'Ausgeliehen'}\n"
            
            if data.borrow_date and not data.return_date:
                from datetime import date
                days_borrowed = (date.today() - data.borrow_date).days
                details += f"Tage ausgeliehen: {days_borrowed}"
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
    
    def _on_result_double_click(self, event):
        """Handle double-click on result."""
        self._edit_selected_item()
    
    def _show_context_menu(self, event):
        """Show context menu."""
        # Select item under cursor
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _show_selected_details(self):
        """Show details window for selected item."""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        tags = item['tags']
        
        if len(tags) >= 2:
            result_type = tags[0]
            result_id = int(tags[1])
            
            if result_type == 'reader':
                self._show_reader_details(result_id)
            elif result_type == 'book':
                self._show_book_details(result_id)
            elif result_type == 'loan':
                self._show_loan_details(result_id)
    
    def _edit_selected_item(self):
        """Edit selected item."""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        tags = item['tags']
        
        if len(tags) >= 2:
            result_type = tags[0]
            result_id = int(tags[1])
            
            try:
                if result_type == 'reader':
                    from ui.reader_management import ReaderEditDialog
                    reader = self.reader_service.get_reader_by_id(result_id)
                    if reader:
                        ReaderEditDialog(self.parent, self.db_manager, reader)
                elif result_type == 'book':
                    from ui.book_management import BookEditDialog
                    book = self.book_service.get_book_by_id(result_id)
                    if book:
                        BookEditDialog(self.parent, self.db_manager, book)
                elif result_type == 'loan':
                    messagebox.showinfo("Information", "Ausleihen können über die Ausleihen-Ansicht verwaltet werden.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Bearbeiten: {str(e)}")
    
    def _show_reader_details(self, reader_id: int):
        """Show reader details window."""
        try:
            reader_info = self.reader_service.get_reader_with_loans(reader_id)
            if reader_info:
                # Use the existing reader details functionality
                messagebox.showinfo("Reader Details", f"Reader: {reader_info['reader'].name}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Leser-Details: {str(e)}")
    
    def _show_book_details(self, book_id: int):
        """Show book details window."""
        try:
            book_info = self.book_service.get_book_with_loans(book_id)
            if book_info:
                # Use the existing book details functionality
                messagebox.showinfo("Book Details", f"Book: {book_info['book'].title}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Buch-Details: {str(e)}")
    
    def _show_loan_details(self, loan_id: int):
        """Show loan details window."""
        try:
            loan = self.loan_service.get_loan_by_id(loan_id)
            if loan:
                messagebox.showinfo("Loan Details", f"Loan: {loan.reader_name} → {loan.book_title}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Ausleihe-Details: {str(e)}")
    
    def _export_results(self):
        """Export search results to file."""
        if not self.current_results:
            messagebox.showwarning("Warnung", "Keine Ergebnisse zum Exportieren vorhanden.")
            return
        
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Suchergebnisse exportieren"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"MiniBiblio - Suchergebnisse\n")
                    f.write(f"Suchbegriff: {self.search_entry.get()}\n")
                    f.write(f"Suchbereich: {self._get_search_type_display_name()}\n")
                    f.write(f"Anzahl Ergebnisse: {len(self.current_results)}\n")
                    f.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, result in enumerate(self.current_results, 1):
                        f.write(f"{i}. {result['type'].upper()}\n")
                        data = result['data']
                        
                        if result['type'] == 'reader':
                            f.write(f"   Name: {data.name}\n")
                            f.write(f"   Nummer: {data.reader_number}\n")
                            f.write(f"   Adresse: {data.address}\n")
                            f.write(f"   Telefon: {data.phone}\n")
                        elif result['type'] == 'book':
                            f.write(f"   Titel: {data.title}\n")
                            f.write(f"   Nummer: {data.book_number}\n")
                            f.write(f"   Autor: {data.author or 'Unbekannt'}\n")
                            f.write(f"   ISBN: {data.isbn or 'Unbekannt'}\n")
                        elif result['type'] == 'loan':
                            f.write(f"   Leser: {getattr(data, 'reader_name', 'Unbekannt')}\n")
                            f.write(f"   Buch: {getattr(data, 'book_title', 'Unbekannt')}\n")
                            f.write(f"   Ausleihdatum: {data.borrow_date.strftime('%d.%m.%Y') if data.borrow_date else 'Unbekannt'}\n")
                            f.write(f"   Status: {data.status}\n")
                        
                        f.write("\n")
                
                messagebox.showinfo("Export erfolgreich", f"Ergebnisse wurden nach {filename} exportiert.")
        
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren: {str(e)}")

# Example usage/test function
def main():
    """Test the search interface."""
    root = tk.Tk()
    root.title("Search Interface Test")
    root.geometry("1000x700")
    
    # Initialize database
    db_manager = DatabaseManager("test_library.db")
    db_manager.initialize_database()
    
    # Create search interface
    search_interface = SearchInterface(root, db_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()