"""
Notifications module for VyapaarSetGo
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS
from datetime import datetime


class Notifications(ctk.CTkFrame):
    """Notifications page with alerts and reminders"""
    
    def __init__(self, parent, db=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS, DB_PATH
        super().__init__(parent, fg_color=COLORS['background'])
        # Use the provided database (user-specific) or fallback to main DB
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()
        self.setup_ui()
        self.load_notifications()
    
    def setup_ui(self):
        """Setup notifications UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_notifications,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=35,
            width=100,
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.pack(side="left", padx=5)
        
        mark_all_read_btn = ctk.CTkButton(
            actions_frame,
            text="✓ Mark All Read",
            command=self.mark_all_read,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            width=120,
            font=ctk.CTkFont(size=12)
        )
        mark_all_read_btn.pack(side="left", padx=5)
        
        clear_all_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            height=35,
            width=100,
            font=ctk.CTkFont(size=12)
        )
        clear_all_btn.pack(side="left", padx=5)
        
        # Main content area
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollable frame for notifications
        self.notifications_scroll = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS['background'])
        self.notifications_scroll.pack(fill="both", expand=True)
        
        self.notifications_frame = ctk.CTkFrame(self.notifications_scroll, fg_color="transparent")
        self.notifications_frame.pack(fill="x")
    
    def load_notifications(self):
        """Load notifications from database"""
        # Clear existing notifications
        for widget in self.notifications_frame.winfo_children():
            widget.destroy()
        
        # Get all notifications, newest first
        notifications = self.db.fetch_all(
            "SELECT id, type, title, message, is_read, created_at FROM notifications ORDER BY created_at DESC"
        )
        
        if not notifications:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.notifications_frame, fg_color="transparent")
            empty_frame.pack(expand=True, pady=50)
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="📭 No notifications",
                font=ctk.CTkFont(size=18),
                text_color=COLORS['text_light']
            )
            empty_label.pack()
            
            empty_subtitle = ctk.CTkLabel(
                empty_frame,
                text="You're all caught up!",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            empty_subtitle.pack(pady=(10, 0))
            return
        
        # Display notifications
        for notification in notifications:
            self.create_notification_card(notification)
    
    def create_notification_card(self, notification):
        """Create a notification card"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        notif_id, notif_type, title, message, is_read, created_at = notification
        
        # Determine color based on type
        type_colors = {
            'low_stock': COLORS['warning'],
            'out_of_stock': COLORS['error'],
            'expiry': COLORS['warning'],
            'payment_due': COLORS['error'],
            'info': COLORS['primary'],
        }
        type_icons = {
            'low_stock': '⚠️',
            'out_of_stock': '❌',
            'expiry': '📅',
            'payment_due': '💳',
            'info': 'ℹ️',
        }
        
        card_color = type_colors.get(notif_type, COLORS['surface'])
        icon = type_icons.get(notif_type, '📢')
        
        # Card frame
        card = ctk.CTkFrame(
            self.notifications_frame,
            fg_color=COLORS['surface'] if is_read else COLORS.get('surface_hover', COLORS['surface']),
            corner_radius=12,
            border_width=1 if not is_read else 0,
            border_color=card_color if not is_read else COLORS.get('border', COLORS['secondary'])
        )
        card.pack(fill="x", pady=8, padx=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=15)
        
        # Top row: Icon, title, and actions
        top_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))
        
        # Icon and title
        icon_title_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        icon_title_frame.pack(side="left", fill="x", expand=True)
        
        icon_label = ctk.CTkLabel(
            icon_title_frame,
            text=icon,
            font=ctk.CTkFont(size=20)
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            icon_title_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text'],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Time and actions (notification style: time + Done pill)
        actions_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        actions_frame.pack(side="right", padx=(12, 0))
        
        # Format time
        if isinstance(created_at, str):
            try:
                time_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except:
                time_obj = datetime.now()
        else:
            time_obj = created_at if hasattr(created_at, 'strftime') else datetime.now()
        
        time_str = time_obj.strftime("%b %d, %H:%M")
        # Stack time above the action so it looks like a notification meta line
        time_label = ctk.CTkLabel(
            actions_frame,
            text=time_str,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_light']
        )
        time_label.pack(anchor="e", pady=(0, 4))
        
        # 'Done' acts as "seen" / "mark as read"
        if not is_read:
            mark_read_btn = ctk.CTkButton(
                actions_frame,
                text="Done",
                width=70,
                height=26,
                command=lambda nid=notif_id: self.mark_as_read(nid),
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_dark'],
                font=ctk.CTkFont(size=11, weight="bold")
            )
            mark_read_btn.pack(anchor="e")
        else:
            status_label = ctk.CTkLabel(
                actions_frame,
                text="Seen",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_light']
            )
            status_label.pack(anchor="e")
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'],
            anchor="w",
            justify="left",
            wraplength=600
        )
        message_label.pack(fill="x", anchor="w")
    
    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        if self.db.execute_query("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,)):
            self.load_notifications()
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        if self.db.execute_query("UPDATE notifications SET is_read = 1 WHERE is_read = 0"):
            messagebox.showinfo("Success", "All notifications marked as read")
            self.load_notifications()
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        if self.db.execute_query("DELETE FROM notifications WHERE id = ?", (notification_id,)):
            self.load_notifications()
    
    def clear_all(self):
        """Clear all notifications"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all notifications?"):
            if self.db.execute_query("DELETE FROM notifications"):
                messagebox.showinfo("Success", "All notifications cleared")
                self.load_notifications()
    
    def refresh_notifications(self):
        """Refresh notifications list"""
        self.load_notifications()


def check_low_stock(db, threshold=10):
    """Check for low stock products and create notifications (only if low_stock_alerts is on)."""
    if not db:
        return
    try:
        from utils.settings_manager import SettingsManager
        if not SettingsManager().get("low_stock_alerts", True):
            return
    except Exception:
        pass

    # Get products with low stock
    low_stock_products = db.fetch_all(
        "SELECT id, product_id, name, quantity FROM products WHERE quantity > 0 AND quantity <= ?",
        (threshold,)
    )
    
    out_of_stock_products = db.fetch_all(
        "SELECT id, product_id, name, quantity FROM products WHERE quantity = 0"
    )
    
    # Create notifications for low stock
    for product in low_stock_products:
        product_id, prod_id, name, qty = product[1], product[1], product[2], product[3]
        
        # Check if notification already exists for this product
        existing = db.fetch_one(
            "SELECT id FROM notifications WHERE type = 'low_stock' AND message LIKE ? AND is_read = 0",
            (f"%{name}%",)
        )
        
        if not existing:
            db.execute_query(
                "INSERT INTO notifications (type, title, message, is_read) VALUES (?, ?, ?, ?)",
                (
                    'low_stock',
                    f'Low Stock Alert',
                    f'Product "{name}" (ID: {prod_id}) is running low. Current stock: {qty} units.',
                    0
                )
            )
    
    # Create notifications for out of stock
    for product in out_of_stock_products:
        product_id, prod_id, name, qty = product[1], product[1], product[2], product[3]
        
        # Check if notification already exists for this product
        existing = db.fetch_one(
            "SELECT id FROM notifications WHERE type = 'out_of_stock' AND message LIKE ? AND is_read = 0",
            (f"%{name}%",)
        )
        
        if not existing:
            db.execute_query(
                "INSERT INTO notifications (type, title, message, is_read) VALUES (?, ?, ?, ?)",
                (
                    'out_of_stock',
                    f'Out of Stock Alert',
                    f'Product "{name}" (ID: {prod_id}) is out of stock. Please restock immediately.',
                    0
                )
            )


def check_expiry_reminders(db, days_ahead=30):
    """Create notifications for products expiring soon (only if expiry_reminders is on)."""
    if not db:
        return
    try:
        from utils.settings_manager import SettingsManager
        if not SettingsManager().get("expiry_reminders", True):
            return
    except Exception:
        return
    try:
        from datetime import timedelta
        today = datetime.now().date()
        end = today + timedelta(days=days_ahead)
        rows = db.fetch_all(
            "SELECT id, product_id, name, expiry_date FROM products WHERE expiry_date IS NOT NULL AND date(expiry_date) <= date(?) AND date(expiry_date) >= date(?)",
            (end, today)
        )
        for row in rows:
            pid, prod_id, name, exp = row[0], row[1], row[2], row[3]
            existing = db.fetch_one(
                "SELECT id FROM notifications WHERE type = 'expiry' AND message LIKE ? AND is_read = 0",
                (f"%{name}%",)
            )
            if not existing:
                db.execute_query(
                    "INSERT INTO notifications (type, title, message, is_read) VALUES (?, ?, ?, ?)",
                    ("expiry", "Expiry Reminder", f'Product "{name}" expires on {exp}. Consider using or restocking.', 0)
                )
    except Exception:
        pass


def check_payment_reminders(db):
    """Create a notification for pending customer dues (only if payment_reminders is on)."""
    if not db:
        return
    try:
        from utils.settings_manager import SettingsManager
        if not SettingsManager().get("payment_reminders", True):
            return
    except Exception:
        return
    try:
        row = db.fetch_one(
            "SELECT COUNT(*), COALESCE(SUM(due_amount), 0) FROM customers WHERE due_amount > 0"
        )
        if not row or (row[0] == 0 and row[1] == 0):
            return
        count, total = int(row[0]), float(row[1])
        existing = db.fetch_one(
            "SELECT id FROM notifications WHERE type = 'payment_reminder' AND is_read = 0 LIMIT 1"
        )
        if not existing:
            sym = SettingsManager().get_currency_symbol()
            db.execute_query(
                "INSERT INTO notifications (type, title, message, is_read) VALUES (?, ?, ?, ?)",
                ("payment_reminder", "Payment Reminder", f"{count} customer(s) have pending dues (total {sym} {total:,.2f}).", 0)
            )
    except Exception:
        pass

