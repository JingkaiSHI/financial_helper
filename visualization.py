import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class VisualizationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def show_visualizations(self, parent=None):
        """Create a window with text-based financial summaries."""
        if not parent:
            window = tk.Toplevel()
            window.title("Financial Summary")
            window.geometry("800x600")
        else:
            window = parent
        
        # Create notebook with tabs
        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        current_month_tab = ttk.Frame(notebook)
        last_month_tab = ttk.Frame(notebook)
        custom_period_tab = ttk.Frame(notebook)
        
        notebook.add(current_month_tab, text="Current Month")
        notebook.add(last_month_tab, text="Last Month")
        notebook.add(custom_period_tab, text="Custom Period")
        
        # Get date ranges
        today = datetime.now()
        first_day = today.replace(day=1)
        current_month_start = first_day.strftime("%Y-%m-%d")
        current_month_end = today.strftime("%Y-%m-%d")
        
        last_month_end = first_day - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1).strftime("%Y-%m-%d")
        last_month_end = last_month_end.strftime("%Y-%m-%d")
        
        # Set up each tab
        self._setup_summary_tab(current_month_tab, current_month_start, current_month_end, "Current Month")
        self._setup_summary_tab(last_month_tab, last_month_start, last_month_end, "Last Month")
        self._setup_custom_period_tab(custom_period_tab)
        
        return window if not parent else None
    
    def _setup_summary_tab(self, tab, start_date, end_date, period_name):
        """Set up a tab with financial summary info."""
        # Create scrollable text area
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap="word", padx=10, pady=10)
        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", fill="both", expand=True)
        
        # Get data and generate summary
        entries = self.db_manager.get_entries(start_date, end_date)
        
        # Write the summary
        text_widget.insert("end", f"Financial Summary for {period_name}\n", "header")
        text_widget.insert("end", f"Period: {start_date} to {end_date}\n\n")
        
        # Overview
        total_income = sum(entry["amount"] for entry in entries if entry["amount"] > 0)
        total_spending = sum(entry["amount"] for entry in entries if entry["amount"] < 0)
        net_change = total_income + total_spending  # spending is already negative
        
        text_widget.insert("end", "OVERVIEW\n", "section")
        text_widget.insert("end", f"Total Income: ${total_income:.2f}\n")
        text_widget.insert("end", f"Total Spending: ${abs(total_spending):.2f}\n")
        text_widget.insert("end", f"Net Change: ${net_change:.2f}\n\n")
        
        # Spending by category
        text_widget.insert("end", "SPENDING BY CATEGORY\n", "section")
        
        # Group entries by category
        category_spending = {}
        for entry in entries:
            if entry["amount"] < 0:  # Only spending entries
                category = entry["name"]
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += abs(entry["amount"])
        
        # Sort categories by amount
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            percentage = (amount / abs(total_spending)) * 100 if total_spending != 0 else 0
            text_widget.insert("end", f"{category}: ${amount:.2f} ({percentage:.1f}%)\n")
        
        text_widget.insert("end", "\n")
        
        # Income by category
        text_widget.insert("end", "INCOME BY CATEGORY\n", "section")
        
        # Group entries by category for income
        category_income = {}
        for entry in entries:
            if entry["amount"] > 0:  # Only income entries
                category = entry["name"]
                if category not in category_income:
                    category_income[category] = 0
                category_income[category] += entry["amount"]
        
        # Sort categories by amount
        sorted_income_categories = sorted(category_income.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_income_categories:
            percentage = (amount / total_income) * 100 if total_income != 0 else 0
            text_widget.insert("end", f"{category}: ${amount:.2f} ({percentage:.1f}%)\n")
        
        # Apply some basic text styling
        text_widget.tag_configure("header", font=("Arial", 16, "bold"))
        text_widget.tag_configure("section", font=("Arial", 12, "bold"))
        
        # Make read-only
        text_widget.configure(state="disabled")
    
    def _setup_custom_period_tab(self, tab):
        """Set up the custom period tab with date inputs."""
        # Control frame
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Start Date:").pack(side="left", padx=5)
        start_date_entry = ttk.Entry(control_frame, width=12)
        start_date_entry.pack(side="left", padx=5)
        
        # Default to 30 days ago
        default_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        start_date_entry.insert(0, default_start)
        
        ttk.Label(control_frame, text="End Date:").pack(side="left", padx=5)
        end_date_entry = ttk.Entry(control_frame, width=12)
        end_date_entry.pack(side="left", padx=5)
        end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Content frame that will be replaced when generating new report
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        def update_report():
            # Clear existing content
            for widget in content_frame.winfo_children():
                widget.destroy()
                
            # Get dates
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            
            # Validate dates
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                error_label = ttk.Label(content_frame, text="Invalid date format. Use YYYY-MM-DD",
                                      foreground="red")
                error_label.pack(pady=20)
                return
                
            # Create a new summary in the content frame
            new_frame = ttk.Frame(content_frame)
            new_frame.pack(fill="both", expand=True)
            
            # Use the same method as for the fixed period tabs
            self._setup_summary_tab(new_frame, start_date, end_date, "Custom Period")
        
        # Update button
        ttk.Button(control_frame, text="Generate Report", command=update_report).pack(side="left", padx=20)
        
        # Generate initial report
        update_report()