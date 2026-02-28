"""
Settings module
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from utils.settings_manager import SettingsManager
import json
import os


class Settings(ctk.CTkFrame):
    """Settings page"""
    
    def __init__(self, parent, on_theme_change=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS['background'])
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings.copy()
        self.controls = {}  # Store references to all controls
        self.on_theme_change = on_theme_change  # Callback for theme changes
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['background'])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(anchor="w", pady=(0, 30))
        
        # General Settings Section
        self.create_section(scroll_frame, "General Settings", [
            ("Theme", "Appearance", "theme", ["System", "Light", "Dark"]),
            ("Language", "Application Language", "language", ["English", "Hindi", "Gujarati", "Marathi"]),
            ("Date Format", "Date Display Format", "date_format", ["YYYY-MM-DD", "DD-MM-YYYY", "MM/DD/YYYY"]),
            ("Currency", "Default Currency", "currency", ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"]),
        ])
        
        # Notification Settings Section
        self.create_section(scroll_frame, "Notifications", [
            ("Low Stock Alerts", "Get notified when stock is low", "low_stock_alerts", None),
            ("Expiry Reminders", "Get notified before products expire", "expiry_reminders", None),
            ("Daily Reports", "Receive daily sales reports", "daily_reports", None),
            ("Payment Reminders", "Get reminders for pending payments", "payment_reminders", None),
        ])
        
        # Data Management Section
        self.create_section(scroll_frame, "Data Management", [
            ("Backup Frequency", "Automatic backup schedule", "backup_frequency", ["Daily", "Weekly", "Monthly", "Never"]),
            ("Export Format", "Data export format", "export_format", ["CSV", "Excel", "JSON"]),
            ("Auto-save", "Automatically save changes", "auto_save", None),
        ])
        
        # Account Settings Section
        self.create_section(scroll_frame, "Account", [
            ("Shop Name", "Your shop/business name", "shop_name", None),
            ("Contact Email", "Primary contact email", "contact_email", None),
            ("Phone Number", "Contact phone number", "phone_number", None),
        ])
        
        # Action Buttons
        buttons_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(30, 0))
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", padx=5)
        
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_settings,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        reset_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            buttons_frame,
            text="📤 Export Settings",
            command=self.export_settings,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        export_btn.pack(side="left", padx=5)
    
    def create_section(self, parent, section_title, items):
        """Create a settings section with editable controls"""
        section_frame = ctk.CTkFrame(parent, fg_color=COLORS['surface'], corner_radius=12)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=section_title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Section items
        for idx, item in enumerate(items):
            item_title, item_desc, setting_key, options = item
            item_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=10)
            
            # Left side - title and description
            left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True)
            
            item_title_label = ctk.CTkLabel(
                left_frame,
                text=item_title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text'],
                anchor="w"
            )
            item_title_label.pack(anchor="w", pady=(0, 3))
            
            item_desc_label = ctk.CTkLabel(
                left_frame,
                text=item_desc,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
                anchor="w"
            )
            item_desc_label.pack(anchor="w")
            
            # Right side - value/control
            right_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            right_frame.pack(side="right", padx=(20, 0))
            
            # Create appropriate control based on setting type
            current_value = self.settings.get(setting_key, "")
            
            if options is not None:
                # Dropdown/ComboBox for options
                control = ctk.CTkComboBox(
                    right_frame,
                    values=options,
                    width=180,
                    height=35,
                    font=ctk.CTkFont(size=12),
                    state="readonly"
                )
                control.set(str(current_value))
                control.pack(side="right")
            elif isinstance(current_value, bool):
                # Switch for boolean settings
                control = ctk.CTkSwitch(
                    right_frame,
                    text="",
                    width=50,
                    height=20
                )
                control.select() if current_value else control.deselect()
                control.pack(side="right")
            else:
                # Entry field for text settings
                control = ctk.CTkEntry(
                    right_frame,
                    width=200,
                    height=35,
                    font=ctk.CTkFont(size=12)
                )
                control.insert(0, str(current_value))
                control.pack(side="right")
            
            # Store control reference
            self.controls[setting_key] = control
            
            # Divider (except for last item)
            if idx < len(items) - 1:
                divider = ctk.CTkFrame(section_frame, fg_color=COLORS['background'], height=1)
                divider.pack(fill="x", padx=20, pady=(0, 0))
    
    def get_current_settings(self):
        """Get current values from all controls"""
        current = {}
        for key, control in self.controls.items():
            if isinstance(control, ctk.CTkSwitch):
                current[key] = control.get()
            elif isinstance(control, ctk.CTkComboBox):
                current[key] = control.get()
            elif isinstance(control, ctk.CTkEntry):
                current[key] = control.get()
        return current
    
    def save_settings(self):
        """Save settings"""
        # Get current values from controls
        new_settings = self.get_current_settings()
        self.settings.update(new_settings)
        
        # Update settings manager
        for key, value in new_settings.items():
            self.settings_manager.set(key, value)
        
        # Check if theme changed
        old_theme = self.settings.get("theme", "System")
        new_theme = new_settings.get("theme", "System")
        theme_changed = old_theme != new_theme
        
        # Save to file and apply changes
        if self.settings_manager.save():
            # Apply theme immediately
            if new_theme == "Dark":
                ctk.set_appearance_mode("dark")
            elif new_theme == "Light":
                ctk.set_appearance_mode("light")
            else:
                ctk.set_appearance_mode("system")
            
            # Reload settings manager
            self.settings_manager.reload()
            
            if theme_changed and self.on_theme_change:
                # Show message first
                messagebox.showinfo(
                    "Settings Saved", 
                    "Your settings have been saved successfully!\n\n"
                    "Refreshing the entire application to apply the new theme..."
                )
                # Trigger full app refresh after messagebox closes (longer delay to ensure messagebox is closed)
                self.after(100, self.on_theme_change)
            else:
                messagebox.showinfo(
                    "Settings Saved", 
                    "Your settings have been saved successfully!"
                )
                # Just refresh the settings page
                for widget in self.winfo_children():
                    widget.destroy()
                self.setup_ui()
        else:
            messagebox.showerror("Error", "Failed to save settings. Please try again.")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset to default values
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
            
            self.settings = default_settings.copy()
            
            # Update all controls
            for key, control in self.controls.items():
                value = default_settings.get(key, "")
                if isinstance(control, ctk.CTkSwitch):
                    control.select() if value else control.deselect()
                elif isinstance(control, ctk.CTkComboBox):
                    control.set(str(value))
                elif isinstance(control, ctk.CTkEntry):
                    control.delete(0, "end")
                    control.insert(0, str(value))
            
            # Update settings manager and save
            for key, value in default_settings.items():
                self.settings_manager.set(key, value)
            self.settings_manager.save()
            messagebox.showinfo("Settings Reset", "All settings have been reset to their default values.")
    
    def export_settings(self):
        """Export settings to a file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Settings"
        )
        
        if filename:
            try:
                current_settings = self.get_current_settings()
                with open(filename, 'w') as f:
                    json.dump(current_settings, f, indent=2)
                messagebox.showinfo("Settings Exported", f"Your settings have been exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
