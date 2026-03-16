"""
Main application entry point for VyapaarSetGo
"""
import customtkinter as ctk
from tkinter import messagebox
import os
from database import Database
from modules.login import LoginFrame
from modules.dashboard import Dashboard
from modules.inventory import Inventory
from modules.suppliers import Suppliers
from modules.khata import Khata
from modules.sales import Sales
from modules.reports import Reports
from modules.profile import Profile
from modules.help import Help
from modules.faq import FAQ
from modules.about import About
from modules.settings import Settings
from modules.notifications import Notifications, check_low_stock, check_expiry_reminders, check_payment_reminders
from modules.splash import SplashScreen
from components.sidebar import Sidebar
from components.header import Header
from config import COLORS, APP_NAME, DB_PATH, settings_manager


class MainApplication(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.current_page = None
        self.pages = {}
        self.login_container = None
        self.splash_container = None
        self.db = None  # Will be initialized after login
        self.user_db_path = None  # User-specific database path
        
        # Initialize main database (for users table only)
        self.main_db = Database(DB_PATH)
        if not self.main_db.connect():
            print("Warning: Could not connect to database. Please check your SQLite configuration.")
        # Initialize main database tables
        self.main_db.initialize_database()
        
        self.setup_window()
        # Show splash screen before login
        self.show_splash()
    
    def setup_window(self):
        """Configure main window"""
        self.title(f"{APP_NAME} - Smart Grocery Management")
        self.geometry("1400x800")
        # Use dynamic colors
        self.configure(fg_color=COLORS['background'])
        
        # Update colors when theme changes
        self.bind("<Configure>", lambda e: self._update_colors())
    
    def _update_colors(self):
        """Update window colors based on current theme"""
        try:
            self.configure(fg_color=COLORS['background'])
        except:
            pass
    
    def show_login(self):
        """Show login form in the main window"""
        # Clear any existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create login frame directly in main window
        self.login_container = LoginFrame(self, self.on_login_success)
        self.login_container.pack(expand=True, fill="both")

    def show_splash(self):
        """Show splash screen before login"""
        for widget in self.winfo_children():
            widget.destroy()

        self.splash_container = SplashScreen(self, self.show_login)
        self.splash_container.pack(expand=True, fill="both")
    
    def on_login_success(self, user):
        """Handle successful login - transform window to desktop app"""
        self.current_user = user
        user_id = user[0]  # Get user ID
        
        # Create user-specific database path
        import os
        user_db_dir = "user_databases"
        if not os.path.exists(user_db_dir):
            os.makedirs(user_db_dir)
        
        self.user_db_path = os.path.join(user_db_dir, f"user_{user_id}.db")
        
        # Initialize user-specific database
        self.db = Database(self.user_db_path)
        if not self.db.connect():
            messagebox.showerror("Error", "Could not connect to your database. Please try again.")
            return
        
        # Initialize user-specific database tables (without users table)
        self.db.initialize_user_database()
        
        # Check for notifications on login (respect settings)
        check_low_stock(self.db)
        check_expiry_reminders(self.db)
        check_payment_reminders(self.db)
        
        # Clear login content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Setup desktop application UI
        self.setup_main_ui()
        # Navigate to dashboard
        self.navigate_to_page("dashboard")
    
    def setup_main_ui(self):
        """Setup main application UI"""
        # Ensure appearance mode is set before creating any widgets
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        theme = settings.get("theme", "System")
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        # Force update to ensure appearance mode is applied
        self.update_idletasks()
        self.update()
        
        # Import COLORS fresh to get updated values
        from config import COLORS
        
        # Sidebar - add top padding so it visually aligns
        # with the header and main content cards.
        self.sidebar = Sidebar(self, self.navigate_to_page)
        self.sidebar.pack(side="left", fill="y", pady=(10, 0))
        
        # Main content area
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS['background'])
        self.main_container.pack(side="right", fill="both", expand=True)
        
        # Header
        user_name = self.current_user[1] if self.current_user else ""
        self.header = Header(
            self.main_container,
            "Dashboard",
            user_name=user_name,
            on_profile_click=lambda: self.navigate_to_page("profile"),
        )
        # Add horizontal padding so the header aligns with
        # the dashboard cards, and a small top margin.
        self.header.pack(fill="x", padx=20, pady=(10, 0))
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['background'])
        self.content_frame.pack(fill="both", expand=True)
        
        # Initialize all pages
        self.initialize_pages()
    
    def initialize_pages(self):
        """Initialize all application pages"""
        # Ensure appearance mode is set before creating pages
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        theme = settings.get("theme", "System")
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        # Force update to ensure appearance mode is applied
        self.update_idletasks()
        
        # Now create all pages with correct theme and user-specific database
        self.pages = {
            "dashboard": Dashboard(self.content_frame, on_navigate=self.navigate_to_page, db=self.db),
            "inventory": Inventory(self.content_frame, db=self.db),
            "khata": Khata(self.content_frame, db=self.db),
            "suppliers": Suppliers(self.content_frame, db=self.db),
            "sales": Sales(self.content_frame, db=self.db, on_data_change=self.refresh_pages_after_sale),
            "reports": Reports(self.content_frame, db=self.db),
            "notifications": Notifications(self.content_frame, db=self.db),
            "profile": Profile(self.content_frame, self.current_user, db=self.db),
            "help": Help(self.content_frame, on_navigate=self.navigate_to_page),
            "faq": FAQ(self.content_frame),
            "about": About(self.content_frame),
            "settings": Settings(self.content_frame, current_user=self.current_user, on_theme_change=self.refresh_app_theme),
        }
        
        # Check for notifications after pages are initialized (respect settings)
        def run_notification_checks():
            check_low_stock(self.db)
            check_expiry_reminders(self.db)
            check_payment_reminders(self.db)
        self.after(500, run_notification_checks)
    
    def refresh_pages_after_sale(self):
        """Refresh all pages after a sale transaction"""
        # Refresh dashboard if it exists
        if "dashboard" in self.pages:
            try:
                dashboard = self.pages["dashboard"]
                # Clear existing widgets and reload
                for widget in dashboard.winfo_children():
                    widget.destroy()
                dashboard.setup_dashboard()
                dashboard.load_data()
                # If dashboard is currently visible, update it
                if self.current_page == dashboard:
                    dashboard.update_idletasks()
            except Exception as e:
                print(f"Error refreshing dashboard: {e}")
        
        # Refresh inventory to show updated stock
        if "inventory" in self.pages:
            try:
                inventory = self.pages["inventory"]
                if hasattr(inventory, 'load_products'):
                    inventory.load_products()
                # If inventory is currently visible, update it
                if self.current_page == inventory:
                    inventory.update_idletasks()
            except Exception as e:
                print(f"Error refreshing inventory: {e}")
        
        # Refresh customer Khata so balances reflect the latest sale
        if "khata" in self.pages:
            try:
                khata = self.pages["khata"]
                if hasattr(khata, 'load_customers'):
                    khata.load_customers()
                if self.current_page == khata:
                    khata.update_idletasks()
            except Exception as e:
                print(f"Error refreshing khata: {e}")
        
        # Refresh notifications to check for new low stock alerts
        if "notifications" in self.pages:
            try:
                notifications = self.pages["notifications"]
                if hasattr(notifications, 'load_notifications'):
                    notifications.load_notifications()
                # If notifications is currently visible, update it
                if self.current_page == notifications:
                    notifications.update_idletasks()
            except Exception as e:
                print(f"Error refreshing notifications: {e}")
        
        # Refresh sales page to show updated product stock
        if "sales" in self.pages:
            try:
                sales = self.pages["sales"]
                if hasattr(sales, 'load_products'):
                    sales.load_products()
            except Exception as e:
                print(f"Error refreshing sales: {e}")
    
    def refresh_app_theme(self):
        """Refresh entire app when theme changes"""
        if not hasattr(self, 'main_container'):
            return  # Not logged in yet
        
        # Store current page
        current_page_id = None
        for page_id, page in self.pages.items():
            if page == self.current_page:
                current_page_id = page_id
                break
        
        # Step 1: Reload settings to get latest theme
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.reload()  # Reload to get latest settings
        theme = settings.get("theme", "System")
        
        # Step 2: Set appearance mode
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        # Step 3: Force multiple updates to ensure appearance mode propagates
        for _ in range(3):
            self.update_idletasks()
            self.update()
        
        # Step 4: Destroy and recreate after delay (longer delay for CustomTkinter to process)
        self.after(300, lambda: self._destroy_and_recreate(current_page_id))
    
    def _destroy_and_recreate(self, current_page_id):
        """Destroy all widgets and recreate with new theme"""
        # Double-check appearance mode is set
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        theme = settings.get("theme", "System")
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        # Force update
        self.update_idletasks()
        self.update()
        
        # Update main window background
        from config import COLORS
        self.configure(fg_color=COLORS['background'])
        self.update()
        
        # Destroy all pages
        for page_id, page in list(self.pages.items()):
            try:
                if page.winfo_exists():
                    page.pack_forget()
                    page.destroy()
            except:
                pass
        
        # Destroy sidebar, header, and containers
        try:
            if hasattr(self, 'sidebar') and self.sidebar.winfo_exists():
                self.sidebar.pack_forget()
                self.sidebar.destroy()
        except:
            pass
        try:
            if hasattr(self, 'header') and self.header.winfo_exists():
                self.header.pack_forget()
                self.header.destroy()
        except:
            pass
        try:
            if hasattr(self, 'main_container') and self.main_container.winfo_exists():
                self.main_container.pack_forget()
                self.main_container.destroy()
        except:
            pass
        
        # Force multiple updates to ensure widgets are destroyed
        for _ in range(5):
            self.update_idletasks()
            self.update()
        
        # Clear pages dict
        self.pages = {}
        self.current_page = None
        
        # Wait longer for CustomTkinter to fully process the appearance mode change
        self.after(300, lambda: self._complete_refresh(current_page_id))
    
    def _complete_refresh(self, current_page_id):
        """Complete the theme refresh by recreating UI"""
        # Ensure appearance mode is definitely set
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.reload()
        theme = settings.get("theme", "System")
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        # CRITICAL: Force CustomTkinter to process the appearance mode change
        # This is essential for widgets to get the correct default colors
        for _ in range(10):
            self.update_idletasks()
            self.update()
        
        # Small additional delay to ensure appearance mode is fully propagated
        self.after(100, lambda: self._recreate_ui(current_page_id))
    
    def _recreate_ui(self, current_page_id):
        """Recreate the UI with new theme"""
        # Update main window background first
        from config import COLORS
        self.configure(fg_color=COLORS['background'])
        self.update()
        
        # Recreate main UI with new theme - this will use fresh COLORS
        self.setup_main_ui()
        
        # Force multiple updates
        for _ in range(10):
            self.update_idletasks()
            self.update()
        
        # Navigate back to the page we were on (or settings if that's where we were)
        if current_page_id:
            self.navigate_to_page(current_page_id)
        else:
            self.navigate_to_page("settings")
        
        # Final updates to ensure everything is rendered
        for _ in range(10):
            self.update_idletasks()
            self.update()
    
    def _update_pages_database(self):
        """Update all pages to use user-specific database"""
        if not self.db:
            return
        
        # Update database for pages that need it
        for page_id, page in self.pages.items():
            if hasattr(page, 'db'):
                page.db = self.db
            # Re-initialize if needed
            if hasattr(page, 'load_data'):
                try:
                    page.load_data()
                except:
                    pass
            elif hasattr(page, 'load_products'):
                try:
                    page.load_products()
                except:
                    pass
    
    def navigate_to_page(self, page_id, topic=None):
        """Navigate to a specific page"""
        if page_id == "logout":
            if self.confirm_logout():
                # Clear desktop UI and show login again
                for widget in self.winfo_children():
                    widget.destroy()
                self.current_user = None
                self.current_page = None
                self.pages = {}
                self.show_login()
            return
        
        # Hide current page
        if self.current_page:
            self.current_page.pack_forget()
        
        # Show new page
        if page_id in self.pages:
            # Hide current page
            if self.current_page:
                self.current_page.pack_forget()
            
            # If FAQ page and topic provided, recreate with topic
            if page_id == "faq" and topic:
                # Remove old FAQ page
                if "faq" in self.pages:
                    self.pages["faq"].destroy()
                # Create new FAQ page with topic
                self.pages["faq"] = FAQ(self.content_frame, selected_topic=topic)
            
            self.current_page = self.pages[page_id]
            self.current_page.pack(fill="both", expand=True)
            
            # Update header title
            page_titles = {
                "dashboard": "Dashboard",
                "inventory": "Inventory Management",
                "khata": "Customer Khata",
                "suppliers": "Supplier Management",
                "sales": "Sales / Billing",
                "reports": "Reports",
                "notifications": "Notifications",
                "profile": "My Profile",
                "help": "Help & Support",
                "faq": "Frequently Asked Questions",
                "about": "About",
                "settings": "Settings",
            }
            self.header.update_title(page_titles.get(page_id, "Dashboard"))
    
    def confirm_logout(self):
        """Confirm logout"""
        from tkinter import messagebox
        return messagebox.askyesno("Logout", "Are you sure you want to logout?")
    
    def on_closing(self):
        """Handle window closing"""
        if self.db:
            self.db.disconnect()
        self.destroy()


def main():
    """Main entry point"""

    # Initialize main database ONLY if first time
    if not os.path.exists(DB_PATH):
        db = Database(DB_PATH)
        if db.connect():
            db.initialize_database()
            db.disconnect()

    # Start application
    app = MainApplication()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
