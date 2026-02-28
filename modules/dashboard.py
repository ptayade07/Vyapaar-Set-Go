"""
Dashboard module for VyapaarSetGo
"""
import customtkinter as ctk
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class Dashboard(ctk.CTkFrame):
    """Dashboard with stats and charts"""
    
    def __init__(self, parent, on_navigate=None, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.on_navigate = on_navigate
        self.setup_dashboard()
        self.load_data()
    
    def setup_dashboard(self):
        """Setup dashboard UI"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['background'])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top row - Summary cards (4 cards)
        self.stats_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 20))
        
        # Middle row - Charts section (3 cards side by side)
        charts_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 20))
        
        # Left chart - Sales Trend (larger)
        self.sales_trend_frame = ctk.CTkFrame(charts_row, fg_color=COLORS['surface'], corner_radius=10)
        self.sales_trend_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Middle chart - Sales by Category (donut/pie style)
        self.category_frame = ctk.CTkFrame(charts_row, fg_color=COLORS['surface'], corner_radius=10)
        self.category_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right chart - Top Products (list style)
        self.top_products_frame = ctk.CTkFrame(charts_row, fg_color=COLORS['surface'], corner_radius=10)
        self.top_products_frame.pack(side="left", fill="both", expand=True)
        
        # Bottom row - Additional info (3 cards)
        bottom_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(0, 20))
        
        # Time-based sales
        self.time_sales_frame = ctk.CTkFrame(bottom_row, fg_color=COLORS['surface'], corner_radius=10)
        self.time_sales_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Products by Category
        self.products_category_frame = ctk.CTkFrame(bottom_row, fg_color=COLORS['surface'], corner_radius=10)
        self.products_category_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # This Month Summary
        self.month_summary_frame = ctk.CTkFrame(bottom_row, fg_color=COLORS['surface'], corner_radius=10)
        self.month_summary_frame.pack(side="left", fill="both", expand=True)
        
        # Quick Actions section (at the bottom)
        self.setup_quick_actions(scroll_frame)
    
    def setup_quick_actions(self, parent):
        """Setup quick action cards"""
        actions_label = ctk.CTkLabel(
            parent,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        actions_label.pack(anchor="w", pady=(20, 10))
        
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions = [
            ("➕", "Add New Product", "Efficiently add new inventory items to your stock.", "inventory"),
            ("📄", "Record New Sale", "Process a new transaction quickly and easily.", "sales"),
            ("💰", "Update Customer Payment", "Record a payment for customer credit accounts.", "khata"),
            ("📊", "View Sales Reports", "Access detailed reports on daily and monthly sales.", "reports"),
        ]
        
        for icon, title, desc, target_page in actions:
            card = ctk.CTkFrame(actions_frame, fg_color=COLORS['surface'], corner_radius=10)
            card.pack(side="left", fill="both", expand=True, padx=10)
            
            icon_label = ctk.CTkLabel(
                card,
                text=icon,
                font=ctk.CTkFont(size=32)
            )
            icon_label.pack(pady=(20, 10))
            
            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS['text']
            )
            title_label.pack(pady=(0, 5))
            
            desc_label = ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
                wraplength=200
            )
            desc_label.pack(pady=(0, 15), padx=15)
            
            action_btn = ctk.CTkButton(
                card,
                text=title.replace("New ", "").replace("Update ", "").replace("View ", ""),
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_dark'],
                height=35,
                font=ctk.CTkFont(size=12),
                command=(lambda p=target_page: self.on_navigate(p)) if self.on_navigate else None,
            )
            action_btn.pack(fill="x", padx=15, pady=(0, 20))
    
    def create_stat_card(self, parent, title, value, icon, color=COLORS['primary']):
        """Create a stat card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['surface'], corner_radius=10)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon and title
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        title_label.pack(side="left", padx=10)
        
        # Value
        value_label = ctk.CTkLabel(
            content_frame,
            text=str(value),
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="w")
        
        return card
    
    def load_data(self):
        """Load dashboard data"""
        # Get stats
        total_products = self.db.fetch_one("SELECT COUNT(*) FROM products")[0] or 0
        total_customers = self.db.fetch_one("SELECT COUNT(*) FROM customers")[0] or 0
        
        # Today's sales
        today = datetime.now().date()
        today_sales = self.db.fetch_one(
            "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE date(sale_date) = ?",
            (today,)
        )
        today_sales = today_sales[0] if today_sales else 0
        
        # Pending dues
        pending_dues = self.db.fetch_one(
            "SELECT COALESCE(SUM(due_amount), 0) FROM customers"
        )
        pending_dues = pending_dues[0] if pending_dues else 0
        
        # Create stat cards with different colors
        self.create_stat_card(self.stats_frame, "Total Products", f"{total_products:,}", "📦", COLORS['primary'])
        self.create_stat_card(self.stats_frame, "Total Customers", f"{total_customers:,}", "👥", "#3b82f6")
        self.create_stat_card(self.stats_frame, "Today's Sales", f"₹ {today_sales:,.2f}", "🛒", COLORS['warning'])
        self.create_stat_card(
            self.stats_frame,
            "Pending Dues",
            f"₹ {pending_dues:,.2f}",
            "💳",
            "#ec4899"
        )
        
        # Load all charts and data
        self.load_charts()
        self.load_category_data()
        self.load_top_products()
        self.load_time_sales()
        self.load_products_by_category()
        self.load_month_summary()
    
    def load_charts(self):
        """Load sales trend chart"""
        # Get last 7 days sales
        dates = []
        sales = []
        
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            dates.append(date.strftime("%a"))
            
            result = self.db.fetch_one(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE date(sale_date) = ?",
                (date,)
            )
            sales.append(float(result[0]) if result else 0)
        
        # Title
        title_label = ctk.CTkLabel(
            self.sales_trend_frame,
            text="Sales Trend (Last 7 Days)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        # Chart canvas
        chart_canvas = ctk.CTkFrame(self.sales_trend_frame, fg_color="transparent")
        chart_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create matplotlib chart with dark mode support
        from utils.chart_utils import get_chart_colors, configure_chart_dark_mode
        colors = get_chart_colors()
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=colors['figure_bg'])
        fig, ax = configure_chart_dark_mode(fig, ax)
        
        ax.plot(dates, sales, color=COLORS['primary'], marker='o', linewidth=2, markersize=6)
        ax.fill_between(dates, sales, alpha=0.3, color=COLORS['primary'])
        ax.set_ylabel('Sales (₹)', fontsize=10)
        ax.set_xlabel('Day', fontsize=10)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def load_category_data(self):
        """Load sales by category (donut chart style)"""
        # Get category sales data
        query = """SELECT p.category, SUM(si.quantity * si.unit_price) as total
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.product_id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE date(s.sale_date) >= date('now', '-30 days')
                   GROUP BY p.category
                   ORDER BY total DESC
                   LIMIT 5"""
        
        category_data = self.db.fetch_all(query)
        
        title_label = ctk.CTkLabel(
            self.category_frame,
            text="Sales by Category",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        content_frame = ctk.CTkFrame(self.category_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        if category_data:
            total = sum(float(row[1]) for row in category_data)
            for category, amount in category_data:
                percentage = (float(amount) / total * 100) if total > 0 else 0
                
                item_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['background'], corner_radius=5)
                item_frame.pack(fill="x", pady=5)
                
                cat_label = ctk.CTkLabel(
                    item_frame,
                    text=category,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS['text']
                )
                cat_label.pack(side="left", padx=10, pady=8)
                
                amount_label = ctk.CTkLabel(
                    item_frame,
                    text=f"₹ {float(amount):,.2f} ({percentage:.1f}%)",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_light']
                )
                amount_label.pack(side="right", padx=10)
        else:
            no_data = ctk.CTkLabel(
                content_frame,
                text="No sales data available",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data.pack(pady=20)
    
    def load_top_products(self):
        """Load top selling products"""
        query = """SELECT p.name, SUM(si.quantity) as total_qty
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.product_id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE date(s.sale_date) >= date('now', '-30 days')
                   GROUP BY p.name
                   ORDER BY total_qty DESC
                   LIMIT 5"""
        
        top_products = self.db.fetch_all(query)
        
        title_label = ctk.CTkLabel(
            self.top_products_frame,
            text="Top Selling Products",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        content_frame = ctk.CTkFrame(self.top_products_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        if top_products:
            for i, (name, qty) in enumerate(top_products, 1):
                item_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['background'], corner_radius=5)
                item_frame.pack(fill="x", pady=5)
                
                rank_label = ctk.CTkLabel(
                    item_frame,
                    text=f"{i}.",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS['primary'],
                    width=30
                )
                rank_label.pack(side="left", padx=10, pady=8)
                
                name_label = ctk.CTkLabel(
                    item_frame,
                    text=name[:20] + "..." if len(name) > 20 else name,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text']
                )
                name_label.pack(side="left", padx=5)
                
                qty_label = ctk.CTkLabel(
                    item_frame,
                    text=f"{int(qty)} units",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_light']
                )
                qty_label.pack(side="right", padx=10)
        else:
            no_data = ctk.CTkLabel(
                content_frame,
                text="No product sales data",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data.pack(pady=20)
    
    def load_time_sales(self):
        """Load sales by time of day"""
        # Get hourly sales for today
        today = datetime.now().date()
        query = """SELECT strftime('%H', sale_date) as hour, SUM(final_amount) as total
                   FROM sales
                   WHERE date(sale_date) = ?
                   GROUP BY hour
                   ORDER BY hour"""
        
        time_data = self.db.fetch_all(query, (today,))
        
        title_label = ctk.CTkLabel(
            self.time_sales_frame,
            text="Sales by Time Today",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        chart_frame = ctk.CTkFrame(self.time_sales_frame, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        if time_data:
            hours = [f"{int(row[0])}:00" for row in time_data]
            amounts = [float(row[1]) for row in time_data]
            
            from utils.chart_utils import get_chart_colors, configure_chart_dark_mode
            colors = get_chart_colors()
            fig, ax = plt.subplots(figsize=(6, 3), facecolor=colors['figure_bg'])
            fig, ax = configure_chart_dark_mode(fig, ax)
            
            ax.plot(hours, amounts, color=COLORS['warning'], marker='o', linewidth=2)
            ax.fill_between(hours, amounts, alpha=0.3, color=COLORS['warning'])
            ax.set_ylabel('Sales (₹)', fontsize=9)
            ax.set_xlabel('Time', fontsize=9)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            no_data = ctk.CTkLabel(
                chart_frame,
                text="No sales today",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data.pack(pady=20)
    
    def load_products_by_category(self):
        """Load products count by category"""
        query = """SELECT category, COUNT(*) as count
                   FROM products
                   GROUP BY category
                   ORDER BY count DESC
                   LIMIT 5"""
        
        category_data = self.db.fetch_all(query)
        
        title_label = ctk.CTkLabel(
            self.products_category_frame,
            text="Products by Category",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        content_frame = ctk.CTkFrame(self.products_category_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        if category_data:
            for category, count in category_data:
                item_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['background'], corner_radius=5)
                item_frame.pack(fill="x", pady=5)
                
                cat_label = ctk.CTkLabel(
                    item_frame,
                    text=category,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text']
                )
                cat_label.pack(side="left", padx=10, pady=8)
                
                count_label = ctk.CTkLabel(
                    item_frame,
                    text=f"{count} products",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS['primary']
                )
                count_label.pack(side="right", padx=10)
        else:
            no_data = ctk.CTkLabel(
                content_frame,
                text="No categories",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data.pack(pady=20)
    
    def load_month_summary(self):
        """Load this month's summary"""
        # Get this month's sales
        first_day = datetime.now().replace(day=1).date()
        today = datetime.now().date()
        
        query = """SELECT SUM(final_amount) as total, COUNT(*) as count
                   FROM sales
                   WHERE date(sale_date) >= ? AND date(sale_date) <= ?"""
        
        result = self.db.fetch_one(query, (first_day, today))
        month_sales = float(result[0]) if result and result[0] else 0
        month_count = result[1] if result else 0
        
        title_label = ctk.CTkLabel(
            self.month_summary_frame,
            text="This Month Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=15)
        
        content_frame = ctk.CTkFrame(self.month_summary_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Large value
        value_label = ctk.CTkLabel(
            content_frame,
            text=f"₹ {month_sales:,.2f}",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['primary']
        )
        value_label.pack(pady=(10, 5))
        
        # Count
        count_label = ctk.CTkLabel(
            content_frame,
            text=f"{month_count} Transactions",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        count_label.pack()
        
        # Month name
        month_label = ctk.CTkLabel(
            content_frame,
            text=datetime.now().strftime("%B %Y"),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light']
        )
        month_label.pack(pady=(5, 0))

