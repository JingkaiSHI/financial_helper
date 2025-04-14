import datetime
import time
import threading
import platform
import subprocess
import os

class ReminderManager:
    def __init__(self, db_manager, trigger_callback=None):
        self.db_manager = db_manager
        self.trigger_callback = trigger_callback
        self.reminder_thread = None
        self.running = False
    
    def start_reminder_service(self):
        """Start the reminder service in a separate thread."""
        self.running = False
        self.running = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
    
    def stop_reminder_service(self):
        """Stop the reminder service."""
        self.running = False
        if self.reminder_thread and self.reminder_thread.is_alive():
            # Try to join with timeout
            try:
                self.reminder_thread.join(timeout=0.1)
            except Exception:
                pass
    
    def _reminder_loop(self):
        """Background loop checking if reminder should be triggered."""
        while self.running:
            settings = self.db_manager.get_reminder_settings()
            reminder_time = settings["time"]
            last_entry_date = settings["last_entry_date"]
            
            # Check if we need to show reminder
            current_datetime = datetime.datetime.now()
            current_date = current_datetime.strftime("%Y-%m-%d")
            current_time = current_datetime.strftime("%H:%M")
            
            # Show reminder if:
            # 1. Current time is at or after reminder time
            # 2. No entry has been made today
            if current_time >= reminder_time and last_entry_date != current_date:
                if self.trigger_callback:
                    self.trigger_callback()
                else:
                    self._show_notification("Financial Helper Reminder", 
                                         "Don't forget to record your financial activity today!")
            
            # Sleep for a minute before checking again
            time.sleep(60)
    
    def _show_notification(self, title, message):
        """Show a system notification."""
        if platform.system() == "Darwin":  # macOS
            script = f'''
            osascript -e 'display notification "{message}" with title "{title}"'
            '''
            subprocess.run(script, shell=True)
        elif platform.system() == "Linux":
            subprocess.run(['notify-send', title, message])
        elif platform.system() == "Windows":
            # Windows implementation would go here
            pass
    
    def check_if_reminder_needed(self):
        """Check if a reminder is currently needed (for initial app startup)."""
        settings = self.db_manager.get_reminder_settings()
        last_entry_date = settings["last_entry_date"]
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # If no entry today, reminder is needed
        return last_entry_date != current_date