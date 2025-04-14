import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import argparse
from datetime import datetime

# Import our modules
from db_manager import DatabaseManager
from category_manager import CategoryManager
from reminder import ReminderManager
from visualization import VisualizationManager
from gui import FinancialHelperGUI

def add_cli_entry(db_manager):
    """Add a financial entry via command line."""
    print("\n=== Add New Financial Entry ===")
    
    # Get amount
    while True:
        try:
            amount = float(input("Amount (positive for income, negative for spending): "))
            break
        except ValueError:
            print("Error: Please enter a valid number")
    
    # Show available categories
    categories = db_manager.get_categories()
    print("\nAvailable categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    
    # Get category
    while True:
        cat_input = input("\nSelect category (number or type a new name): ")
        try:
            idx = int(cat_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx]
                break
        except ValueError:
            # Not a number, use as new category name
            category = cat_input
            break
    
    # Get date
    date_input = input("Date (YYYY-MM-DD, press Enter for today): ")
    if not date_input:
        entry_date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            entry_date = date_input
        except ValueError:
            print("Invalid date format. Using today's date.")
            entry_date = datetime.now().strftime("%Y-%m-%d")
    
    # Get note
    note = input("Note (optional): ")
    
    # Add entry
    success = db_manager.add_entry(amount, category, entry_date, note)
    if success:
        print("\nEntry saved successfully!")
    else:
        print("\nFailed to save entry.")

def display_summary(db_manager):
    """Display financial summary in terminal."""
    print("\n=== Financial Summary ===")
    
    today = datetime.now()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    
    print(f"\nCurrent month ({first_day} to {today_str}):")
    entries = db_manager.get_entries(first_day, today_str)
    
    total_income = sum(e["amount"] for e in entries if e["amount"] > 0)
    total_expense = abs(sum(e["amount"] for e in entries if e["amount"] < 0))
    net = total_income - total_expense
    
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expenses: ${total_expense:.2f}")
    print(f"Net Change: ${net:.2f}")
    
    # Show recent entries
    print("\nRecent entries:")
    for i, entry in enumerate(entries[:5], 1):
        print(f"{i}. {entry['entry_date']}: ${entry['amount']:.2f} - {entry['name']} {entry['note']}")

def run_cli_mode(db_manager):
    """Run the application in CLI mode."""
    print("\nFinancial Helper - CLI Mode")
    
    while True:
        print("\nOptions:")
        print("1. Add new entry")
        print("2. View financial summary")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            add_cli_entry(db_manager)
        elif choice == '2':
            display_summary(db_manager)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-3.")
            
# Add this at the top of main.py
def fix_environment():
    """Fix environment variables and paths when running as app bundle"""
    import os
    import sys
    
    # Print diagnostic info to help debug
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # If running as app bundle, add the Resources directory to path
    if getattr(sys, 'frozen', False):
        bundle_dir = os.path.dirname(sys.executable)
        if 'Contents/MacOS' in bundle_dir:
            resources_dir = os.path.join(bundle_dir, '../Resources')
            resources_dir = os.path.normpath(resources_dir)
            if os.path.exists(resources_dir) and resources_dir not in sys.path:
                sys.path.insert(0, resources_dir)



def main():
    """Main entry point for the application."""
    fix_environment()
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Financial Helper Application")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    args = parser.parse_args()
    
    # Set up the database
    db_manager = DatabaseManager()
    
    # If CLI mode requested, run that
    if args.cli:
        run_cli_mode(db_manager)
        return
        
    # Try GUI mode, fall back to CLI if no display available
    try:
        # Create the root window
        root = tk.Tk()
        
        # Set up the category manager
        category_manager = CategoryManager(db_manager)
        
        # Set up the visualization manager
        visualization_manager = VisualizationManager(db_manager)
        
        # Set up the reminder manager
        reminder_manager = ReminderManager(db_manager)
        
        # Create the GUI
        app = FinancialHelperGUI(root, db_manager, category_manager, reminder_manager, visualization_manager)
        
        # Start the GUI event loop
        root.mainloop()
    except tk.TclError as e:
        if "no display" in str(e).lower():
            print("No display available. Running in command-line mode.")
            run_cli_mode(db_manager)
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()