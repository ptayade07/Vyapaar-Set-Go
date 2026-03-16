"""
Sidebar navigation component
"""
import customtkinter as ctk
from config import COLORS


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation menu"""
    
    def __init__(self, parent, on_navigate):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        # Use a neutral surface background so the sidebar
        # feels lighter, and keep green only as an accent.
        super().__init__(parent, width=230, corner_radius=0, fg_color=COLORS['surface'])
        self.on_navigate = on_navigate
        self.current_page = "dashboard"
        self.buttons = {}
        self.setup_sidebar()
    
    def setup_sidebar(self):
        """Setup sidebar UI"""
        # Use pack layout consistently
        self.pack_propagate(False)  # Maintain fixed width
        
        # Top section with navigation items
        # Reduce top padding so the first item aligns better
        # with the main header bar on the right.
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=(8, 10))

        nav_items = [
            ("dashboard", "Dashboard", "🏠"),
            ("inventory", "Inventory", "📦"),
            ("khata", "Khata", "📒"),
            ("suppliers", "Suppliers", "🚚"),
            ("sales", "Sales", "🛒"),
            ("reports", "Reports", "📊"),
            ("notifications", "Notifications", "🔔"),
            ("help", "Help", "❓"),
            ("about", "About", "ℹ️"),
            ("settings", "Settings", "⚙️"),
        ]
        
        for page_id, label, icon in nav_items:
            # Import COLORS fresh to get current theme colors
            from config import COLORS
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}   {label}",
                command=lambda p=page_id: self.navigate(p),
                # Default state: neutral background with dark text
                fg_color="transparent",
                hover_color=COLORS.get('surface_hover', COLORS['surface']),
                text_color=COLORS['text'],
                anchor="w",
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(fill="x", pady=4)
            self.buttons[page_id] = btn

        # Bottom section with logout button
        logout_frame = ctk.CTkFrame(self, fg_color="transparent")
        logout_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 20))

        logout_btn = ctk.CTkButton(
            logout_frame,
            text="  🚪   Logout",
            command=lambda: self.navigate("logout"),
            fg_color="transparent",
            hover_color=COLORS.get('surface_hover', COLORS['surface']),
            text_color=COLORS['error'],
            anchor="w",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        logout_btn.pack(fill="x")

        self.navigate(self.current_page)

    def navigate(self, page_id):
        """Navigate to a page"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        for btn in self.buttons.values():
            # Reset to neutral sidebar style
            btn.configure(
                fg_color="transparent",
                text_color=COLORS['text']
            )

        if page_id in self.buttons:
            self.buttons[page_id].configure(
                # Green pill for the active item to match app accent
                fg_color=COLORS['primary'],
                text_color="white"
            )

        self.current_page = page_id
        self.on_navigate(page_id)

