"""
Configuration file for VyapaarSetGo application
"""
import customtkinter as ctk
from utils.settings_manager import SettingsManager

# Initialize settings manager
settings_manager = SettingsManager()

# Global app font family (change this to switch fonts everywhere)
APP_FONT_FAMILY = "Poppins"

# Monkey-patch CTkFont so that whenever no family is given,
# our global app font family is used instead.
_OriginalCTkFont = ctk.CTkFont


def AppFont(*args, **kwargs):
    if "family" not in kwargs or not kwargs.get("family"):
        kwargs["family"] = APP_FONT_FAMILY
    return _OriginalCTkFont(*args, **kwargs)


ctk.CTkFont = AppFont


def app_font(size=12, weight="normal"):
    """Helper for creating app fonts with the global family."""
    return ctk.CTkFont(size=size, weight=weight)


# CustomTkinter appearance settings (will be overridden by settings manager)
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

# Get current theme and apply it
current_theme = settings_manager.get("theme", "System")
if current_theme == "Dark":
    ctk.set_appearance_mode("dark")
elif current_theme == "Light":
    ctk.set_appearance_mode("light")
else:
    ctk.set_appearance_mode("system")

# Color scheme - Dynamic based on theme
class Colors:
    """Dynamic color class that returns colors based on current theme"""
    
    def __init__(self):
        self._settings_manager = SettingsManager()
    
    def _is_dark(self):
        """Check if dark mode is active"""
        # First check settings (most reliable source of truth)
        theme = self._settings_manager.get("theme", "System")
        if theme == "Dark":
            return True
        elif theme == "Light":
            return False
        
        # For System theme, check actual appearance mode
        try:
            app_mode = ctk.get_appearance_mode()
            if app_mode == "Dark":
                return True
            elif app_mode == "Light":
                return False
            else:
                # System mode - default to light
                return False
        except:
            # Fallback to light
            return False
    
    def _get_colors(self):
        """Get colors based on current theme"""
        is_dark = self._is_dark()
        
        if is_dark:
            # Dark theme colors
            return {
                'primary': '#22c55e',  # Green
                'primary_dark': '#16a34a',
                'secondary': '#6b7280',  # Gray
                'background': '#1a1a1a',  # Very dark gray
                'surface': '#2a2a2a',  # Dark gray
                'surface_hover': '#353535',  # Lighter dark gray for hover
                'text': '#e5e7eb',  # Light gray text
                'text_light': '#9ca3af',  # Lighter gray text
                'error': '#ef4444',
                'warning': '#f59e0b',
                'success': '#22c55e',
                'border': '#404040',  # Border color for dark theme
            }
        else:
            # Light theme colors
            return {
                'primary': '#22c55e',  # Green
                'primary_dark': '#16a34a',
                'secondary': '#6b7280',  # Gray
                'background': '#f3f4f6',
                'surface': '#ffffff',
                'surface_hover': '#f9fafb',  # Light gray for hover
                'text': '#1f2937',
                'text_light': '#6b7280',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'success': '#22c55e',
                'border': '#e5e7eb',  # Border color for light theme
            }
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return self._get_colors()[key]
    
    def get(self, key, default=None):
        """Get color with default"""
        return self._get_colors().get(key, default)
    
    def keys(self):
        """Return color keys"""
        return self._get_colors().keys()
    
    def values(self):
        """Return color values"""
        return self._get_colors().values()
    
    def items(self):
        """Return color items"""
        return self._get_colors().items()

# Create colors instance
COLORS = Colors()

# Database configuration (SQLite)
DB_PATH = "vyapaarsetgo.db"  # SQLite database file path

# Application settings
APP_NAME = "VyapaarSetGo"
APP_VERSION = "1.0.0"
