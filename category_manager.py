class CategoryManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_categories(self):
        """Get all available categories."""
        return self.db_manager.get_categories()
    
    def add_category(self, category_name):
        """Add a new category by creating a dummy entry and then removing it."""
        # Check if category already exists
        categories = self.db_manager.get_categories()
        if category_name in categories:
            return False, "Category already exists"
            
        # Add a temporary entry to create the category, then delete it
        # A bit of a hack but it works with the current db structure
        self.db_manager.add_entry(0.0, category_name, None, "Temporary for category creation")
        entries = self.db_manager.get_entries()
        if entries and entries[0]["name"] == category_name:
            self.db_manager.delete_entry(entries[0]["id"])
            return True, "Category created"
            
        return False, "Failed to create category"