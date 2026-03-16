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
    
    def __init__(self, parent, current_user=None, on_theme_change=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS['background'])
        self.current_user = current_user  # tuple: (id, username, role)
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
        
        # Account Settings Section (only Shop Name now)
        self.create_section(scroll_frame, "Account", [
            ("Shop Name", "Your shop/business name", "shop_name", None),
        ])
        
        # Action Buttons (only Save, aligned to right)
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
        save_btn.pack(side="right", padx=5)
    
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
            right_frame.pack(side="right", padx=(20, 0), pady=(5, 0))
            
            # Create appropriate control based on setting type
            current_value = self.settings.get(setting_key, "")

            # Toggle (switch) settings - always use switch, coerce 1/0 to bool
            toggle_keys = ("low_stock_alerts", "expiry_reminders", "daily_reports", "payment_reminders", "auto_save")
            if setting_key in toggle_keys:
                bool_val = bool(current_value) if current_value not in (None, "") else (setting_key != "daily_reports")
                control = ctk.CTkSwitch(
                    right_frame,
                    text="",
                    width=50,
                    height=20
                )
                control.select() if bool_val else control.deselect()
                control.pack(side="right")
                self.controls[setting_key] = control
                if idx < len(items) - 1:
                    divider = ctk.CTkFrame(section_frame, fg_color=COLORS['background'], height=1)
                    divider.pack(fill="x", padx=20, pady=(0, 0))
                continue

            # Special handling for shop name: label + Change button with password check
            if setting_key == "shop_name":
                name_value = str(current_value or "")
                value_label = ctk.CTkLabel(
                    right_frame,
                    text=name_value or "Not set",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text'],
                    anchor="e",
                )
                value_label.pack(anchor="e", pady=(0, 6))

                change_btn = ctk.CTkButton(
                    right_frame,
                    text="Change",
                    width=90,
                    height=32,
                    fg_color=COLORS['primary'],
                    hover_color=COLORS['primary_dark'],
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda: self.open_change_shop_name_dialog(value_label),
                )
                change_btn.pack(anchor="e")

                self.controls[setting_key] = value_label
                continue
            
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
            elif isinstance(control, ctk.CTkLabel):
                current[key] = control.cget("text")
        return current
    
    def save_settings(self):
        """Save settings"""
        # Get current values from controls
        new_settings = self.get_current_settings()
        # Track old values BEFORE updating self.settings
        old_shop_name = self.settings.get("shop_name", "VSG")
        old_theme = self.settings.get("theme", "System")

        # Apply new in-memory settings
        self.settings.update(new_settings)
        
        # Update settings manager
        for key, value in new_settings.items():
            self.settings_manager.set(key, value)
        
        # Check if theme or shop name changed
        new_theme = new_settings.get("theme", "System")
        theme_changed = old_theme != new_theme
        new_shop_name = new_settings.get("shop_name", old_shop_name)
        shop_name_changed = new_shop_name != old_shop_name
        
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

                # Also refresh header/logo and profile shop name if it changed
                if shop_name_changed:
                    try:
                        root = self.winfo_toplevel()
                        if hasattr(root, "header"):
                            root.header.update_colors()
                        if hasattr(root, "pages") and isinstance(root.pages, dict):
                            profile_page = root.pages.get("profile")
                            if profile_page and hasattr(profile_page, "reload_profile"):
                                profile_page.reload_profile()
                    except Exception:
                        pass
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

    # ------------------------------------------------------------------
    # Account helpers
    # ------------------------------------------------------------------
    def _get_user_email(self):
        """Fetch current user's email from main users table, if any."""
        if not self.current_user:
            return None
        try:
            from config import DB_PATH
            from database import Database
            db = Database(DB_PATH)
            db.connect()
            row = db.fetch_one("SELECT email FROM users WHERE id = ?", (self.current_user[0],))
            if row and len(row) > 0:
                return row[0]
        except Exception:
            return None
        return None

    def open_change_shop_name_dialog(self, value_label):
        """Open dialog to change shop name with password confirmation."""
        if not self.current_user:
            messagebox.showerror("Error", "User information not available.")
            return

        from config import DB_PATH
        from database import Database

        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Shop Name")
        # Extra height so fields + buttons always visible
        dialog.geometry("520x380")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color=COLORS['surface'])
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        title = ctk.CTkLabel(
            frame,
            text="Change Shop Name",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        info = ctk.CTkLabel(
            frame,
            text="Enter a new shop name and confirm with your account password.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light'],
            wraplength=420,
            justify="left",
        )
        info.pack(anchor="w", padx=10, pady=(0, 15))

        name_label = ctk.CTkLabel(
            frame,
            text="New Shop Name",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        name_label.pack(fill="x", padx=10, pady=(0, 3))

        name_entry = ctk.CTkEntry(frame, height=38, font=ctk.CTkFont(size=12))
        current_name = value_label.cget("text")
        if current_name and current_name != "Not set":
            name_entry.insert(0, current_name)
        name_entry.pack(fill="x", padx=10, pady=(0, 10))

        pwd_label = ctk.CTkLabel(
            frame,
            text="Current Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        pwd_label.pack(fill="x", padx=10, pady=(8, 3))

        pwd_entry = ctk.CTkEntry(frame, height=38, font=ctk.CTkFont(size=12), show="*")
        pwd_entry.pack(fill="x", padx=10, pady=(0, 10))

        error_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['error'],
        )
        error_label.pack(anchor="w", padx=10, pady=(0, 8))

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.pack(fill="x", padx=10, pady=(8, 4))

        def do_close():
            dialog.destroy()

        def do_save():
            new_name = name_entry.get().strip()
            password = pwd_entry.get().strip()

            if not new_name or not password:
                error_label.configure(text="Please enter both shop name and password.")
                return

            try:
                db = Database(DB_PATH)
                db.connect()
                row = db.fetch_one(
                    "SELECT password FROM users WHERE id = ?",
                    (self.current_user[0],),
                )
                if not row or row[0] != password:
                    error_label.configure(text="Password is incorrect.")
                    return

                # Save in settings
                self.settings_manager.set("shop_name", new_name)
                self.settings_manager.save()
                value_label.configure(text=new_name)

                messagebox.showinfo("Shop Name Updated", "Your shop name has been updated.")
                dialog.destroy()
            except Exception as e:
                error_label.configure(text=f"Error: {e}")

        cancel_btn = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="transparent",
            border_color=COLORS['secondary'],
            border_width=1,
            hover_color=COLORS['background'],
            text_color=COLORS['text'],
            height=32,
            font=ctk.CTkFont(size=12),
            command=do_close,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            buttons,
            text="Save",
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color="white",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=do_save,
        )
        save_btn.pack(side="right")

        name_entry.focus_set()
    def open_change_email_dialog(self, value_label):
        """Open dialog to change contact email with password confirmation."""
        if not self.current_user:
            messagebox.showerror("Error", "User information not available.")
            return

        from config import DB_PATH
        from database import Database

        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Contact Email")
        # Make window larger so everything (including buttons) is visible
        dialog.geometry("480x380")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Content frame (no scroll, bigger window instead)
        frame = ctk.CTkFrame(dialog, fg_color=COLORS['surface'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            frame,
            text="Change Contact Email",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        info = ctk.CTkLabel(
            frame,
            text="Enter a new email address and confirm with your account password.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light'],
            wraplength=360,
            justify="left",
        )
        info.pack(anchor="w", padx=10, pady=(0, 15))

        # Email entry
        email_label = ctk.CTkLabel(
            frame,
            text="New Email",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        email_label.pack(fill="x", padx=10, pady=(0, 3))

        email_entry = ctk.CTkEntry(frame, height=36, font=ctk.CTkFont(size=12))
        current_email = self._get_user_email() or value_label.cget("text")
        if current_email and current_email != "Not set":
            email_entry.insert(0, current_email)
        email_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Password entry
        pwd_label = ctk.CTkLabel(
            frame,
            text="Current Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        pwd_label.pack(fill="x", padx=10, pady=(10, 3))

        pwd_entry = ctk.CTkEntry(
            frame,
            height=36,
            font=ctk.CTkFont(size=12),
            show="*",
        )
        pwd_entry.pack(fill="x", padx=10, pady=(0, 10))

        error_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['error'],
        )
        error_label.pack(anchor="w", padx=10, pady=(0, 8))

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.pack(fill="x", padx=10, pady=(10, 0))

        def do_close():
            dialog.destroy()

        def do_save():
            new_email = email_entry.get().strip()
            password = pwd_entry.get().strip()

            if not new_email or not password:
                error_label.configure(text="Please enter both email and password.")
                return

            if "@" not in new_email or "." not in new_email:
                error_label.configure(text="Please enter a valid email address.")
                return

            try:
                db = Database(DB_PATH)
                db.connect()
                row = db.fetch_one(
                    "SELECT password FROM users WHERE id = ?",
                    (self.current_user[0],),
                )
                if not row or row[0] != password:
                    error_label.configure(text="Password is incorrect.")
                    return

                if not db.execute_query(
                    "UPDATE users SET email = ? WHERE id = ?",
                    (new_email, self.current_user[0]),
                ):
                    error_label.configure(text="Failed to update email. Please try again.")
                    return

                # Update settings contact_email as well
                self.settings_manager.set("contact_email", new_email)
                self.settings_manager.save()
                value_label.configure(text=new_email)

                # Also refresh Profile page (if it exists) so email shows updated value
                try:
                    root = self.winfo_toplevel()
                    if hasattr(root, "pages") and isinstance(root.pages, dict):
                        profile_page = root.pages.get("profile")
                        if profile_page and hasattr(profile_page, "reload_profile"):
                            profile_page.reload_profile()
                except Exception:
                    pass

                messagebox.showinfo("Email Updated", "Your contact email has been updated.")
                dialog.destroy()
            except Exception as e:
                error_label.configure(text=f"Error: {e}")

        cancel_btn = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="transparent",
            border_color=COLORS['secondary'],
            border_width=1,
            hover_color=COLORS['background'],
            text_color=COLORS['text'],
            height=32,
            font=ctk.CTkFont(size=12),
            command=do_close,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            buttons,
            text="Save",
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color="white",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=do_save,
        )
        save_btn.pack(side="right")

        email_entry.focus_set()
        dialog.wait_window()
