"""
Login module for VyapaarSetGo
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH


class LoginFrame(ctk.CTkFrame):
    """Login frame that can be embedded in main window"""
    
    def __init__(self, parent, on_success):
        super().__init__(parent, fg_color=COLORS['surface'])
        self.on_success = on_success
        # Use main database for authentication (users table)
        self.db = Database(DB_PATH)
        self.db.connect()
        # Initialize main database if needed
        self.db.initialize_database()
        self.is_signup = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        # Outer container for centering
        outer_container = ctk.CTkFrame(self, fg_color=COLORS['background'])
        outer_container.pack(expand=True, fill="both")
        
        # Centered card container
        card_container = ctk.CTkFrame(outer_container, fg_color=COLORS['surface'], corner_radius=15)
        card_container.pack(expand=True, pady=50)
        card_container.pack_propagate(False)
        card_container.configure(width=500, height=650)
        
        # Main container inside card
        container = ctk.CTkFrame(card_container, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Logo and branding
        logo_frame = ctk.CTkFrame(container, fg_color="transparent")
        logo_frame.pack(pady=(10, 20))
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="✓ VyapaarSetGo",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['primary']
        )
        logo_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Smart Grocery Management",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light']
        )
        subtitle_label.pack(pady=(3, 0))
        
        # Toggle between Login and Sign Up
        toggle_frame = ctk.CTkFrame(container, fg_color="transparent")
        toggle_frame.pack(pady=(0, 15))
        
        self.login_btn = ctk.CTkButton(
            toggle_frame,
            text="Login",
            command=self.show_login_form,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            width=140,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_btn.pack(side="left", padx=5)
        
        self.signup_btn = ctk.CTkButton(
            toggle_frame,
            text="Sign Up",
            command=self.show_signup_form,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            width=140,
            font=ctk.CTkFont(size=14)
        )
        self.signup_btn.pack(side="left", padx=5)
        
        # Form container
        self.form_container = ctk.CTkFrame(container, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Show login form by default
        self.show_login_form()
    
    def show_login_form(self):
        """Show login form"""
        self.is_signup = False
        self.login_btn.configure(fg_color=COLORS['primary'], font=ctk.CTkFont(size=14, weight="bold"))
        self.signup_btn.configure(fg_color=COLORS['secondary'], font=ctk.CTkFont(size=14))
        
        # Clear form container
        for widget in self.form_container.winfo_children():
            widget.destroy()
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.form_container,
            text="Welcome Back!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        welcome_label.pack(pady=(0, 5))
        
        desc_label = ctk.CTkLabel(
            self.form_container,
            text="Login to manage your grocery shop efficiently.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        desc_label.pack(pady=(0, 20))
        
        # Form fields
        form_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        form_frame.pack(fill="x")
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 3))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your username",
            height=42,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(fill="x", pady=(0, 12))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 3))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your password",
            height=42,
            font=ctk.CTkFont(size=14),
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 8))
        
        # Forgot password link
        forgot_link = ctk.CTkLabel(
            form_frame,
            text="Forgot Password?",
            font=ctk.CTkFont(size=11, underline=True),
            text_color=COLORS['primary'],
            cursor="hand2"
        )
        forgot_link.pack(anchor="e", pady=(0, 15))
        forgot_link.bind("<Button-1>", lambda e: self.show_forgot_password())
        
        # Login button
        login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.handle_login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark']
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['error']
        )
        self.error_label.pack()
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
    
    def show_signup_form(self):
        """Show sign up form"""
        self.is_signup = True
        self.signup_btn.configure(fg_color=COLORS['primary'], font=ctk.CTkFont(size=14, weight="bold"))
        self.login_btn.configure(fg_color=COLORS['secondary'], font=ctk.CTkFont(size=14))
        
        # Clear form container
        for widget in self.form_container.winfo_children():
            widget.destroy()
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.form_container,
            text="Create Account",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        welcome_label.pack(pady=(0, 5))
        
        desc_label = ctk.CTkLabel(
            self.form_container,
            text="Sign up to start managing your grocery shop.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        desc_label.pack(pady=(0, 20))
        
        # Form fields
        form_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        form_frame.pack(fill="x")
        
        # Full name field
        name_label = ctk.CTkLabel(
            form_frame,
            text="Full Name",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 3))
        
        self.signup_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Your full name",
            height=42,
            font=ctk.CTkFont(size=14)
        )
        self.signup_name_entry.pack(fill="x", pady=(0, 12))
        
        # Phone number field
        phone_label = ctk.CTkLabel(
            form_frame,
            text="Phone Number",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        phone_label.pack(fill="x", pady=(0, 3))
        
        self.signup_phone_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="10-digit mobile number",
            height=42,
            font=ctk.CTkFont(size=14)
        )
        self.signup_phone_entry.pack(fill="x", pady=(0, 12))
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 3))
        
        self.signup_username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Choose a username",
            height=42,
            font=ctk.CTkFont(size=14)
        )
        self.signup_username_entry.pack(fill="x", pady=(0, 12))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 3))
        
        self.signup_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Create a password",
            height=42,
            show="*",
            font=ctk.CTkFont(size=14)
        )
        self.signup_password_entry.pack(fill="x", pady=(0, 12))
        
        # Confirm Password field
        confirm_password_label = ctk.CTkLabel(
            form_frame,
            text="Confirm Password",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        )
        confirm_password_label.pack(fill="x", pady=(0, 3))
        
        self.confirm_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Confirm your password",
            height=42,
            show="*",
            font=ctk.CTkFont(size=14)
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 15))
        
        # Sign up button
        signup_btn = ctk.CTkButton(
            form_frame,
            text="Sign Up",
            command=self.handle_signup,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark']
        )
        signup_btn.pack(fill="x", pady=(0, 10))
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['error']
        )
        self.error_label.pack()
        
        # Bind Enter key
        self.confirm_password_entry.bind("<Return>", lambda e: self.handle_signup())
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return
        
        # Authenticate user
        query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        user = self.db.fetch_one(query, (username, password))
        
        if user:
            self.error_label.configure(text="")
            self.on_success(user)
        else:
            self.error_label.configure(text="Invalid username or password")
    
    def handle_signup(self):
        """Handle sign up attempt"""
        full_name = self.signup_name_entry.get().strip()
        phone = self.signup_phone_entry.get().strip()
        username = self.signup_username_entry.get().strip()
        password = self.signup_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not full_name or not phone or not username or not password or not confirm_password:
            self.error_label.configure(text="Please fill all fields")
            return
        
        if password != confirm_password:
            self.error_label.configure(text="Passwords do not match")
            return
        
        if len(password) < 4:
            self.error_label.configure(text="Password must be at least 4 characters")
            return
        
        # Basic phone validation (optional but helpful)
        if len(phone) < 6:
            self.error_label.configure(text="Please enter a valid phone number")
            return
        
        # Check if username already exists
        existing = self.db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            self.error_label.configure(text="Username already exists")
            return
        
        # Create new user with profile info
        query = "INSERT INTO users (username, password, role, full_name, phone) VALUES (?, ?, ?, ?, ?)"
        if self.db.execute_query(query, (username, password, 'shop_owner', full_name, phone)):
            self.error_label.configure(text="Account created successfully! Please login.", text_color=COLORS['success'])
            self.after(1000, self.show_login_form)
        else:
            self.error_label.configure(text="Failed to create account. Please try again.")
    
    def show_forgot_password(self):
        """Show forgot password dialog"""
        dialog = ctk.CTkInputDialog(
            text="Contact administrator to reset your password",
            title="Forgot Password"
        )
