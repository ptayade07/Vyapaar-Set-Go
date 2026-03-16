"""
Reports module
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
import json
import tempfile
import webbrowser
import os
from utils.settings_manager import SettingsManager


class Reports(ctk.CTkFrame):
    """Reports module"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.current_filter = "daily"
        self.last_sales_data = []
        self.last_start_date = None
        self.last_end_date = None
        self.last_date_format = "%b %d"
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

        # Remember last loaded data and range for CSV/print
        self.last_sales_data = sales_data
        self.last_start_date = start_date
        self.last_end_date = end_date
        self.last_date_format = date_format
        
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
        _sym = SettingsManager().get_currency_symbol()

        if sales:
            fig1, ax1 = plt.subplots(figsize=(8, 4), facecolor=colors['figure_bg'])
            fig1, ax1 = configure_chart_dark_mode(fig1, ax1)
            
            ax1.plot(dates, sales, color='#f97316', marker='o', linewidth=2, markersize=6)
            ax1.fill_between(dates, sales, alpha=0.3, color='#f97316')
            ax1.set_ylabel(f'Sales ({_sym})', fontsize=10)
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
            ax2.set_ylabel(f'Profit ({_sym})', fontsize=10)
            ax2.set_xlabel('Date', fontsize=10)
            ax2.set_title('Profit Trend', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas2 = FigureCanvasTkAgg(fig2, self.profit_chart_canvas)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
        
        # Create summary cards (use currency from settings)
        if sales_data:
            sm = SettingsManager()
            sym = sm.get_currency_symbol()
            total_sales = sum(float(row[1]) for row in sales_data)
            total_profit = total_sales * 0.3
            total_transactions = sum(row[2] for row in sales_data)
            avg_transaction = total_sales / total_transactions if total_transactions > 0 else 0

            self.create_summary_card("Total Sales", f"{sym} {total_sales:,.2f}", COLORS['primary'])
            self.create_summary_card("Total Profit", f"{sym} {total_profit:,.2f}", COLORS['success'])
            self.create_summary_card("Transactions", f"{total_transactions:,}", COLORS['secondary'])
            self.create_summary_card("Avg. Transaction", f"{sym} {avg_transaction:,.2f}", COLORS['warning'])
        
        # Create detailed table
        for idx, row in enumerate(sales_data):
            date_str, total_sales, trans_count = row
            profit = float(total_sales) * 0.3
            avg_trans = float(total_sales) / trans_count if trans_count > 0 else 0
            
            # Format date string for display (use date_format from settings)
            try:
                display_date = SettingsManager().format_date(date_str)
            except Exception:
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
            
            # Total Sales (currency from settings)
            sales_label = ctk.CTkLabel(
                row_frame,
                text=f"{sym} {total_sales:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=120
            )
            sales_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
            
            # Total Profit
            profit_label = ctk.CTkLabel(
                row_frame,
                text=f"{sym} {profit:,.2f}",
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
                text=f"{sym} {avg_trans:.2f}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text'],
                width=150
            )
            avg_label.grid(row=0, column=4, padx=15, pady=12, sticky="w")
    
    def download_csv(self):
        """Download current report view as CSV or JSON based on export_format setting."""
        if not self.last_sales_data:
            messagebox.showinfo("Download", "No report data available for the selected period.")
            return

        sm = SettingsManager()
        export_fmt = (sm.get("export_format") or "CSV").strip().upper()
        if export_fmt not in ("CSV", "JSON", "EXCEL"):
            export_fmt = "CSV"
        sym = sm.get_currency_symbol()

        if export_fmt == "JSON":
            default_name = f"vyapaar_report_{self.current_filter}_{datetime.now().strftime('%Y%m%d')}.json"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile=default_name,
                title="Save report as JSON",
            )
        else:
            default_name = f"vyapaar_report_{self.current_filter}_{datetime.now().strftime('%Y%m%d')}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=default_name,
                title="Save report",
            )
        if not file_path:
            return

        try:
            rows_out = []
            for row in self.last_sales_data:
                date_str, total_sales, trans_count = row
                total_sales = float(total_sales)
                profit = total_sales * 0.3
                avg_trans = total_sales / trans_count if trans_count else 0.0
                display_date = sm.format_date(date_str) if date_str else ""
                rows_out.append({
                    "date": display_date,
                    "total_sales": total_sales,
                    "total_profit": profit,
                    "transactions": trans_count,
                    "avg_transaction": round(avg_trans, 2),
                })

            if export_fmt == "JSON":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(rows_out, f, indent=2)
                messagebox.showinfo("Download", f"Report saved as JSON:\n{file_path}")
                return
            # CSV (or Excel as CSV)
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Date", f"Total Sales ({sym})", f"Total Profit ({sym})", "Transactions", f"Avg. Transaction ({sym})"]
                )
                for r in rows_out:
                    writer.writerow([
                        r["date"],
                        f"{r['total_sales']:.2f}",
                        f"{r['total_profit']:.2f}",
                        r["transactions"],
                        f"{r['avg_transaction']:.2f}",
                    ])
            messagebox.showinfo("Download", f"Report saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Download", f"Failed to save:\n{e}")
    
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
        """Open current report as printable HTML in the browser."""
        if not self.last_sales_data:
            messagebox.showinfo("Print Report", "No report data available for the selected period.")
            return

        try:
            html = self._build_report_html()
            fd, path = tempfile.mkstemp(suffix=".html", prefix="vyapaar_report_")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open("file://" + path)
        except Exception as e:
            messagebox.showerror("Print Report", f"Failed to open printable report:\n{e}")

    def _build_report_html(self) -> str:
        """Generate a simple printable HTML report using last_sales_data."""
        sm = SettingsManager()
        sym = sm.get_currency_symbol()
        rows_html = []
        total_sales = 0.0
        total_profit = 0.0
        total_transactions = 0

        for row in self.last_sales_data:
            date_str, tsales, trans_count = row
            tsales = float(tsales)
            profit = tsales * 0.3
            avg_trans = tsales / trans_count if trans_count else 0.0
            total_sales += tsales
            total_profit += profit
            total_transactions += trans_count
            display_date = sm.format_date(date_str) if date_str else ""
            rows_html.append(
                f"<tr><td>{display_date}</td>"
                f"<td>{sym} {tsales:.2f}</td>"
                f"<td>{sym} {profit:.2f}</td>"
                f"<td>{trans_count}</td>"
                f"<td>{sym} {avg_trans:.2f}</td></tr>"
            )

        avg_transaction = total_sales / total_transactions if total_transactions else 0.0
        rows = "\n".join(rows_html)
        start = sm.format_date(self.last_start_date) if self.last_start_date else ""
        end = sm.format_date(self.last_end_date) if self.last_end_date else ""
        generated_on = datetime.now().strftime("%d %b %Y, %I:%M %p")

        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>VyapaarSetGo - Report</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 24px auto; padding: 16px; }}
h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
p.meta {{ color: #6b7280; font-size: 0.9rem; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }}
th {{ font-weight: 600; background-color: #f9fafb; }}
.summary {{ margin-top: 12px; font-size: 0.95rem; }}
.summary strong {{ font-weight: 600; }}
@media print {{ body {{ margin: 12px; }} }}
</style></head>
<body>
<h1>VyapaarSetGo - Sales Report</h1>
<p class="meta">Range: {start} to {end}<br>Generated on: {generated_on}</p>
<table>
  <thead>
    <tr>
      <th>Date</th>
      <th>Total Sales ({sym})</th>
      <th>Total Profit ({sym})</th>
      <th>Transactions</th>
      <th>Avg. Transaction ({sym})</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>
<div class="summary">
  <p><strong>Total Sales:</strong> {sym} {total_sales:.2f}</p>
  <p><strong>Total Profit (30% est.):</strong> {sym} {total_profit:.2f}</p>
  <p><strong>Total Transactions:</strong> {total_transactions}</p>
  <p><strong>Avg. Transaction:</strong> {sym} {avg_transaction:.2f}</p>
</div>
</body></html>"""

