"""
Settings Manager - Centralized settings management
"""
import json
import os
import customtkinter as ctk
from datetime import datetime


class SettingsManager:
    """Centralized settings manager"""
    
    _instance = None
    _settings_file = "settings.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.settings = self._load_settings()
        self._apply_theme()
    
    def _load_settings(self):
        """Load settings from file or return defaults"""
        default_settings = {
            "theme": "System",
            "language": "English",
            "date_format": "YYYY-MM-DD",
            "currency": "₹ (INR)",
            "low_stock_alerts": True,
            "expiry_reminders": True,
            "daily_reports": False,
            "payment_reminders": True,
            "backup_frequency": "Daily",
            "export_format": "CSV",
            "auto_save": True,
            "shop_name": "VSG",
            "contact_email": "shop@example.com",
            "phone_number": "+91 98765 43210",
        }
        
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Convert 1/0 to True/False for boolean values
                    for key in loaded:
                        if key in ["low_stock_alerts", "expiry_reminders", "daily_reports", 
                                  "payment_reminders", "auto_save"]:
                            loaded[key] = bool(loaded[key])
                    default_settings.update(loaded)
                    return default_settings
            except:
                return default_settings
        return default_settings
    
    def _apply_theme(self):
        """Apply theme setting"""
        theme = self.settings.get("theme", "System")
        if theme == "System":
            ctk.set_appearance_mode("system")
        elif theme == "Light":
            ctk.set_appearance_mode("light")
        elif theme == "Dark":
            ctk.set_appearance_mode("dark")
        
        # Force update all widgets
        try:
            # This will trigger a refresh of all widgets
            import tkinter as tk
            root = tk._default_root
            if root:
                root.update()
        except:
            pass
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def save(self):
        """Save settings to file"""
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            # Reapply theme if it changed
            self._apply_theme()
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def format_date(self, date_obj):
        """Format date according to user's date format setting"""
        if not date_obj:
            return "N/A"
        
        date_format = self.settings.get("date_format", "YYYY-MM-DD")
        
        try:
            if isinstance(date_obj, str):
                # Try to parse if it's a string
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
            
            if date_format == "YYYY-MM-DD":
                return date_obj.strftime("%Y-%m-%d")
            elif date_format == "DD-MM-YYYY":
                return date_obj.strftime("%d-%m-%Y")
            elif date_format == "MM/DD/YYYY":
                return date_obj.strftime("%m/%d/%Y")
            else:
                return date_obj.strftime("%Y-%m-%d")
        except:
            return str(date_obj)
    
    def format_currency(self, amount):
        """Format currency according to user's currency setting"""
        currency = self.settings.get("currency", "₹ (INR)")
        
        # Extract symbol
        if "₹" in currency or "INR" in currency:
            symbol = "₹"
        elif "$" in currency or "USD" in currency:
            symbol = "$"
        elif "€" in currency or "EUR" in currency:
            symbol = "€"
        elif "£" in currency or "GBP" in currency:
            symbol = "£"
        else:
            symbol = "₹"
        
        return f"{symbol} {amount:.2f}"
    
    def get_currency_symbol(self):
        """Get just the currency symbol"""
        currency = self.settings.get("currency", "₹ (INR)")
        if "₹" in currency or "INR" in currency:
            return "₹"
        elif "$" in currency or "USD" in currency:
            return "$"
        elif "€" in currency or "EUR" in currency:
            return "€"
        elif "£" in currency or "GBP" in currency:
            return "£"
        return "₹"
    
    def reload(self):
        """Reload settings from file"""
        self.settings = self._load_settings()
        self._apply_theme()
        # Force update to ensure theme is applied
        import tkinter as tk
        try:
            root = tk._default_root
            if root:
                root.update_idletasks()
                root.update()
        except:
            pass

