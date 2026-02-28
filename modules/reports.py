"""
Reports module
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class Reports(ctk.CTkFrame):
    """Reports module"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.current_filter = "daily"
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        """Setup reports UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Reports",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        # Filter tabs and actions
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Tabs
        tabs_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        tabs_frame.pack(side="left")
        
        self.daily_btn = ctk.CTkButton(
            tabs_frame,
            text="Daily",
            command=lambda: self.set_filter("daily"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.daily_btn.pack(side="left", padx=5)
        
        self.monthly_btn = ctk.CTkButton(
            tabs_frame,
            text="Monthly",
            command=lambda: self.set_filter("monthly"),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.monthly_btn.pack(side="left", padx=5)
        
        self.custom_btn = ctk.CTkButton(
            tabs_frame,
            text="Custom Range",
            command=lambda: self.set_filter("custom"),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.custom_btn.pack(side="left", padx=5)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.load_reports,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=35,
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.pack(side="left", padx=5)
        
        csv_btn = ctk.CTkButton(
            actions_frame,
            text="📥 Download CSV",
            command=self.download_csv,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        csv_btn.pack(side="left", padx=5)
        
        print_btn = ctk.CTkButton(
            actions_frame,
            text="🖨️ Print Report",
            command=self.print_report,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        print_btn.pack(side="left", padx=5)
        
        # Summary cards
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['background'])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Charts section
        charts_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        charts_frame.pack(fill="x", pady=(0, 20))
        
        # Sales Overview Chart
        sales_chart_frame = ctk.CTkFrame(charts_frame, fg_color=COLORS['surface'], corner_radius=10)
        sales_chart_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        sales_label = ctk.CTkLabel(
            sales_chart_frame,
            text="Sales Overview",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        sales_label.pack(pady=15)
        
        self.sales_chart_canvas = ctk.CTkFrame(sales_chart_frame, fg_color="transparent")
        self.sales_chart_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Profit Trend Chart
        profit_chart_frame = ctk.CTkFrame(charts_frame, fg_color=COLORS['surface'], corner_radius=10)
        profit_chart_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        profit_label = ctk.CTkLabel(
            profit_chart_frame,
            text="Profit Trend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        profit_label.pack(pady=15)
        
        self.profit_chart_canvas = ctk.CTkFrame(profit_chart_frame, fg_color="transparent")
        self.profit_chart_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Detailed Report Table
        table_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS['surface'], corner_radius=10)
        table_frame.pack(fill="both", expand=True)
        
        table_label = ctk.CTkLabel(
            table_frame,
            text="Detailed Report Data",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        table_label.pack(pady=15)
        
        # Table scroll
        self.table_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Table headers
        headers_frame = ctk.CTkFrame(
            self.table_scroll, 
            fg_color=COLORS['surface'], 
            corner_radius=10,
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary'])
        )
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Date", "Total Sales", "Total Profit", "Transactions", "Avg. Transaction Value"]
        widths = [120, 120, 120, 120, 150]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text'],
                width=width
            )
            label.grid(row=0, column=i, padx=15, pady=14, sticky="w")
        
        # Table data
        self.table_data_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        self.table_data_frame.pack(fill="x")
    
    def set_filter(self, filter_type):
        """Set report filter"""
        self.current_filter = filter_type
        
        # Update button colors
        if filter_type == "daily":
            self.daily_btn.configure(fg_color=COLORS['primary'])
            self.monthly_btn.configure(fg_color=COLORS['secondary'])
            self.custom_btn.configure(fg_color=COLORS['secondary'])
        elif filter_type == "monthly":
            self.daily_btn.configure(fg_color=COLORS['secondary'])
            self.monthly_btn.configure(fg_color=COLORS['primary'])
            self.custom_btn.configure(fg_color=COLORS['secondary'])
        else:
            self.daily_btn.configure(fg_color=COLORS['secondary'])
            self.monthly_btn.configure(fg_color=COLORS['secondary'])
            self.custom_btn.configure(fg_color=COLORS['primary'])
        
        self.load_reports()
    
    def load_reports(self):
        """Load report data"""
        # Clear existing charts and summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        for widget in self.sales_chart_canvas.winfo_children():
            widget.destroy()
        for widget in self.profit_chart_canvas.winfo_children():
            widget.destroy()
        for widget in self.table_data_frame.winfo_children():
            widget.destroy()
        
        # Get date range based on filter
        if self.current_filter == "daily":
            start_date = datetime.now().date() - timedelta(days=6)
            end_date = datetime.now().date()
            date_format = "%b %d"
        elif self.current_filter == "monthly":
            start_date = datetime.now().date().replace(day=1) - timedelta(days=30)
            end_date = datetime.now().date()
            date_format = "%b %d"
        else:
            # Custom range - for now use last 7 days
            start_date = datetime.now().date() - timedelta(days=6)
            end_date = datetime.now().date()
            date_format = "%b %d"
        
        # Fetch sales data
        query = """SELECT date(sale_date) as sale_date, 
                  SUM(final_amount) as total_sales,
                  COUNT(*) as transactions
                  FROM sales 
                  WHERE date(sale_date) BETWEEN ? AND ?
                  GROUP BY date(sale_date)
                  ORDER BY sale_date"""
        
        sales_data = self.db.fetch_all(query, (start_date, end_date))
        
        # Prepare data for charts
        dates = []
        sales = []
        profits = []
        transactions = []
        
        for row in sales_data:
            date_str, total_sales, trans_count = row
            # SQLite returns date as string, parse it if needed
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    dates.append(date_obj.strftime(date_format))
                except:
                    dates.append(date_str[:5])  # Use first 5 chars if parsing fails
            else:
                dates.append(date_str.strftime(date_format) if hasattr(date_str, 'strftime') else str(date_str))
            sales.append(float(total_sales))
            # Calculate profit (assuming 30% margin for demo)
            profit = float(total_sales) * 0.3
            profits.append(profit)
            transactions.append(trans_count)
        
        # Create Sales Overview Chart with dark mode support
        from utils.chart_utils import get_chart_colors, configure_chart_dark_mode
        colors = get_chart_colors()
        
        if sales:
            fig1, ax1 = plt.subplots(figsize=(8, 4), facecolor=colors['figure_bg'])
            fig1, ax1 = configure_chart_dark_mode(fig1, ax1)
            
            ax1.plot(dates, sales, color='#f97316', marker='o', linewidth=2, markersize=6)
            ax1.fill_between(dates, sales, alpha=0.3, color='#f97316')
            ax1.set_ylabel('Sales (₹)', fontsize=10)
            ax1.set_xlabel('Date', fontsize=10)
            ax1.set_title('Sales Overview', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas1 = FigureCanvasTkAgg(fig1, self.sales_chart_canvas)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
        
        # Create Profit Trend Chart with dark mode support
        if profits:
            fig2, ax2 = plt.subplots(figsize=(8, 4), facecolor=colors['figure_bg'])
            fig2, ax2 = configure_chart_dark_mode(fig2, ax2)
            
            ax2.bar(dates, profits, color='#22c55e', alpha=0.8)
            ax2.set_ylabel('Profit (₹)', fontsize=10)
            ax2.set_xlabel('Date', fontsize=10)
            ax2.set_title('Profit Trend', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas2 = FigureCanvasTkAgg(fig2, self.profit_chart_canvas)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
        
        # Create summary cards
        if sales_data:
            total_sales = sum(float(row[1]) for row in sales_data)
            total_profit = total_sales * 0.3
            total_transactions = sum(row[2] for row in sales_data)
            avg_transaction = total_sales / total_transactions if total_transactions > 0 else 0
            
            self.create_summary_card("Total Sales", f"₹ {total_sales:,.2f}", COLORS['primary'])
            self.create_summary_card("Total Profit", f"₹ {total_profit:,.2f}", COLORS['success'])
            self.create_summary_card("Transactions", f"{total_transactions:,}", COLORS['secondary'])
            self.create_summary_card("Avg. Transaction", f"₹ {avg_transaction:,.2f}", COLORS['warning'])
        
        # Create detailed table
        for idx, row in enumerate(sales_data):
            date_str, total_sales, trans_count = row
            profit = float(total_sales) * 0.3
            avg_trans = float(total_sales) / trans_count if trans_count > 0 else 0
            
            # Format date string for display
            if isinstance(date_str, str):
                display_date = date_str
            else:
                display_date = date_str.strftime("%Y-%m-%d") if hasattr(date_str, 'strftime') else str(date_str)
            
            row_bg = COLORS.get('surface_hover', COLORS['surface']) if idx % 2 == 0 else COLORS['background']
            row_frame = ctk.CTkFrame(
                self.table_data_frame,
                fg_color=row_bg,
                corner_radius=8,
                border_width=1,
                border_color=COLORS.get('border', COLORS['secondary'])
            )
            row_frame.pack(fill="x", pady=4)
            
            # Add hover effect
            def on_enter(e):
                row_frame.configure(fg_color=COLORS.get('surface_hover', COLORS['surface']))
            def on_leave(e):
                row_frame.configure(fg_color=row_bg)
            
            row_frame.bind("<Enter>", on_enter)
            row_frame.bind("<Leave>", on_leave)
            
            # Date
            date_label = ctk.CTkLabel(
                row_frame,
                text=display_date,
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=120
            )
            date_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
            
            # Total Sales
            sales_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {total_sales:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=120
            )
            sales_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
            
            # Total Profit
            profit_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {profit:,.2f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['primary'],
                width=120
            )
            profit_label.grid(row=0, column=2, padx=15, pady=12, sticky="w")
            
            # Transactions
            trans_label = ctk.CTkLabel(
                row_frame,
                text=str(trans_count),
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=120
            )
            trans_label.grid(row=0, column=3, padx=15, pady=12, sticky="w")
            
            # Avg Transaction Value
            avg_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {avg_trans:.2f}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=150
            )
            avg_label.grid(row=0, column=4, padx=15, pady=12, sticky="w")
    
    def download_csv(self):
        """Download report as CSV"""
        messagebox.showinfo("Download CSV", "CSV download functionality can be implemented here")
    
    def create_summary_card(self, title, value, color):
        """Create a summary card"""
        card = ctk.CTkFrame(self.summary_frame, fg_color=COLORS['surface'], corner_radius=10)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        value_label = ctk.CTkLabel(
            content_frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="w")
    
    def print_report(self):
        """Print report"""
        messagebox.showinfo("Print Report", "Print functionality can be implemented here")

