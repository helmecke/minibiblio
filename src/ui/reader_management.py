import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from business.reader_service import ReaderService
from database.models import Reader

class ReaderRegistrationDialog:
    """Dialog for registering new library readers."""
    
    def __init__(self, parent, db_manager: DatabaseManager, on_success: Optional[Callable] = None):
        """
        Initialize reader registration dialog.
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
            on_success: Callback function called when reader is successfully created
        """
        self.parent = parent
        self.reader_service = ReaderService(db_manager)
        self.on_success = on_success
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Neuen Leser registrieren")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self._center_dialog()
        
        # Create form
        self._create_form()
        
        # Focus on name field
        self.name_entry.focus()
    
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
        title_label = ttk.Label(main_frame, text="Neuen Leser registrieren", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Name field
        ttk.Label(main_frame, text="Name*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Address field
        ttk.Label(main_frame, text="Adresse*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.address_text = tk.Text(main_frame, width=30, height=3)
        self.address_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Phone field
        ttk.Label(main_frame, text="Telefon*:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Required fields note
        note_label = ttk.Label(main_frame, text="* Pflichtfelder", 
                              font=("TkDefaultFont", 8), foreground="gray")
        note_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Speichern", 
                                     command=self._save_reader)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Abbrechen", 
                                  command=self._cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self._save_reader())
        self.dialog.bind('<Escape>', lambda event: self._cancel())
    
    def _save_reader(self):
        """Save the new reader."""
        try:
            # Get form data
            name = self.name_entry.get().strip()
            address = self.address_text.get("1.0", tk.END).strip()
            phone = self.phone_entry.get().strip()
            
            # Validate required fields
            if not name:
                messagebox.showerror("Fehler", "Name ist erforderlich.")
                self.name_entry.focus()
                return
            
            if not address:
                messagebox.showerror("Fehler", "Adresse ist erforderlich.")
                self.address_text.focus()
                return
            
            if not phone:
                messagebox.showerror("Fehler", "Telefonnummer ist erforderlich.")
                self.phone_entry.focus()
                return
            
            # Create reader
            reader = self.reader_service.create_reader(name, address, phone)
            
            # Show success message
            messagebox.showinfo("Erfolg", 
                              f"Leser erfolgreich registriert!\n"
                              f"Lesernummer: {reader.reader_number}\n"
                              f"Name: {reader.name}")
            
            # Store result and call success callback
            self.result = reader
            if self.on_success:
                self.on_success(reader)
            
            # Close dialog
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Validierungsfehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def _cancel(self):
        """Cancel registration and close dialog."""
        self.dialog.destroy()

class ReaderListView:
    """View for displaying and managing list of readers."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """
        Initialize reader list view.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
        """
        self.parent = parent
        self.reader_service = ReaderService(db_manager)
        self.db_manager = db_manager
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_widgets()
        self._load_readers()
    
    def _create_widgets(self):
        """Create the list view widgets."""
        # Title and controls frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(top_frame, text="Leserverzeichnis", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Add reader button
        add_button = ttk.Button(button_frame, text="Neuer Leser", 
                               command=self._add_reader)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(button_frame, text="Aktualisieren", 
                                   command=self._load_readers)
        refresh_button.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Suchen:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("number", "name", "address", "phone")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        self.tree.heading("number", text="Nr.")
        self.tree.heading("name", text="Name")
        self.tree.heading("address", text="Adresse")
        self.tree.heading("phone", text="Telefon")
        
        self.tree.column("number", width=60, minwidth=50)
        self.tree.column("name", width=200, minwidth=150)
        self.tree.column("address", width=250, minwidth=200)
        self.tree.column("phone", width=150, minwidth=100)
        
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
        
        # Bind double-click to view reader details
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Context menu for edit/delete
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Details anzeigen", command=self._view_selected_reader)
        self.context_menu.add_command(label="Bearbeiten", command=self._edit_selected_reader)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Löschen", command=self._delete_selected_reader)
        
        # Bind right-click to show context menu
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _add_reader(self):
        """Show add reader dialog."""
        dialog = ReaderRegistrationDialog(self.parent, self.db_manager, 
                                         on_success=self._on_reader_added)
    
    def _on_reader_added(self, reader: Reader):
        """Callback when a reader is successfully added."""
        self._load_readers()
    
    def _load_readers(self):
        """Load and display all readers."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load readers
            readers = self.reader_service.get_all_readers()
            
            # Add readers to treeview
            for reader in readers:
                self.tree.insert("", tk.END, values=(
                    reader.reader_number,
                    reader.name,
                    reader.address.replace('\n', ' '),  # Single line for display
                    reader.phone
                ), tags=(reader.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Leser: {str(e)}")
    
    def _on_search(self, event):
        """Handle search input."""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._load_readers()
            return
        
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Search readers
            readers = self.reader_service.search_readers_by_name(search_term)
            
            # Add matching readers to treeview
            for reader in readers:
                self.tree.insert("", tk.END, values=(
                    reader.reader_number,
                    reader.name,
                    reader.address.replace('\n', ' '),
                    reader.phone
                ), tags=(reader.id,))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Suche: {str(e)}")
    
    def _on_double_click(self, event):
        """Handle double-click on reader item."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            reader_id = int(item['tags'][0])
            self._show_reader_details(reader_id)
    
    def _show_reader_details(self, reader_id: int):
        """Show detailed reader information."""
        try:
            reader_info = self.reader_service.get_reader_with_loans(reader_id)
            if reader_info:
                reader = reader_info['reader']
                loans = reader_info['loans']
                
                # Create details window
                details_window = tk.Toplevel(self.parent)
                details_window.title(f"Leser Details - {reader.name}")
                details_window.geometry("500x400")
                
                # Reader info
                info_frame = ttk.LabelFrame(details_window, text="Leserinformationen", padding="10")
                info_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(info_frame, text=f"Lesernummer: {reader.reader_number}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Name: {reader.name}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Adresse: {reader.address}").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Telefon: {reader.phone}").pack(anchor=tk.W)
                
                # Loan history
                loans_frame = ttk.LabelFrame(details_window, text=f"Ausleihhistorie ({len(loans)} Einträge)", padding="10")
                loans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                if loans:
                    # Create treeview for loans
                    loan_columns = ("book", "borrow_date", "return_date", "status")
                    loan_tree = ttk.Treeview(loans_frame, columns=loan_columns, show="headings", height=8)
                    
                    loan_tree.heading("book", text="Buch")
                    loan_tree.heading("borrow_date", text="Ausgeliehen")
                    loan_tree.heading("return_date", text="Zurückgegeben")
                    loan_tree.heading("status", text="Status")
                    
                    for loan in loans:
                        loan_tree.insert("", tk.END, values=(
                            f"{loan['book_title']} ({loan['book_number']})",
                            loan['borrow_date'] or "",
                            loan['return_date'] or "",
                            "Ausgeliehen" if loan['status'] == 'borrowed' else "Zurückgegeben"
                        ))
                    
                    loan_tree.pack(fill=tk.BOTH, expand=True)
                else:
                    ttk.Label(loans_frame, text="Keine Ausleihhistorie vorhanden.").pack()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Details: {str(e)}")
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_reader_id(self) -> Optional[int]:
        """Get the ID of the currently selected reader."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return int(item['tags'][0])
        return None
    
    def _view_selected_reader(self):
        """View details of selected reader."""
        reader_id = self._get_selected_reader_id()
        if reader_id:
            self._show_reader_details(reader_id)
    
    def _edit_selected_reader(self):
        """Edit selected reader."""
        reader_id = self._get_selected_reader_id()
        if reader_id:
            try:
                reader = self.reader_service.get_reader_by_id(reader_id)
                if reader:
                    dialog = ReaderEditDialog(self.parent, self.db_manager, reader, 
                                            on_success=self._on_reader_updated)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Lesers: {str(e)}")
    
    def _delete_selected_reader(self):
        """Delete selected reader."""
        reader_id = self._get_selected_reader_id()
        if reader_id:
            try:
                reader = self.reader_service.get_reader_by_id(reader_id)
                if reader:
                    # Confirm deletion
                    result = messagebox.askyesno("Leser löschen", 
                                               f"Sind Sie sicher, dass Sie den Leser '{reader.name}' löschen möchten?\n\n"
                                               "Diese Aktion kann nicht rückgängig gemacht werden.")
                    if result:
                        self.reader_service.delete_reader(reader_id)
                        messagebox.showinfo("Erfolg", "Leser wurde erfolgreich gelöscht.")
                        self._load_readers()
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")
    
    def _on_reader_updated(self, reader: Reader):
        """Callback when a reader is successfully updated."""
        self._load_readers()

class ReaderEditDialog:
    """Dialog for editing existing library readers."""
    
    def __init__(self, parent, db_manager: DatabaseManager, reader: Reader, on_success: Optional[Callable] = None):
        """
        Initialize reader edit dialog.
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
            reader: Reader object to edit
            on_success: Callback function called when reader is successfully updated
        """
        self.parent = parent
        self.reader_service = ReaderService(db_manager)
        self.reader = reader
        self.on_success = on_success
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Leser bearbeiten - {reader.name}")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self._center_dialog()
        
        # Create form
        self._create_form()
        
        # Focus on name field
        self.name_entry.focus()
    
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
        title_label = ttk.Label(main_frame, text=f"Leser bearbeiten", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Reader number (read-only)
        ttk.Label(main_frame, text="Lesernummer:").grid(row=1, column=0, sticky=tk.W, pady=5)
        reader_num_label = ttk.Label(main_frame, text=str(self.reader.reader_number), 
                                    font=("TkDefaultFont", 10, "bold"))
        reader_num_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Name field
        ttk.Label(main_frame, text="Name*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.name_entry.insert(0, self.reader.name)
        
        # Address field
        ttk.Label(main_frame, text="Adresse*:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.address_text = tk.Text(main_frame, width=30, height=3)
        self.address_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.address_text.insert("1.0", self.reader.address)
        
        # Phone field
        ttk.Label(main_frame, text="Telefon*:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.phone_entry.insert(0, self.reader.phone)
        
        # Required fields note
        note_label = ttk.Label(main_frame, text="* Pflichtfelder", 
                              font=("TkDefaultFont", 8), foreground="gray")
        note_label.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Speichern", 
                                     command=self._save_reader)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Abbrechen", 
                                  command=self._cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self._save_reader())
        self.dialog.bind('<Escape>', lambda event: self._cancel())
    
    def _save_reader(self):
        """Save the updated reader."""
        try:
            # Get form data
            name = self.name_entry.get().strip()
            address = self.address_text.get("1.0", tk.END).strip()
            phone = self.phone_entry.get().strip()
            
            # Validate required fields
            if not name:
                messagebox.showerror("Fehler", "Name ist erforderlich.")
                self.name_entry.focus()
                return
            
            if not address:
                messagebox.showerror("Fehler", "Adresse ist erforderlich.")
                self.address_text.focus()
                return
            
            if not phone:
                messagebox.showerror("Fehler", "Telefonnummer ist erforderlich.")
                self.phone_entry.focus()
                return
            
            # Update reader
            updated_reader = self.reader_service.update_reader(self.reader.id, name, address, phone)
            
            if updated_reader:
                # Show success message
                messagebox.showinfo("Erfolg", 
                                  f"Leser erfolgreich aktualisiert!\n"
                                  f"Lesernummer: {updated_reader.reader_number}\n"
                                  f"Name: {updated_reader.name}")
                
                # Store result and call success callback
                self.result = updated_reader
                if self.on_success:
                    self.on_success(updated_reader)
                
                # Close dialog
                self.dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Leser konnte nicht gefunden oder aktualisiert werden.")
            
        except ValueError as e:
            messagebox.showerror("Validierungsfehler", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def _cancel(self):
        """Cancel edit and close dialog."""
        self.dialog.destroy()

# Example usage/test function
def main():
    """Test the reader management UI."""
    root = tk.Tk()
    root.title("Reader Management Test")
    root.geometry("800x600")
    
    # Initialize database
    db_manager = DatabaseManager("test_library.db")
    db_manager.initialize_database()
    
    # Create reader list view
    reader_view = ReaderListView(root, db_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()