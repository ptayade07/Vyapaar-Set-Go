"""User profile page for VyapaarSetGo"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, DB_PATH
from database import Database


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

    def setup_ui(self):
        """Setup profile page UI"""
        # Main scrollable container
        main_container = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"])
        main_container.pack(expand=True, fill="both", padx=40, pady=40)

        # Header Section
        header_frame = ctk.CTkFrame(main_container, fg_color=COLORS["surface"], corner_radius=12)
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

        # Profile Card
        profile_card = ctk.CTkFrame(main_container, fg_color=COLORS["surface"], corner_radius=12)
        profile_card.pack(fill="x", pady=(0, 20))

        profile_content = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_content.pack(fill="x", padx=24, pady=24)

        # Avatar and Basic Info
        top_section = ctk.CTkFrame(profile_content, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 24))

        username = self.user[1] if self.user else "User"
        role = self.user[2] if self.user and len(self.user) > 2 else "Shop Owner"

        # Large Avatar
        avatar_frame = ctk.CTkFrame(
            top_section,
            fg_color=COLORS["primary"],
            corner_radius=999,
            width=100,
            height=100,
        )
        avatar_frame.pack(side="left")
        avatar_frame.pack_propagate(False)

        initials = username[:1].upper() if username else "U"
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=initials,
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="white",
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        # Name and Role
        name_section = ctk.CTkFrame(top_section, fg_color="transparent")
        name_section.pack(side="left", padx=(24, 0), fill="x", expand=True)

        name_label = ctk.CTkLabel(
            name_section,
            text=username,
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

        # Divider
        divider = ctk.CTkFrame(profile_content, fg_color=COLORS["background"], height=1)
        divider.pack(fill="x", pady=(0, 24))

        # Account Details Section
        details_title = ctk.CTkLabel(
            profile_content,
            text="Account Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        details_title.pack(anchor="w", pady=(0, 16))

        # Details Grid
        details_grid = ctk.CTkFrame(profile_content, fg_color="transparent")
        details_grid.pack(fill="x")

        # User ID
        self.create_detail_row(details_grid, "User ID", str(self.user[0]) if self.user else "N/A")
        self.create_detail_row(details_grid, "Username", username)
        self.create_detail_row(details_grid, "Role", role)
        self.create_detail_row(details_grid, "Account Status", "Active", COLORS["success"])

        # Statistics Section
        stats_card = ctk.CTkFrame(main_container, fg_color=COLORS["surface"], corner_radius=12)
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
            stat_frame = ctk.CTkFrame(stats_grid, fg_color=COLORS["background"], corner_radius=8)
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

        # Actions Section
        actions_card = ctk.CTkFrame(main_container, fg_color=COLORS["surface"], corner_radius=12)
        actions_card.pack(fill="x")

        actions_content = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_content.pack(fill="x", padx=24, pady=24)

        actions_title = ctk.CTkLabel(
            actions_content,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        actions_title.pack(anchor="w", pady=(0, 16))

        actions_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
        actions_frame.pack(fill="x")

        # Action buttons (placeholders)
        action_btn = ctk.CTkButton(
            actions_frame,
            text="Edit Profile",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            command=self.on_edit_profile,
        )
        action_btn.pack(side="left", padx=(0, 12))

        change_pass_btn = ctk.CTkButton(
            actions_frame,
            text="Change Password",
            fg_color="transparent",
            border_color=COLORS["secondary"],
            border_width=1,
            hover_color=COLORS["background"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=12),
            height=36,
            command=self.on_change_password,
        )
        change_pass_btn.pack(side="left")

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
        main_frame = ctk.CTkFrame(self.top, fg_color=COLORS["surface"])
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
        
        # Create top-level window
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Edit Profile")
        self.top.geometry("500x480")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Make sure window is on top and visible
        self.top.lift()
        self.top.focus_force()
        
        # Center the window
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.top.winfo_screenheight() // 2) - (480 // 2)
        self.top.geometry(f"500x480+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ctk.CTkFrame(self.top, fg_color=COLORS["surface"])
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
        
        # Username field
        username_label = ctk.CTkLabel(
            main_frame,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        username_label.pack(fill="x", padx=30, pady=(0, 5))
        
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
        new_username = self.username_entry.get().strip()
        
        # Validation
        if not new_username:
            self.error_label.configure(text="Username cannot be empty")
            return
        
        if len(new_username) < 3:
            self.error_label.configure(text="Username must be at least 3 characters")
            return
        
        # Check if username already exists (excluding current user)
        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (new_username, self.user[0])
        )
        
        if existing:
            self.error_label.configure(text="Username already exists")
            return
        
        # Update username
        update_query = "UPDATE users SET username = ? WHERE id = ?"
        if self.db.execute_query(update_query, (new_username, self.user[0])):
            self.profile_updated = True
            # Update user tuple
            self.user = (self.user[0], new_username, self.user[2] if len(self.user) > 2 else "shop_owner")
            self.top.destroy()
        else:
            self.error_label.configure(text="Failed to update profile. Please try again.")
