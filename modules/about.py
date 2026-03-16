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
        center_wrapper.pack(expand=True, pady=10)
        
        # Center content with constrained width so it feels like a card
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

        # Version pill
        version_frame = ctk.CTkFrame(
            center_frame,
            fg_color=COLORS.get("surface", "#ffffff"),
            corner_radius=999,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        version_frame.pack(pady=(0, 30))

        version_label = ctk.CTkLabel(
            version_frame,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary"],
        )
        version_label.pack(padx=20, pady=12)

        # Two-column content row (About + Features on left, Tech on right)
        content_row = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_row.pack(fill="both", expand=True)

        left_column = ctk.CTkFrame(content_row, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(content_row, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Description
        desc_frame = ctk.CTkFrame(
            left_column,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        desc_frame.pack(fill="x", pady=(0, 12))

        desc_title = ctk.CTkLabel(
            desc_frame,
            text="About",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        desc_title.pack(anchor="w", padx=20, pady=(20, 10))

        common_body_font = ctk.CTkFont(size=12)

        desc_text = ctk.CTkLabel(
            desc_frame,
            text=(
                f"{APP_NAME} is a smart business assistant made for small grocery and kirana shops. "
                "It brings your daily work into one simple place so you can track stock, manage customer khata, "
                "handle suppliers, bill customers quickly, and understand your business with clear reports — "
                "without complicated software or spreadsheets."
            ),
            font=common_body_font,
            text_color=COLORS["text"],
            wraplength=520,
            justify="left",
        )
        desc_text.pack(anchor="w", padx=20, pady=(0, 20))

        # Features List
        features_frame = ctk.CTkFrame(
            left_column,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        features_frame.pack(fill="both", expand=True, pady=(0, 12))

        features_title = ctk.CTkLabel(
            features_frame,
            text="Features",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        features_title.pack(anchor="w", padx=20, pady=(20, 15))

        features = [
            "📦 Track stock levels and product details in one place",
            "📒 Manage customer khata (dues and advance balances)",
            "🧾 Fast sales & billing with printable bills",
            "🚚 Record supplier purchases and update inventory automatically",
            "📊 Ready-made reports for sales, stock, and customer activity",
            "👤 Simple profile page with basic account information",
        ]

        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"• {feature}",
                font=common_body_font,
                text_color=COLORS["text"],
                justify="left",
                anchor="w",
            )
            feature_label.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(features_frame, text="", height=5).pack(anchor="w", padx=20, pady=(0, 10))

        # Technology & Developer Info
        tech_frame = ctk.CTkFrame(
            right_column,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        tech_frame.pack(fill="both", expand=True, pady=(0, 12))

        tech_title = ctk.CTkLabel(
            tech_frame,
            text="Technology Stack",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        )
        tech_title.pack(anchor="w", padx=20, pady=(20, 10))

        tech_body = ctk.CTkLabel(
            tech_frame,
            text=(
                "• Python with CustomTkinter for a clean, modern desktop UI\n"
                "• SQLite for fast, file-based data storage\n"
                "• Matplotlib and reporting tools for charts and exports\n"
                "• Pillow (PIL) for profile and image handling"
            ),
            font=common_body_font,
            text_color=COLORS["text"],
            justify="left",
            wraplength=520,
        )
        tech_body.pack(anchor="w", padx=20, pady=(0, 16))

        dev_label = ctk.CTkLabel(
            tech_frame,
            text="Built to help local shop owners run their daily business more efficiently and professionally.",
            font=common_body_font,
            text_color=COLORS["text_light"],
            wraplength=520,
            justify="left",
        )
        dev_label.pack(anchor="w", padx=20, pady=(0, 20))

        # Support / Contact
        support_title = ctk.CTkLabel(
            tech_frame,
            text="Support",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        )
        support_title.pack(anchor="w", padx=20, pady=(0, 6))

        support_body = ctk.CTkLabel(
            tech_frame,
            text=(
                "For questions or feedback about VyapaarSetGo,\n"
                "please contact the developer at:\n"
                "Email: purvatayade2603@gmail.com"
            ),
            font=common_body_font,
            text_color=COLORS["text_light"],
            justify="left",
            wraplength=520,
        )
        support_body.pack(anchor="w", padx=20, pady=(0, 16))

        # Footer
        footer_label = ctk.CTkLabel(
            center_frame,
            text="© 2025 VyapaarSetGo. All rights reserved.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_light"],
        )
        footer_label.pack(pady=(16, 0))

