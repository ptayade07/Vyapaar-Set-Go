"""User profile page for VyapaarSetGo"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config import COLORS, DB_PATH
from database import Database
from PIL import Image, ImageOps, ImageDraw
import os
import shutil


class Profile(ctk.CTkFrame):
    """Profile view for the logged-in user"""

    def __init__(self, parent, user, db=None):
        super().__init__(parent, fg_color=COLORS["background"])
        self.user = user  # expected tuple: (id, username, role)
        self.db = db if db else Database(DB_PATH)
        if not db:
            if not self.db.connection:
                self.db.connect()
        self.setup_ui()

    def reload_profile(self):
        """Reload profile UI from latest database values."""
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        """Setup profile page UI"""
        from config import COLORS
        # Main scrollable container
        main_container = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"])
        main_container.pack(expand=True, fill="both", padx=40, pady=40)

        # Header Section
        header_frame = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        header_frame.pack(fill="x", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=24, pady=24)

        title = ctk.CTkLabel(
            header_content,
            text="My Profile",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ctk.CTkLabel(
            header_content,
            text="Manage your account information and preferences",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"],
        )
        subtitle.pack(anchor="w")

        # Main Profile Card (single column, centered feel)
        profile_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        profile_card.pack(fill="x", pady=(0, 20))

        profile_content = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_content.pack(fill="x", padx=24, pady=24)

        # Avatar and Basic Info
        top_section = ctk.CTkFrame(profile_content, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 24))

        username = self.user[1] if self.user else "User"
        role = self.user[2] if self.user and len(self.user) > 2 else "Shop Owner"

        # Load avatar path and profile info from main users database (same as login)
        self.avatar_image = None
        avatar_path = None
        display_name = username
        phone_from_db = None
        email_from_db = None
        if self.user:
            try:
                from config import DB_PATH as MAIN_DB_PATH
                from database import Database as MainDB
                main_db = MainDB(MAIN_DB_PATH)
                main_db.connect()
                row = main_db.fetch_one(
                    "SELECT avatar_path, full_name, phone, email FROM users WHERE id = ?",
                    (self.user[0],),
                )
                if row:
                    avatar_path = row[0]
                    if len(row) > 1 and row[1]:
                        display_name = row[1]
                    if len(row) > 2 and row[2]:
                        phone_from_db = row[2]
                    if len(row) > 3 and row[3]:
                        email_from_db = row[3]
            except Exception:
                avatar_path = None

        # Large Avatar
        avatar_bg_color = COLORS["primary"] if not (avatar_path and os.path.exists(avatar_path)) else "transparent"
        avatar_frame = ctk.CTkFrame(
            top_section,
            fg_color=avatar_bg_color,
            corner_radius=999,
            width=100,
            height=100,
        )
        avatar_frame.pack(side="left")
        avatar_frame.pack_propagate(False)

        if avatar_path and os.path.exists(avatar_path):
            try:
                img = Image.open(avatar_path).convert("RGBA")
                # Make image square and fit, then apply circular mask so it doesn't look square in the circle
                size = (90, 90)
                img = ImageOps.fit(img, size, Image.LANCZOS)
                mask = Image.new("L", size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size[0], size[1]), fill=255)
                img.putalpha(mask)
                self.avatar_image = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                avatar_label = ctk.CTkLabel(avatar_frame, image=self.avatar_image, text="")
            except Exception:
                initials = username[:1].upper() if username else "U"
                avatar_label = ctk.CTkLabel(
                    avatar_frame,
                    text=initials,
                    font=ctk.CTkFont(size=40, weight="bold"),
                    text_color="white",
                )
        else:
            initials = username[:1].upper() if username else "U"
            avatar_label = ctk.CTkLabel(
                avatar_frame,
                text=initials,
                font=ctk.CTkFont(size=40, weight="bold"),
                text_color="white",
            )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        self.avatar_frame = avatar_frame
        self.avatar_label = avatar_label

        # Name, Role and contact info
        name_section = ctk.CTkFrame(top_section, fg_color="transparent")
        name_section.pack(side="left", padx=(24, 0), fill="x", expand=True)

        name_label = ctk.CTkLabel(
            name_section,
            text=display_name,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"],
        )
        name_label.pack(anchor="w", pady=(0, 4))

        role_badge = ctk.CTkFrame(
            name_section,
            fg_color="#e8f5e9",  # Light green background
            corner_radius=6,
        )
        role_badge.pack(anchor="w")

        role_label = ctk.CTkLabel(
            role_badge,
            text=role,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["primary"],
        )
        role_label.pack(padx=12, pady=6)

        # Basic profile info lines
        phone_value = phone_from_db or "9876543210"
        shop_value = "Purva Grocery Store"
        email_value = email_from_db or "purva@email.com"

        phone_label = ctk.CTkLabel(
            name_section,
            text=f"Phone: {phone_value}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        phone_label.pack(anchor="w", pady=(8, 0))

        shop_label = ctk.CTkLabel(
            name_section,
            text=f"Shop: {shop_value}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        shop_label.pack(anchor="w")

        email_label = ctk.CTkLabel(
            name_section,
            text=f"Email: {email_value}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        email_label.pack(anchor="w")

        # Login username hint
        username_hint = ctk.CTkLabel(
            name_section,
            text=f"Login username: {username}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_light"],
        )
        username_hint.pack(anchor="w", pady=(4, 0))

        # Quick action buttons on the top row
        actions_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        actions_frame.pack(side="right")

        upload_btn = ctk.CTkButton(
            actions_frame,
            text="Upload Photo",
            fg_color=COLORS["surface"],
            hover_color=COLORS.get("surface_hover", COLORS["surface"]),
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
            font=ctk.CTkFont(size=12),
            height=32,
            command=self.on_upload_photo,
        )
        upload_btn.pack(fill="x", pady=(0, 8))

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit Profile",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            command=self.on_edit_profile,
        )
        edit_btn.pack(fill="x", pady=(0, 8))

        contact_btn = ctk.CTkButton(
            actions_frame,
            text="Change Email / Phone",
            fg_color="transparent",
            border_color=COLORS["secondary"],
            border_width=1,
            hover_color=COLORS["background"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=11),
            height=32,
            command=self.on_change_contact,
        )
        contact_btn.pack(fill="x")

        # Divider below basic info
        divider = ctk.CTkFrame(profile_content, fg_color=COLORS["background"], height=1)
        divider.pack(fill="x", pady=(16, 0))

        # --- Account Information card (separate section) ---
        account_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        account_card.pack(fill="x", pady=(20, 12))

        account_content = ctk.CTkFrame(account_card, fg_color="transparent")
        account_content.pack(fill="x", padx=24, pady=24)

        account_title = ctk.CTkLabel(
            account_content,
            text="Account Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        account_title.pack(anchor="w", pady=(0, 12))

        account_grid = ctk.CTkFrame(account_content, fg_color="transparent")
        account_grid.pack(fill="x")

        self.create_detail_row(account_grid, "Account Created", "10 Jan 2025")
        self.create_detail_row(account_grid, "Last Login", "13 Mar 2026")

        # --- Shop Information ---
        shop_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        shop_card.pack(fill="x", pady=(0, 12))

        shop_content = ctk.CTkFrame(shop_card, fg_color="transparent")
        shop_content.pack(fill="x", padx=24, pady=24)

        shop_title = ctk.CTkLabel(
            shop_content,
            text="Shop Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        shop_title.pack(anchor="w", pady=(0, 12))

        shop_grid = ctk.CTkFrame(shop_content, fg_color="transparent")
        shop_grid.pack(fill="x")

        # Shop name from settings (default VSG)
        try:
            from utils.settings_manager import SettingsManager
            settings = SettingsManager()
            shop_name = settings.get("shop_name", "VSG") or "VSG"
        except Exception:
            shop_name = "VSG"

        self.create_detail_row(shop_grid, "Shop", shop_name)
        self.create_detail_row(shop_grid, "Address", "Sector 21, Pune")
        self.create_detail_row(shop_grid, "GST", "27XXXXX")

        # --- Account Statistics ---
        stats_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        stats_card.pack(fill="x", pady=(0, 20))

        stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_content.pack(fill="x", padx=24, pady=24)

        stats_title = ctk.CTkLabel(
            stats_content,
            text="Account Statistics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        stats_title.pack(anchor="w", pady=(0, 20))

        stats_grid = ctk.CTkFrame(stats_content, fg_color="transparent")
        stats_grid.pack(fill="x")

        # Stats items (placeholder for now)
        stats_items = [
            ("Member Since", "2025"),
            ("Last Login", "Today"),
            ("Total Sessions", "Active"),
        ]

        for i, (label, value) in enumerate(stats_items):
            stat_frame = ctk.CTkFrame(
                stats_grid,
                fg_color=COLORS.get("surface_hover", COLORS["background"]),
                corner_radius=8,
            )
            stat_frame.grid(row=0, column=i, padx=(0, 12) if i < len(stats_items) - 1 else (0, 0), sticky="ew")
            stats_grid.grid_columnconfigure(i, weight=1)

            stat_label = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_light"],
            )
            stat_label.pack(pady=(12, 4))

            stat_value = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text"],
            )
            stat_value.pack(pady=(0, 12))

        # --- Security Settings ---
        security_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        security_card.pack(fill="x", pady=(0, 12))

        security_content = ctk.CTkFrame(security_card, fg_color="transparent")
        security_content.pack(fill="x", padx=24, pady=24)

        security_title = ctk.CTkLabel(
            security_content,
            text="Security Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        security_title.pack(anchor="w", pady=(0, 12))

        security_desc = ctk.CTkLabel(
            security_content,
            text="Manage your password and keep your account secure.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        security_desc.pack(anchor="w", pady=(0, 10))

        security_btn = ctk.CTkButton(
            security_content,
            text="Change Password",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            command=self.on_change_password,
        )
        security_btn.pack(anchor="w")

        # --- Preferences ---
        prefs_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        prefs_card.pack(fill="x", pady=(0, 20))

        prefs_content = ctk.CTkFrame(prefs_card, fg_color="transparent")
        prefs_content.pack(fill="x", padx=24, pady=24)

        prefs_title = ctk.CTkLabel(
            prefs_content,
            text="Preferences",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        prefs_title.pack(anchor="w", pady=(0, 12))

        prefs_desc = ctk.CTkLabel(
            prefs_content,
            text="Display and behaviour options (placeholders for now).",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        prefs_desc.pack(anchor="w", pady=(0, 10))

        prefs_list = ctk.CTkFrame(prefs_content, fg_color="transparent")
        prefs_list.pack(fill="x")

        self.create_detail_row(prefs_list, "Theme", "System")
        self.create_detail_row(prefs_list, "Language", "English (India)")

    def create_detail_row(self, parent, label, value, value_color=None):
        """Create a detail row with label and value"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 12))

        label_widget = ctk.CTkLabel(
            row_frame,
            text=label + ":",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_light"],
            width=120,
            anchor="w",
        )
        label_widget.pack(side="left")

        value_widget = ctk.CTkLabel(
            row_frame,
            text=value,
            font=ctk.CTkFont(size=12),
            text_color=value_color or COLORS["text"],
        )
        value_widget.pack(side="left", padx=(12, 0))

    def on_upload_photo(self):
        """Let user choose an avatar image and save it."""
        if not self.user:
            messagebox.showerror("Error", "User information not available")
            return

        file_path = filedialog.askopenfilename(
            title="Choose Profile Photo",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.gif")],
        )
        if not file_path:
            return

        try:
            # Copy image into local avatars folder next to main DB used for users table
            from config import DB_PATH as MAIN_DB_PATH
            from database import Database as MainDB

            base_dir = os.path.dirname(os.path.abspath(MAIN_DB_PATH))
            avatars_dir = os.path.join(base_dir, "avatars")
            os.makedirs(avatars_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1] or ".png"
            dest_path = os.path.join(avatars_dir, f"user_{self.user[0]}{ext}")
            shutil.copy(file_path, dest_path)

            # Save in users table (main DB)
            main_db = MainDB(MAIN_DB_PATH)
            main_db.connect()
            if not main_db.execute_query(
                "UPDATE users SET avatar_path = ? WHERE id = ?",
                (dest_path, self.user[0]),
            ):
                messagebox.showerror("Error", "Failed to save profile photo")
                return

            # Reload profile UI to show new avatar
            messagebox.showinfo("Profile Photo", "Profile photo updated successfully")
            for widget in self.winfo_children():
                widget.destroy()
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update photo: {e}")

    def on_edit_profile(self):
        """Handle edit profile button click"""
        if not self.user:
            messagebox.showerror("Error", "User information not available")
            return
        
        # Create edit profile dialog
        dialog = EditProfileDialog(self, self.user, self.db)
        self.wait_window(dialog.top)
        
        # Refresh if profile was updated successfully
        if dialog.profile_updated:
            # Update user tuple
            self.user = dialog.user
            messagebox.showinfo("Success", "Profile updated successfully!")
            # Clear and reload the profile page
            for widget in self.winfo_children():
                widget.destroy()
            self.setup_ui()

    def on_change_password(self):
        """Handle change password button click"""
        if not self.user:
            messagebox.showerror("Error", "User information not available")
            return
        
        # Create change password dialog
        dialog = ChangePasswordDialog(self, self.user, self.db)
        self.wait_window(dialog.top)
        
        # Refresh if password was changed successfully
        if dialog.password_changed:
            messagebox.showinfo("Success", "Password changed successfully!")

    def on_change_contact(self):
        """Open dialog to change email and phone with password confirmation."""
        if not self.user:
            messagebox.showerror("Error", "User information not available")
            return
        
        from config import DB_PATH as MAIN_DB_PATH
        from database import Database as MainDB
        from utils.settings_manager import SettingsManager

        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Email / Phone")
        # Extra height so all three fields and buttons are visible
        dialog.geometry("560x480")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        title = ctk.CTkLabel(
            frame,
            text="Update Contact Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        info = ctk.CTkLabel(
            frame,
            text="Change your email and phone number. Your password is required to confirm changes.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_light"],
            wraplength=440,
            justify="left",
        )
        info.pack(anchor="w", padx=10, pady=(0, 15))

        # Fetch current email/phone from DB
        current_email = None
        current_phone = None
        try:
            db = MainDB(MAIN_DB_PATH)
            db.connect()
            row = db.fetch_one("SELECT email, phone FROM users WHERE id = ?", (self.user[0],))
            if row:
                if len(row) > 0:
                    current_email = row[0]
                if len(row) > 1:
                    current_phone = row[1]
        except Exception:
            pass

        # Email field
        email_label = ctk.CTkLabel(
            frame,
            text="Email",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        email_label.pack(fill="x", padx=10, pady=(0, 3))

        email_entry = ctk.CTkEntry(frame, height=38, font=ctk.CTkFont(size=12))
        if current_email:
            email_entry.insert(0, current_email)
        email_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Phone field
        phone_label = ctk.CTkLabel(
            frame,
            text="Phone Number",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        phone_label.pack(fill="x", padx=10, pady=(8, 3))

        phone_entry = ctk.CTkEntry(frame, height=38, font=ctk.CTkFont(size=12))
        if current_phone:
            phone_entry.insert(0, current_phone)
        phone_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Password field
        pwd_label = ctk.CTkLabel(
            frame,
            text="Current Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        pwd_label.pack(fill="x", padx=10, pady=(8, 3))

        pwd_entry = ctk.CTkEntry(frame, height=38, font=ctk.CTkFont(size=12), show="*")
        pwd_entry.pack(fill="x", padx=10, pady=(0, 10))

        error_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["error"],
        )
        error_label.pack(anchor="w", padx=10, pady=(0, 8))

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.pack(fill="x", padx=10, pady=(8, 4))

        def close_dialog():
            dialog.destroy()

        def save_contact():
            new_email = email_entry.get().strip()
            new_phone = phone_entry.get().strip()
            password = pwd_entry.get().strip()

            if not password:
                error_label.configure(text="Please enter your current password.")
                return

            if new_email and ("@" not in new_email or "." not in new_email):
                error_label.configure(text="Please enter a valid email address.")
                return

            try:
                db = MainDB(MAIN_DB_PATH)
                db.connect()
                row = db.fetch_one(
                    "SELECT password FROM users WHERE id = ?",
                    (self.user[0],),
                )
                if not row or row[0] != password:
                    error_label.configure(text="Password is incorrect.")
                    return

                # Build update query
                db_fields = []
                params = []
                if new_email:
                    db_fields.append("email = ?")
                    params.append(new_email)
                if new_phone:
                    db_fields.append("phone = ?")
                    params.append(new_phone)

                if not db_fields:
                    error_label.configure(text="Please enter at least one value to update.")
                    return

                params.append(self.user[0])
                query = f"UPDATE users SET {', '.join(db_fields)} WHERE id = ?"
                if not db.execute_query(query, tuple(params)):
                    error_label.configure(text="Failed to update contact details. Please try again.")
                    return

                # Sync settings for email / phone
                sm = SettingsManager()
                if new_email:
                    sm.set("contact_email", new_email)
                if new_phone:
                    sm.set("phone_number", new_phone)
                sm.save()

                messagebox.showinfo("Updated", "Your contact details have been updated.")
                dialog.destroy()

                # Reload profile to reflect new values
                self.reload_profile()
            except Exception as e:
                error_label.configure(text=f"Error: {e}")

        cancel_btn = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="transparent",
            border_color=COLORS["secondary"],
            border_width=1,
            hover_color=COLORS["background"],
            text_color=COLORS["text"],
            height=32,
            font=ctk.CTkFont(size=12),
            command=close_dialog,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            buttons,
            text="Save",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=save_contact,
        )
        save_btn.pack(side="right")

        email_entry.focus_set()


class ChangePasswordDialog:
    """Dialog for changing user password"""
    
    def __init__(self, parent, user, db):
        self.user = user
        # Use main database for user authentication (users table is in main DB)
        from config import DB_PATH
        from database import Database
        self.db = Database(DB_PATH)
        self.db.connect()
        self.password_changed = False
        
        # Create top-level window
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Change Password")
        self.top.geometry("500x550")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Make sure window is on top and visible
        self.top.lift()
        self.top.focus_force()
        
        # Center the window
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.top.winfo_screenheight() // 2) - (550 // 2)
        self.top.geometry(f"500x550+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Use a scrollable frame so content is always reachable
        main_frame = ctk.CTkScrollableFrame(self.top, fg_color=COLORS["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Change Password",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text=f"Change password for {self.user[1]}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Current password
        current_label = ctk.CTkLabel(
            main_frame,
            text="Current Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        current_label.pack(fill="x", padx=30, pady=(0, 5))
        
        self.current_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter current password",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.current_password_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        # New password
        new_label = ctk.CTkLabel(
            main_frame,
            text="New Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        new_label.pack(fill="x", padx=30, pady=(0, 5))
        
        self.new_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter new password",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.new_password_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        # Confirm password
        confirm_label = ctk.CTkLabel(
            main_frame,
            text="Confirm New Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        confirm_label.pack(fill="x", padx=30, pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirm new password",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.confirm_password_entry.pack(fill="x", padx=30, pady=(0, 20))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["error"],
        )
        self.error_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(15, 30))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            border_color=COLORS["secondary"],
            border_width=1,
            hover_color=COLORS["background"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=12),
            height=36,
            command=self.top.destroy,
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        change_btn = ctk.CTkButton(
            button_frame,
            text="Change Password",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            command=self.change_password,
        )
        change_btn.pack(side="right")
        
        # Focus on current password field
        self.current_password_entry.focus()
        
        # Bind Enter key
        self.current_password_entry.bind("<Return>", lambda e: self.new_password_entry.focus())
        self.new_password_entry.bind("<Return>", lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind("<Return>", lambda e: self.change_password())
    
    def change_password(self):
        """Handle password change"""
        current = self.current_password_entry.get().strip()
        new = self.new_password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()
        
        # Validation
        if not current or not new or not confirm:
            self.error_label.configure(text="Please fill all fields")
            return
        
        # Verify current password
        query = "SELECT password FROM users WHERE id = ? AND password = ?"
        result = self.db.fetch_one(query, (self.user[0], current))
        
        if not result:
            self.error_label.configure(text="Current password is incorrect")
            self.current_password_entry.delete(0, "end")
            self.current_password_entry.focus()
            return
        
        # Check password length
        if len(new) < 4:
            self.error_label.configure(text="Password must be at least 4 characters")
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            self.new_password_entry.focus()
            return
        
        # Check if passwords match
        if new != confirm:
            self.error_label.configure(text="New passwords do not match")
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            self.new_password_entry.focus()
            return
        
        # Check if new password is same as current
        if current == new:
            self.error_label.configure(text="New password must be different from current password")
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            self.new_password_entry.focus()
            return
        
        # Update password
        update_query = "UPDATE users SET password = ? WHERE id = ?"
        if self.db.execute_query(update_query, (new, self.user[0])):
            self.password_changed = True
            self.top.destroy()
        else:
            self.error_label.configure(text="Failed to update password. Please try again.")


class EditProfileDialog:
    """Dialog for editing user profile"""
    
    def __init__(self, parent, user, db):
        self.user = user
        # Use main database for user authentication (users table is in main DB)
        from config import DB_PATH
        from database import Database
        self.db = Database(DB_PATH)
        self.db.connect()
        self.profile_updated = False

        # Load existing profile fields
        self.full_name = ""
        self.phone = ""
        try:
            row = self.db.fetch_one(
                "SELECT full_name, phone FROM users WHERE id = ?",
                (self.user[0],),
            )
            if row:
                if len(row) > 0 and row[0]:
                    self.full_name = row[0]
                if len(row) > 1 and row[1]:
                    self.phone = row[1]
        except Exception:
            pass
        
        # Create top-level window
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Edit Profile")
        # Slightly smaller height so scrolling becomes useful on small screens
        self.top.geometry("500x380")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Make sure window is on top and visible
        self.top.lift()
        self.top.focus_force()
        
        # Center the window
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.top.winfo_screenheight() // 2) - (380 // 2)
        self.top.geometry(f"500x380+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Scrollable content so everything is reachable even on smaller screens
        main_frame = ctk.CTkScrollableFrame(self.top, fg_color=COLORS["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Edit Profile",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text=f"Update your profile information",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Full name field
        name_label = ctk.CTkLabel(
            main_frame,
            text="Full Name",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        name_label.pack(fill="x", padx=30, pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Your full name",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        if self.full_name:
            self.name_entry.insert(0, self.full_name)
        self.name_entry.pack(fill="x", padx=30, pady=(0, 15))

        # Phone field
        phone_label = ctk.CTkLabel(
            main_frame,
            text="Phone Number",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        phone_label.pack(fill="x", padx=30, pady=(0, 5))

        self.phone_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="10-digit mobile number",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        if self.phone:
            self.phone_entry.insert(0, self.phone)
        self.phone_entry.pack(fill="x", padx=30, pady=(0, 15))

        # Username field
        username_label = ctk.CTkLabel(
            main_frame,
            text="Login Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        username_label.pack(fill="x", padx=30, pady=(10, 5))

        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter username",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.username_entry.insert(0, self.user[1] if self.user else "")
        self.username_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        # Role field (read-only)
        role_label = ctk.CTkLabel(
            main_frame,
            text="Role",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        role_label.pack(fill="x", padx=30, pady=(0, 5))
        
        role_display = ctk.CTkLabel(
            main_frame,
            text=self.user[2] if self.user and len(self.user) > 2 else "Shop Owner",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
            anchor="w",
        )
        role_display.pack(fill="x", padx=30, pady=(0, 15))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["error"],
        )
        self.error_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(15, 30))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            border_color=COLORS["secondary"],
            border_width=1,
            hover_color=COLORS["background"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=12),
            height=36,
            command=self.top.destroy,
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Changes",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            command=self.save_profile,
        )
        save_btn.pack(side="right")
        
        # Focus on username field
        self.username_entry.focus()
        self.username_entry.select_range(0, "end")
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.save_profile())
    
    def save_profile(self):
        """Handle profile save"""
        new_full_name = self.name_entry.get().strip()
        new_phone = self.phone_entry.get().strip()
        new_username = self.username_entry.get().strip()
        
        # Validation
        if not new_full_name or not new_phone or not new_username:
            self.error_label.configure(text="Please fill all fields")
            return
        
        if len(new_username) < 3:
            self.error_label.configure(text="Username must be at least 3 characters")
            return
        
        if len(new_phone) < 6:
            self.error_label.configure(text="Please enter a valid phone number")
            return
        
        # Check if username already exists (excluding current user)
        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (new_username, self.user[0])
        )
        
        if existing:
            self.error_label.configure(text="Username already exists")
            return
        
        # Update profile fields
        update_query = "UPDATE users SET username = ?, full_name = ?, phone = ? WHERE id = ?"
        if self.db.execute_query(update_query, (new_username, new_full_name, new_phone, self.user[0])):
            self.profile_updated = True
            # Update user tuple
            self.user = (self.user[0], new_username, self.user[2] if len(self.user) > 2 else "shop_owner")
            self.top.destroy()
        else:
            self.error_label.configure(text="Failed to update profile. Please try again.")
