"""
Utility functions for matplotlib charts with dark mode support
"""
import matplotlib.pyplot as plt
from config import COLORS
from utils.settings_manager import SettingsManager


def get_chart_colors():
    """Get chart colors based on current theme"""
    import customtkinter as ctk
    from config import COLORS
    
    # Check actual appearance mode first (most reliable)
    try:
        app_mode = ctk.get_appearance_mode()
        is_dark = app_mode == "Dark"
    except:
        # Fallback to settings
        settings = SettingsManager()
        theme = settings.get("theme", "System")
        is_dark = theme == "Dark"
    
    if is_dark:
        return {
            'figure_bg': COLORS['surface'],  # Use theme surface color
            'axes_bg': COLORS['surface'],     # Use theme surface color
            'text_color': COLORS['text'],     # Use theme text color
            'grid_color': COLORS.get('border', '#404040'),  # Use theme border color
            'spine_color': COLORS.get('border', '#404040'), # Use theme border color
        }
    else:
        return {
            'figure_bg': COLORS['surface'],   # Use theme surface color
            'axes_bg': COLORS['surface'],     # Use theme surface color
            'text_color': COLORS['text'],     # Use theme text color
            'grid_color': COLORS.get('border', '#e5e7eb'),  # Use theme border color
            'spine_color': COLORS.get('border', '#d1d5db'), # Use theme border color
        }


def configure_chart_dark_mode(fig, ax):
    """Configure matplotlib figure and axes for dark mode"""
    colors = get_chart_colors()
    
    # Set figure background
    fig.patch.set_facecolor(colors['figure_bg'])
    
    # Set axes background
    ax.set_facecolor(colors['axes_bg'])
    
    # Set text colors
    ax.tick_params(colors=colors['text_color'])
    ax.xaxis.label.set_color(colors['text_color'])
    ax.yaxis.label.set_color(colors['text_color'])
    ax.title.set_color(colors['text_color'])
    
    # Set spine colors
    for spine in ax.spines.values():
        spine.set_color(colors['spine_color'])
    
    # Set grid color
    ax.grid(True, color=colors['grid_color'], alpha=0.3)
    
    return fig, ax

