"""
Widget utility functions for theme updates
"""
import customtkinter as ctk
from config import COLORS


def update_widget_colors(widget):
    """Recursively update widget colors based on current theme"""
    try:
        # Update frame colors
        if isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
            # Get current fg_color
            current_fg = widget.cget("fg_color")
            
            # If it's using a COLORS value, update it
            if current_fg in [COLORS['background'], COLORS['surface'], COLORS.get('surface_hover')]:
                # Determine what color it should be
                if widget.cget("fg_color") == COLORS['background']:
                    widget.configure(fg_color=COLORS['background'])
                elif widget.cget("fg_color") == COLORS['surface']:
                    widget.configure(fg_color=COLORS['surface'])
        
        # Update label text colors
        if isinstance(widget, ctk.CTkLabel):
            current_text_color = widget.cget("text_color")
            if current_text_color in [COLORS['text'], COLORS['text_light']]:
                if current_text_color == COLORS['text']:
                    widget.configure(text_color=COLORS['text'])
                elif current_text_color == COLORS['text_light']:
                    widget.configure(text_color=COLORS['text_light'])
        
        # Update button colors
        if isinstance(widget, ctk.CTkButton):
            current_fg = widget.cget("fg_color")
            if current_fg in [COLORS['primary'], COLORS['secondary'], COLORS['surface']]:
                if current_fg == COLORS['primary']:
                    widget.configure(fg_color=COLORS['primary'])
                elif current_fg == COLORS['secondary']:
                    widget.configure(fg_color=COLORS['secondary'])
                elif current_fg == COLORS['surface']:
                    widget.configure(fg_color=COLORS['surface'])
        
        # Recursively update children
        for child in widget.winfo_children():
            update_widget_colors(child)
    except:
        pass

