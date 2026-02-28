"""About page for VyapaarSetGo"""
import customtkinter as ctk
from config import COLORS, APP_NAME, APP_VERSION


class About(ctk.CTkFrame):
    """About page with application information"""

    def __init__(self, parent):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS["background"])
        self.setup_ui()

    def setup_ui(self):
        """Setup about page UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Main scrollable container
        main_container = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"])
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Center content wrapper
        center_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
        center_wrapper.pack(expand=True, pady=20)
        
        # Center content
        center_frame = ctk.CTkFrame(center_wrapper, fg_color="transparent")
        center_frame.pack(expand=True)

        # App Logo/Badge
        logo_frame = ctk.CTkFrame(
            center_frame,
            fg_color=COLORS["primary"],
            corner_radius=20,
            width=120,
            height=120,
        )
        logo_frame.pack(pady=(0, 30))
        logo_frame.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="✓",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="white",
        )
        logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # App Name
        app_name_label = ctk.CTkLabel(
            center_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text"],
        )
        app_name_label.pack(pady=(0, 8))

        # Tagline
        tagline_label = ctk.CTkLabel(
            center_frame,
            text="Smart Grocery Management",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_light"],
        )
        tagline_label.pack(pady=(0, 20))

        # Version
        version_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["surface"], corner_radius=8)
        version_frame.pack(pady=(0, 30))

        version_label = ctk.CTkLabel(
            version_frame,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary"],
        )
        version_label.pack(padx=20, pady=12)

        # Description
        desc_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["surface"], corner_radius=12)
        desc_frame.pack(fill="x", pady=(0, 20))

        desc_title = ctk.CTkLabel(
            desc_frame,
            text="About",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        desc_title.pack(anchor="w", padx=20, pady=(20, 10))

        desc_text = ctk.CTkLabel(
            desc_frame,
            text=(
                f"{APP_NAME} is a comprehensive grocery store management system designed to help "
                "you manage your inventory, track sales, maintain customer accounts, and generate "
                "reports. Built with modern technology to provide a smooth and efficient experience "
                "for managing your grocery business."
            ),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            wraplength=500,
            justify="left",
        )
        desc_text.pack(anchor="w", padx=20, pady=(0, 20))

        # Features List
        features_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["surface"], corner_radius=12)
        features_frame.pack(fill="x", pady=(0, 20))

        features_title = ctk.CTkLabel(
            features_frame,
            text="Features",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        features_title.pack(anchor="w", padx=20, pady=(20, 15))

        features = [
            "📦 Inventory Management",
            "📒 Customer Khata (Account Management)",
            "🛒 Sales & Billing",
            "🚚 Supplier Management",
            "📊 Reports & Analytics",
            "👤 User Profile Management",
        ]

        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text"],
            )
            feature_label.pack(anchor="w", padx=20, pady=(0, 8))

        ctk.CTkLabel(features_frame, text="", height=5).pack(anchor="w", padx=20, pady=(0, 10))

        # Footer
        footer_label = ctk.CTkLabel(
            center_frame,
            text="© 2025 VyapaarSetGo. All rights reserved.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_light"],
        )
        footer_label.pack(pady=(20, 0))

