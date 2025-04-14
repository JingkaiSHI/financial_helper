import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="financial_data.db"):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize database with required tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Create entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            category_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Create reminder settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminder_settings (
            id INTEGER PRIMARY KEY,
            time TEXT NOT NULL,
            last_entry_date TEXT
        )
        ''')
        
        # Insert default categories if none exist
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                ("Groceries",), ("Dining",), ("Transportation",),
                ("Housing",), ("Entertainment",), ("Utilities",),
                ("Healthcare",), ("Shopping",), ("Income",),
                ("Investments",), ("Miscellaneous",)
            ]
            cursor.executemany("INSERT INTO categories (name) VALUES (?)", default_categories)
        
        # Insert default reminder settings if none exist
        cursor.execute("SELECT COUNT(*) FROM reminder_settings")
        if cursor.fetchone()[0] == 0:
            default_time = "20:00"  # 8:00 PM
            cursor.execute("INSERT INTO reminder_settings (time, last_entry_date) VALUES (?, ?)", 
                          (default_time, None))
        
        conn.commit()
        conn.close()
    
    def add_entry(self, amount, category_name, entry_date=None, note=""):
        """Add a new financial entry to the database."""
        if entry_date is None:
            entry_date = datetime.now().strftime("%Y-%m-%d")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create category
        cursor.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        result = cursor.fetchone()
        if result:
            category_id = result[0]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            category_id = cursor.lastrowid
        
        # Add entry
        cursor.execute(
            "INSERT INTO entries (amount, category_id, entry_date, note) VALUES (?, ?, ?, ?)",
            (amount, category_id, entry_date, note)
        )
        
        # Update last entry date in reminder settings
        cursor.execute("UPDATE reminder_settings SET last_entry_date=? WHERE id=1", (entry_date,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_entries(self, start_date=None, end_date=None):
        """Get entries from database with optional date filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
        SELECT e.id, e.amount, c.name, e.entry_date, e.note 
        FROM entries e
        JOIN categories c ON e.category_id = c.id
        '''
        
        params = []
        if start_date:
            query += " WHERE e.entry_date >= ?"
            params.append(start_date)
            if end_date:
                query += " AND e.entry_date <= ?"
                params.append(end_date)
        elif end_date:
            query += " WHERE e.entry_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY e.entry_date DESC"
        
        cursor.execute(query, params)
        
        # Create list of dictionaries instead of pandas DataFrame
        columns = ["id", "amount", "name", "entry_date", "note"]
        entries = []
        for row in cursor.fetchall():
            entries.append(dict(zip(columns, row)))
        
        conn.close()
        return entries
    
    def update_entry(self, entry_id, amount, category_name, entry_date, note=""):
        """Update an existing entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create category
        cursor.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        result = cursor.fetchone()
        if result:
            category_id = result[0]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            category_id = cursor.lastrowid
        
        # Update entry
        cursor.execute(
            "UPDATE entries SET amount=?, category_id=?, entry_date=?, note=? WHERE id=?",
            (amount, category_id, entry_date, note, entry_id)
        )
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_entry(self, entry_id):
        """Delete an entry by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_categories(self):
        """Get all categories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_reminder_settings(self):
        """Get the current reminder settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT time, last_entry_date FROM reminder_settings WHERE id=1")
        result = cursor.fetchone()
        
        conn.close()
        if result:
            return {"time": result[0], "last_entry_date": result[1]}
        return {"time": "20:00", "last_entry_date": None}
    
    def update_reminder_time(self, time):
        """Update reminder time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE reminder_settings SET time=? WHERE id=1", (time,))
        
        conn.commit()
        conn.close()
        return True