"""
Splash screen module for VyapaarSetGo
"""
import customtkinter as ctk
from config import COLORS, APP_NAME, APP_VERSION


class SplashScreen(ctk.CTkFrame):
    """Splash screen frame shown before login"""

    def __init__(self, parent, on_complete, duration_ms: int = 2000):
        super().__init__(parent, fg_color=COLORS['background'])
        self.on_complete = on_complete
        self.duration_ms = duration_ms

        self.setup_ui()

        self.after(self.duration_ms, self.finish)

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color=COLORS['background'])
        container.pack(expand=True, fill="both")

        content = ctk.CTkFrame(container, fg_color=COLORS['surface'], corner_radius=20)
        content.pack(expand=True, padx=60, pady=80)

        content.pack_propagate(False)
        content.configure(width=500, height=350)

        logo_frame = ctk.CTkFrame(content, fg_color="transparent")
        logo_frame.pack(pady=(40, 10))

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="✓",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color=COLORS['primary']
        )
        logo_label.pack()

        title_label = ctk.CTkLabel(
            content,
            text=APP_NAME,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ctk.CTkLabel(
            content,
            text="Smart Grocery Management",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_light']
        )
        subtitle_label.pack(pady=(0, 20))

        version_label = ctk.CTkLabel(
            content,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        version_label.pack(pady=(0, 20))

        progress = ctk.CTkProgressBar(content)
        progress.set(0.5)
        progress.pack(fill="x", padx=80, pady=(0, 20))

        loading_label = ctk.CTkLabel(
            content,
            text="Loading, please wait...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['secondary']
        )
        loading_label.pack(pady=(0, 30))

    def finish(self):
        if callable(self.on_complete):
            self.on_complete()
