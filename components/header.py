"""Header component for main application"""
import customtkinter as ctk
from datetime import datetime
from config import COLORS, APP_NAME


class Header(ctk.CTkFrame):
    """Application header with logo, date and user info"""
    
    def __init__(self, parent, page_title="Dashboard", user_name: str = "", on_profile_click=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, height=64, corner_radius=0, fg_color=COLORS['surface'])
        self.page_title = page_title
        self.user_name = user_name
        self.on_profile_click = on_profile_click
        self.setup_header()
    
    def update_colors(self):
        """Update header colors when theme changes"""
        self.configure(fg_color=COLORS['surface'])
        # Recreate header to update all colors
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_header()
    
    def setup_header(self):
        """Setup header UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Use pack layout consistently
        self.pack_propagate(False)  # Maintain fixed height
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Left section - Logo
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=0)

        # Improved logo design
        logo_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_container.pack(side="left", pady=10)
        
        # Logo icon/badge
        logo_badge = ctk.CTkFrame(
            logo_container,
            fg_color=COLORS['primary'],
            corner_radius=8,
            width=40,
            height=40,
        )
        logo_badge.pack(side="left")
        logo_badge.pack_propagate(False)
        
        logo_icon = ctk.CTkLabel(
            logo_badge,
            text="🛒",
            font=ctk.CTkFont(size=20),
            text_color="white",
        )
        logo_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo text - use shop name from settings (default VSG)
        logo_text_frame = ctk.CTkFrame(logo_container, fg_color="transparent")
        logo_text_frame.pack(side="left", padx=(10, 0))

        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        shop_name = settings.get("shop_name", "VSG") or "VSG"

        logo_label = ctk.CTkLabel(
            logo_text_frame,
            text=shop_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        logo_label.pack(anchor="w")
        
        tagline_label = ctk.CTkLabel(
            logo_text_frame,
            text="Smart Grocery Management",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_light'],
        )
        tagline_label.pack(anchor="w")

        # Center section - Date (spacer)
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.pack(side="left", fill="x", expand=True, padx=20, pady=0)

        # Format date according to settings
        from utils.settings_manager import SettingsManager
        settings = SettingsManager()
        current_date = datetime.now()
        
        # Format based on user preference
        date_format = settings.get("date_format", "YYYY-MM-DD")
        if date_format == "YYYY-MM-DD":
            date_str = current_date.strftime("%A, %B %d, %Y")
        elif date_format == "DD-MM-YYYY":
            date_str = current_date.strftime("%A, %d %B %Y")
        elif date_format == "MM/DD/YYYY":
            date_str = current_date.strftime("%A, %B %d, %Y")
        else:
            date_str = current_date.strftime("%A, %B %d, %Y")
        
        date_label = ctk.CTkLabel(
            center_frame,
            text=date_str,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'],
        )
        date_label.pack(side="right")

        # Right section - User profile
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=0)

        profile_chip = ctk.CTkFrame(
            right_frame,
            fg_color="transparent",
        )
        profile_chip.pack(side="right")

        avatar_frame = ctk.CTkFrame(
            profile_chip,
            fg_color=COLORS.get('surface_hover', COLORS['surface']),
            corner_radius=999,
            width=28,
            height=28,
        )
        avatar_frame.pack(side="left")
        avatar_frame.pack_propagate(False)

        initials = (self.user_name[:1].upper() if self.user_name else "U")
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=initials,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text'],
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        name_label = ctk.CTkLabel(
            profile_chip,
            text=self.user_name or "Profile",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
        )
        name_label.pack(side="left", padx=(8, 0))

        def handle_profile_click(_event=None):
            if callable(self.on_profile_click):
                self.on_profile_click()

        for widget in (profile_chip, avatar_frame, avatar_label, name_label):
            widget.bind("<Button-1>", handle_profile_click)

    def update_title(self, title):
        """Update page title (not visually shown in header)"""
        self.page_title = title

