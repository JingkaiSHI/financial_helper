import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText
import sys

class FinancialHelperGUI:
    def __init__(self, root, db_manager, category_manager, reminder_manager, visualization_manager):
        self.root = root
        self.db_manager = db_manager
        self.category_manager = category_manager
        self.reminder_manager = reminder_manager
        self.visualization_manager = visualization_manager
        
        self.root.title("Financial Helper")
        self.root.geometry("800x600")
        
        # Set initial state of reminder to be checked based on database
        if self.reminder_manager.check_if_reminder_needed():
            self._show_reminder_dialog()
        
        self._create_widgets()
        self.reminder_manager.trigger_callback = self._show_reminder_dialog
        self.reminder_manager.start_reminder_service()
        
        # Set up protocol for app closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.entry_tab = ttk.Frame(self.notebook)
        self.data_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.entry_tab, text="New Entry")
        self.notebook.add(self.data_tab, text="Data View")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Set up each tab
        self._setup_entry_tab()
        self._setup_data_tab()
        self._setup_settings_tab()
    
    def _setup_entry_tab(self):
        """Set up the entry tab UI."""
        frame = ttk.LabelFrame(self.entry_tab, text="Add New Entry")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Amount
        ttk.Label(frame, text="Amount:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(frame, text="(Positive for income, negative for spending)").grid(
            row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Category
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(frame, textvariable=self.category_var)
        self.category_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self._update_category_list()
        
        # New category button
        ttk.Button(frame, text="New Category", command=self._add_new_category).grid(
            row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Date
        ttk.Label(frame, text="Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry = ttk.Entry(frame)
        self.date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.date_entry.insert(0, today)
        ttk.Label(frame, text="(YYYY-MM-DD)").grid(
            row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Note
        ttk.Label(frame, text="Note:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.note_text = ScrolledText(frame, width=30, height=5)
        self.note_text.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Save button
        ttk.Button(frame, text="Save Entry", command=self._save_entry).grid(
            row=4, column=0, columnspan=3, pady=20)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
    
    def _setup_data_tab(self):
        """Set up the data view tab UI."""
        frame = ttk.Frame(self.data_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Controls frame at top
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill="x", pady=5)
        
        ttk.Label(controls_frame, text="Filter by Date Range:").pack(side="left", padx=5)
        self.start_date_entry = ttk.Entry(controls_frame, width=10)
        self.start_date_entry.pack(side="left", padx=5)
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        self.start_date_entry.insert(0, start_date)
        
        ttk.Label(controls_frame, text="to").pack(side="left", padx=5)
        
        self.end_date_entry = ttk.Entry(controls_frame, width=10)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(controls_frame, text="Apply Filter", command=self._refresh_data_view).pack(side="left", padx=10)
        ttk.Button(controls_frame, text="View Summary", command=self._visualize_data).pack(side="left", padx=10)
        
        # Treeview for data
        self.tree_frame = ttk.Frame(frame)
        self.tree_frame.pack(fill="both", expand=True, pady=5)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")
        
        columns = ("ID", "Date", "Amount", "Category", "Note")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", 
                                height=15, yscrollcommand=self.tree_scroll.set)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col != "Note" else 200
            self.tree.column(col, width=width)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # Bind double click for editing
        self.tree.bind("<Double-1>", self._edit_entry)
        
        # Button frame at bottom
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Edit Selected", command=self._edit_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh Data", command=self._refresh_data_view).pack(side="left", padx=5)
        
        # Initial data load
        self._refresh_data_view()
    
    def _setup_settings_tab(self):
        """Set up the settings tab UI."""
        frame = ttk.LabelFrame(self.settings_tab, text="Reminder Settings")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Reminder time setting
        ttk.Label(frame, text="Reminder Time:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        reminder_settings = self.db_manager.get_reminder_settings()
        time_parts = reminder_settings["time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        self.hour_var = tk.StringVar(value=str(hour).zfill(2))
        self.minute_var = tk.StringVar(value=str(minute).zfill(2))
        
        hour_spin = ttk.Spinbox(frame, from_=0, to=23, wrap=True, textvariable=self.hour_var, width=3)
        hour_spin.grid(row=0, column=1, padx=5, pady=10)
        
        ttk.Label(frame, text=":").grid(row=0, column=2)
        
        minute_spin = ttk.Spinbox(frame, from_=0, to=59, wrap=True, textvariable=self.minute_var, width=3)
        minute_spin.grid(row=0, column=3, padx=5, pady=10)
        
        ttk.Button(frame, text="Save Reminder Settings", command=self._save_reminder_settings).grid(
            row=0, column=4, padx=20, pady=10)
        
        # Category management section
        cat_frame = ttk.LabelFrame(self.settings_tab, text="Category Management")
        cat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Category list
        ttk.Label(cat_frame, text="Categories:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.category_listbox = tk.Listbox(cat_frame, height=10, width=30)
        self.category_listbox.grid(row=1, column=0, rowspan=3, padx=5, pady=5, sticky="nsew")
        
        category_scroll = ttk.Scrollbar(cat_frame, orient="vertical", command=self.category_listbox.yview)
        category_scroll.grid(row=1, column=1, rowspan=3, sticky="ns")
        self.category_listbox.configure(yscrollcommand=category_scroll.set)
        
        # Category buttons
        ttk.Button(cat_frame, text="Add Category", command=self._add_new_category).grid(
            row=1, column=2, padx=10, pady=5, sticky="ew")
        
        # Note about categories
        ttk.Label(cat_frame, text="Note: Categories are permanent\nonce created").grid(
            row=2, column=2, padx=10, pady=20, sticky="ew")
        
        # Configure grid
        cat_frame.columnconfigure(0, weight=1)
        cat_frame.rowconfigure(3, weight=1)
        
        # Initial category list load
        self._update_category_list()
    
    def _save_entry(self):
        """Save a new entry."""
        try:
            # Get values from form
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                messagebox.showerror("Error", "Amount cannot be empty")
                return
                
            amount = float(amount_str)
            category = self.category_var.get().strip()
            
            if not category:
                messagebox.showerror("Error", "Please select or create a category")
                return
                
            entry_date = self.date_entry.get().strip()
            note = self.note_text.get("1.0", "end-1c").strip()
            
            # Validate date format
            try:
                datetime.datetime.strptime(entry_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            # Add to database
            success = self.db_manager.add_entry(amount, category, entry_date, note)
            
            if success:
                messagebox.showinfo("Success", "Entry saved successfully!")
                # Clear form
                self.amount_entry.delete(0, "end")
                self.note_text.delete("1.0", "end")
                # Update data view if visible
                if self.notebook.index("current") == 1:  # Data tab
                    self._refresh_data_view()
            else:
                messagebox.showerror("Error", "Failed to save entry")
                
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
    
    def _update_category_list(self):
        """Update category combobox and listbox with current categories."""
        categories = self.db_manager.get_categories()
        
        # Update combobox
        if hasattr(self, 'category_combobox'):
            self.category_combobox['values'] = categories
        
        # Update listbox in settings tab (if it exists)
        if hasattr(self, 'category_listbox'):
            self.category_listbox.delete(0, "end")
            for category in sorted(categories):
                self.category_listbox.insert("end", category)
    
    def _add_new_category(self):
        """Add a new category."""
        new_category = simpledialog.askstring("New Category", "Enter a new category name:")
        if new_category:
            # Check if category already exists
            categories = self.db_manager.get_categories()
            if new_category in categories:
                messagebox.showinfo("Info", "Category already exists")
            else:
                success, message = self.category_manager.add_category(new_category)
                if success:
                    self._update_category_list()
                    self.category_var.set(new_category)
                else:
                    messagebox.showerror("Error", message)
    
    def _refresh_data_view(self):
        """Refresh the data view based on current filters."""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Get date range for filtering
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        # Validate dates
        try:
            if start_date:
                datetime.datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return
        
        # Get entries
        entries = self.db_manager.get_entries(start_date, end_date)
        
        # Add to treeview
        for entry in entries:
            self.tree.insert("", "end", values=(
                entry['id'], 
                entry['entry_date'], 
                f"${entry['amount']:.2f}", 
                entry['name'], 
                entry['note']
            ))
    
    def _edit_entry(self, event=None):
        """Handle double-click on entry."""
        self._edit_selected()
    
    def _edit_selected(self):
        """Edit the selected entry."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select an entry to edit")
            return
        
        # Get the selected item
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Entry")
        edit_window.geometry("400x300")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # ID
        entry_id = values[0]
        
        # Amount
        ttk.Label(edit_window, text="Amount:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        amount_var = tk.StringVar(value=values[2].replace("$", ""))
        amount_entry = ttk.Entry(edit_window, textvariable=amount_var)
        amount_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Category
        ttk.Label(edit_window, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        category_var = tk.StringVar(value=values[3])
        category_combo = ttk.Combobox(edit_window, textvariable=category_var)
        category_combo['values'] = self.db_manager.get_categories()
        category_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Date
        ttk.Label(edit_window, text="Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        date_var = tk.StringVar(value=values[1])
        date_entry = ttk.Entry(edit_window, textvariable=date_var)
        date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Note
        ttk.Label(edit_window, text="Note:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        note_text = ScrolledText(edit_window, width=30, height=5)
        note_text.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        note_text.insert("1.0", values[4] if values[4] else "")
        
        # Function to save changes
        def save_changes():
            try:
                amount = float(amount_var.get().strip())
                category = category_var.get().strip()
                entry_date = date_var.get().strip()
                note = note_text.get("1.0", "end-1c").strip()
                
                # Validate date format
                try:
                    datetime.datetime.strptime(entry_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                    return
                
                success = self.db_manager.update_entry(entry_id, amount, category, entry_date, note)
                
                if success:
                    messagebox.showinfo("Success", "Entry updated successfully!")
                    edit_window.destroy()
                    self._refresh_data_view()
                else:
                    messagebox.showerror("Error", "Failed to update entry")
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
        
        # Save button
        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(
            row=4, column=0, columnspan=2, pady=20)
        
        # Configure grid
        edit_window.columnconfigure(1, weight=1)
    
    def _delete_selected(self):
        """Delete the selected entry."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select an entry to delete")
            return
        
        # Get the selected item
        item = self.tree.item(selection[0])
        values = item['values']
        entry_id = values[0]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete this entry?\n\nAmount: {values[2]}\nCategory: {values[3]}\nDate: {values[1]}")
        
        if confirm:
            success = self.db_manager.delete_entry(entry_id)
            if success:
                messagebox.showinfo("Success", "Entry deleted successfully!")
                self._refresh_data_view()
            else:
                messagebox.showerror("Error", "Failed to delete entry")
    
    def _save_reminder_settings(self):
        """Save reminder settings."""
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            messagebox.showerror("Error", "Invalid time")
            return
            
        reminder_time = f"{hour:02d}:{minute:02d}"
        
        success = self.db_manager.update_reminder_time(reminder_time)
        if success:
            messagebox.showinfo("Success", "Reminder settings updated!")
        else:
            messagebox.showerror("Error", "Failed to update reminder settings")
    
    def _show_reminder_dialog(self):
        """Show reminder dialog that requires entry."""
        # Check if the dialog is already open
        if hasattr(self, 'reminder_dialog') and self.reminder_dialog.winfo_exists():
            self.reminder_dialog.lift()  # Bring to front if already exists
            return
            
        self.reminder_dialog = tk.Toplevel(self.root)
        self.reminder_dialog.title("Financial Entry Reminder")
        self.reminder_dialog.geometry("400x200")
        self.reminder_dialog.transient(self.root)
        self.reminder_dialog.grab_set()
        
        ttk.Label(self.reminder_dialog, 
                 text="It's time to record today's financial activity!",
                 font=("Arial", 12, "bold")).pack(pady=10)
                 
        ttk.Label(self.reminder_dialog, 
                 text="You must enter at least one transaction\nor confirm no spending today.").pack(pady=5)
        
        button_frame = ttk.Frame(self.reminder_dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Add Entry Now", 
                  command=self._handle_add_entry).pack(side="left", padx=10)
        
        ttk.Button(button_frame, text="No Spending Today", 
                  command=self._handle_no_spending).pack(side="left", padx=10)
    
    def _handle_add_entry(self):
        """Handle the 'Add Entry Now' action from reminder."""
        self.reminder_dialog.destroy()
        self.notebook.select(0)  # Switch to New Entry tab
    
    def _handle_no_spending(self):
        """Handle the 'No Spending Today' action from reminder."""
        # Add a zero-amount entry for today to mark it as recorded
        success = self.db_manager.add_entry(
            0.0, 
            "No Spending", 
            datetime.datetime.now().strftime("%Y-%m-%d"), 
            "No financial activity today"
        )
        
        if success:
            messagebox.showinfo("Recorded", "No spending today has been recorded.")
            self.reminder_dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to record. Please try again.")
    
    def _visualize_data(self):
        """Open visualization window."""
        self.visualization_manager.show_visualizations()
    
    def _on_close(self):
        """Handle application closing."""
        try:
            # Stop reminder service
            if hasattr(self, 'reminder_manager'):
                self.reminder_manager.stop_reminder_service()
            
            # Close any open dialogs
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            
            # Destroy main window
            self.root.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            # Force quit if regular shutdown fails
            self.root.quit()