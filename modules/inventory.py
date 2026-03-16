"""
Inventory Management module
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime
import re


class Inventory(ctk.CTkFrame):
    """Inventory Management module"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.selected_product = None
        self.selected_row_frame = None  # Track selected row for visual feedback
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        """Setup inventory UI"""
        # Header section
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Inventory Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Manage your product stock, prices, and expiry dates efficiently.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        subtitle_label.pack(side="left", padx=10)
        
        # Search and filter section
        filter_frame = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=10)
        filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search products by name or ID...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=15, pady=15)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_products(search_entry.get()))
        
        category_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All Categories", "Grains", "Dairy", "Staples", "Produce", "Bakery", "Beverages", "Others"],
            height=35,
            font=ctk.CTkFont(size=12),
            command=lambda v: self.filter_by_category(v)
        )
        category_filter.pack(side="left", padx=10, pady=15)
        category_filter.set("All Categories")
        
        stock_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All Stock Levels", "In Stock", "Low Stock", "Out of Stock"],
            height=35,
            font=ctk.CTkFont(size=12),
            command=lambda v: self.filter_by_stock(v)
        )
        stock_filter.pack(side="left", padx=10, pady=15)
        stock_filter.set("All Stock Levels")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        add_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Add Product",
            command=self.show_add_product_dialog,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit Product",
            command=self.show_edit_product_dialog,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete Product",
            command=self.delete_product,
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        delete_btn.pack(side="left", padx=5)
        
        # Inventory summary cards
        summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        summary_frame.pack(fill="x", padx=20, pady=(0, 12))

        def create_summary_card(parent, title):
            card = ctk.CTkFrame(
                parent,
                fg_color=COLORS['surface'],
                corner_radius=10,
                border_width=1,
                border_color=COLORS.get('border', COLORS['secondary'])
            )
            card.pack(side="left", fill="x", expand=True, padx=5)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=12)

            title_label = ctk.CTkLabel(
                inner,
                text=title,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
                anchor="w",
            )
            title_label.pack(anchor="w")

            value_label = ctk.CTkLabel(
                inner,
                text="–",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLORS['text'],
                anchor="w",
            )
            value_label.pack(anchor="w", pady=(4, 0))

            return value_label

        self.summary_total_products = create_summary_card(summary_frame, "Total Products")
        self.summary_low_stock = create_summary_card(summary_frame, "Low Stock Products")
        self.summary_inventory_value = create_summary_card(summary_frame, "Inventory Value")

        # Products table
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        table_label = ctk.CTkLabel(
            table_frame,
            text="Product List",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        table_label.pack(pady=15)
        
        # Scrollable table
        self.table_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Table headers
        self.setup_table_headers()
        
        # Products list (will be populated)
        self.products_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        self.products_frame.pack(fill="x")
        
        # Pagination
        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.pack(pady=15)
        
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        self.page_label.pack(side="left", padx=10)
    
    def setup_table_headers(self):
        """Setup table headers"""
        headers_frame = ctk.CTkFrame(
            self.table_scroll, 
            fg_color=COLORS['surface'], 
            corner_radius=10,
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary'])
        )
        headers_frame.pack(fill="x", pady=(0, 10))
        
        # Slightly wider columns so the table uses more of the page width
        headers = ["Product ID", "Name", "Category", "Quantity", "Unit Price (₹)", "Expiry Date", "Status", "Actions"]
        widths = [120, 260, 130, 90, 140, 140, 120, 180]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text'],
                width=width
            )
            label.grid(row=0, column=i, padx=15, pady=14, sticky="w")
    
    def load_products(self, search_term="", category="", stock_level=""):
        """Load products from database"""
        # Clear existing products
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # Build query
        query = "SELECT id, product_id, name, category, quantity, unit_price, expiry_date, brand, supplier_id, purchase_price, unit_type FROM products WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR product_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if category and category != "All Categories":
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY product_id"
        
        products = self.db.fetch_all(query, tuple(params) if params else None)

        # Inventory summary uses all products (before stock-level filtering)
        if products:
            total_products = len(products)
            low_stock_count = sum(1 for p in products if p[4] <= 10 and p[4] > 0)
            inventory_value = 0.0
            for p in products:
                qty = p[4]
                purchase_price = p[9] if p[9] is not None else p[5]
                inventory_value += qty * float(purchase_price)
            self.summary_total_products.configure(text=str(total_products))
            self.summary_low_stock.configure(text=str(low_stock_count))
            self.summary_inventory_value.configure(text=f"₹ {inventory_value:,.2f}")
        else:
            self.summary_total_products.configure(text="0")
            self.summary_low_stock.configure(text="0")
            self.summary_inventory_value.configure(text="₹ 0.00")
        
        # Filter by stock level if needed
        if stock_level and stock_level != "All Stock Levels":
            filtered_products = []
            for product in products:
                qty = product[4]
                if stock_level == "In Stock" and qty > 10:
                    filtered_products.append(product)
                elif stock_level == "Low Stock" and 0 < qty <= 10:
                    filtered_products.append(product)
                elif stock_level == "Out of Stock" and qty == 0:
                    filtered_products.append(product)
            products = filtered_products
        
        # Display products
        for idx, product in enumerate(products):
            self.create_product_row(product, idx % 2 == 0)
    
    def create_product_row(self, product, even_row=False):
        """Create a product row in the table"""
        row_bg = COLORS.get('surface_hover', COLORS['surface']) if even_row else COLORS['background']
        row_frame = ctk.CTkFrame(
            self.products_frame,
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

        # Make row clickable
        row_frame.bind("<Button-1>", lambda e, pid=product[0]: self.select_product(pid))

        product_db_id = product[0]
        product_id, name, category, quantity, unit_price, expiry_date = product[1:7]
        brand = product[7]
        supplier_id = product[8]
        purchase_price = product[9]
        unit_type = product[10]

        # Ensure expiry_date is a date object for display
        if expiry_date and isinstance(expiry_date, str):
            try:
                expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            except ValueError:
                expiry_date = None

        # Product ID
        id_label = ctk.CTkLabel(
            row_frame,
            text=product_id,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=120,
        )
        id_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Name
        name_label = ctk.CTkLabel(
            row_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=260,
            anchor="w",
        )
        name_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")

        # Category
        cat_label = ctk.CTkLabel(
            row_frame,
            text=category,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=130,
        )
        cat_label.grid(row=0, column=2, padx=15, pady=12, sticky="w")

        # Quantity
        qty_label = ctk.CTkLabel(
            row_frame,
            text=str(quantity),
            font=ctk.CTkFont(size=12, weight="bold" if quantity <= 10 else "normal"),
            text_color=COLORS['error'] if quantity <= 5 else (COLORS['warning'] if quantity <= 10 else COLORS['text']),
            width=90,
        )
        qty_label.grid(row=0, column=3, padx=15, pady=12, sticky="w")

        # Unit Price
        price_label = ctk.CTkLabel(
            row_frame,
            text=f"₹ {unit_price:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=140,
        )
        price_label.grid(row=0, column=4, padx=15, pady=12, sticky="w")

        # Expiry Date with warning if approaching (use settings date format)
        from utils.settings_manager import SettingsManager
        sm = SettingsManager()
        if expiry_date:
            exp_date = sm.format_date(expiry_date)
        else:
            exp_date = "N/A"
        exp_color = COLORS['text']
        if expiry_date:
            days_diff = (expiry_date - datetime.now().date()).days
            if days_diff <= 0:
                exp_color = COLORS['error']
                exp_date += " (Expired)"
            elif days_diff <= 7:
                exp_color = COLORS['warning']
                exp_date += " (Soon)"

        exp_label = ctk.CTkLabel(
            row_frame,
            text=exp_date,
            font=ctk.CTkFont(size=12),
            text_color=exp_color,
            width=140,
        )
        exp_label.grid(row=0, column=5, padx=15, pady=12, sticky="w")

        # Stock status indicator
        if quantity <= 5:
            status_text = "Critical"
            status_color = COLORS['error']
        elif quantity <= 10:
            status_text = "Low Stock"
            status_color = COLORS['warning']
        elif quantity == 0:
            status_text = "Out of Stock"
            status_color = COLORS['secondary']
        else:
            status_text = "In Stock"
            status_color = COLORS['success']

        status_label = ctk.CTkLabel(
            row_frame,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
            fg_color=status_color,
            corner_radius=999,
            width=120,
        )
        status_label.grid(row=0, column=6, padx=15, pady=12, sticky="w")

        # Actions: compact three-button cluster (View / Edit / Delete)
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=7, padx=8, pady=8, sticky="e")

        btn_font = ctk.CTkFont(size=11)

        view_btn = ctk.CTkButton(
            actions_frame,
            text="Details",
            width=55,
            height=26,
            fg_color=COLORS['surface'],
            hover_color=COLORS.get('surface_hover', COLORS['surface']),
            text_color=COLORS['text'],
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary']),
            corner_radius=6,
            font=btn_font,
            command=lambda pid=product_db_id: self.view_product(pid),
        )
        view_btn.pack(side="left", padx=2)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=55,
            height=26,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            text_color="white",
            border_width=0,
            corner_radius=6,
            font=btn_font,
            command=lambda pid=product_db_id: self.edit_product_from_row(pid),
        )
        edit_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=65,
            height=26,
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            text_color="white",
            border_width=0,
            corner_radius=6,
            font=btn_font,
            command=lambda pid=product_db_id: self.delete_product_from_row(pid),
        )
        del_btn.pack(side="left", padx=2)

        # Store product data in row_frame
        row_frame.product_data = product

    def select_product(self, product_id):
        """Select a product for editing"""
        query = "SELECT * FROM products WHERE id = ?"
        product = self.db.fetch_one(query, (product_id,))
        if product:
            # Reset previous selection visual
            if self.selected_row_frame:
                self.selected_row_frame.configure(fg_color=COLORS['surface'])

            # Find and highlight the selected row
            for widget in self.products_frame.winfo_children():
                if hasattr(widget, 'product_data') and widget.product_data[0] == product_id:
                    widget.configure(fg_color=COLORS['primary'], corner_radius=5)
                    self.selected_row_frame = widget
                    break

            self.selected_product = product
            messagebox.showinfo(
                "Product Selected",
                f"Product '{product[2]}' selected. You can now edit or delete it.",
            )

    def edit_product_from_row(self, product_id):
        self.select_product(product_id)
        if self.selected_product:
            self.show_edit_product_dialog()

    def delete_product_from_row(self, product_id):
        self.select_product(product_id)
        if self.selected_product:
            self.delete_product()

    def view_product(self, product_id):
        product = self.db.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        dialog = ProductDetailDialog(self, self.db, product)
        self.wait_window(dialog)

    def quick_update_stock(self, product_id):
        product = self.db.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        dialog = QuickStockDialog(self, self.db, product)
        self.wait_window(dialog)
        self.load_products()

    def show_product_history(self, product_id):
        product = self.db.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        dialog = ProductHistoryDialog(self, self.db, product)
        self.wait_window(dialog)

    def filter_products(self, search_term):
        """Filter products by search term"""
        self.load_products(search_term=search_term)

    def filter_by_category(self, category):
        """Filter products by category"""
        self.load_products(category=category)

    def filter_by_stock(self, stock_level):
        """Filter products by stock level"""
        self.load_products(stock_level=stock_level)

    def show_add_product_dialog(self):
        """Show add product dialog"""
        dialog = ProductDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_products()

    def show_edit_product_dialog(self):
        """Show edit product dialog"""
        dialog = ProductSelectDialog(self, self.db, mode="edit")
        self.wait_window(dialog)
        selected = getattr(dialog, "selected_product", None)
        if selected:
            edit_dialog = ProductDialog(self, self.db, selected)
            self.wait_window(edit_dialog)
            self.load_products()

    def delete_product(self):
        """Delete selected product"""
        dialog = ProductMultiDeleteDialog(self, self.db)
        self.wait_window(dialog)
        if getattr(dialog, "deleted_any", False):
            self.load_products()


class ProductDialog(ctk.CTkToplevel):
    """Product add/edit dialog"""
    
    def __init__(self, parent, db, product_data=None):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup dialog UI"""
        title = "Edit Product" if self.product_data else "Add Product"
        self.title(title)
        self.geometry("420x550")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        # Make modal and center
        self.transient(self.master)
        self.grab_set()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)
        
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Scrollable frame for form fields
        scroll_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Form fields (Product ID is auto-generated, not shown in form)
        from utils.settings_manager import SettingsManager
        sm = SettingsManager()
        date_format = sm.get("date_format", "YYYY-MM-DD")
        # Placeholder example based on selected format
        if date_format == "DD-MM-YYYY":
            expiry_label_text = "Expiry Date (DD-MM-YYYY)"
            expiry_example = "31-12-2025"
        elif date_format == "MM/DD/YYYY":
            expiry_label_text = "Expiry Date (MM/DD/YYYY)"
            expiry_example = "12/31/2025"
        else:
            expiry_label_text = "Expiry Date (YYYY-MM-DD)"
            expiry_example = "2025-12-31"

        fields = [
            ("Name", "name", "Product Name"),
            ("Category", "category", "Grains"),
            ("Quantity", "quantity", "0"),
            ("Unit Price (₹)", "unit_price", "0.00"),
            ("Purchase Price (₹)", "purchase_price", "0.00"),
            ("Unit Type (kg / litre / piece)", "unit_type", "kg / litre / piece"),
            ("Brand", "brand", "Brand Name"),
            (expiry_label_text, "expiry_date", expiry_example),
        ]
        
        self.entries = {}
        
        for label, key, placeholder in fields:
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text'],
                anchor="w"
            ).pack(fill="x", pady=(0, 3))
            
            if key == "category":
                entry = ctk.CTkComboBox(
                    frame,
                    values=["Grains", "Dairy", "Staples", "Produce", "Bakery", "Beverages", "Others"],
                    height=38,
                    font=ctk.CTkFont(size=12)
                )
            elif key == "unit_type":
                entry = ctk.CTkComboBox(
                    frame,
                    values=["kg", "L", "p"],
                    height=38,
                    font=ctk.CTkFont(size=12)
                )
            else:
                entry = ctk.CTkEntry(
                    frame,
                    placeholder_text=placeholder,
                    height=38,
                    font=ctk.CTkFont(size=12)
                )
            
            entry.pack(fill="x")
            self.entries[key] = entry

        # Supplier mapping (optional)
        supplier_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        supplier_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            supplier_frame,
            text="Supplier",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(fill="x", pady=(0, 3))

        suppliers = self.db.fetch_all("SELECT id, name FROM suppliers ORDER BY name")
        self.supplier_map = {f"{row[1]} (ID {row[0]})": row[0] for row in suppliers}
        supplier_values = ["-- None --"] + list(self.supplier_map.keys())

        self.supplier_combo = ctk.CTkComboBox(
            supplier_frame,
            values=supplier_values,
            height=38,
            font=ctk.CTkFont(size=12)
        )
        self.supplier_combo.pack(fill="x")
        self.supplier_combo.set("-- None --")
        
        # Pre-fill if editing
        if self.product_data:
            self.entries["name"].insert(0, self.product_data[2])
            self.entries["category"].set(self.product_data[3])
            self.entries["quantity"].insert(0, str(self.product_data[4]))
            self.entries["unit_price"].insert(0, str(self.product_data[5]))
            if self.product_data[6]:
                # expiry_date might be a date object or string
                try:
                    from utils.settings_manager import SettingsManager
                    sm = SettingsManager()
                    display_date = sm.format_date(self.product_data[6])
                except Exception:
                    try:
                        display_date = self.product_data[6].strftime("%Y-%m-%d")
                    except AttributeError:
                        display_date = str(self.product_data[6])
                self.entries["expiry_date"].insert(0, display_date)
            # Additional fields: indices 9-12: brand, supplier_id, purchase_price, unit_type
            if len(self.product_data) > 9:
                self.entries["brand"].insert(0, self.product_data[9] or "")
                supplier_id = self.product_data[10]
                if supplier_id:
                    for label_text, sid in self.supplier_map.items():
                        if sid == supplier_id:
                            self.supplier_combo.set(label_text)
                            break
                if self.product_data[11] is not None:
                    self.entries["purchase_price"].insert(0, str(self.product_data[11]))
                if self.product_data[12]:
                    self.entries["unit_type"].set(self.product_data[12])
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save_product,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        # Center dialog on screen
        self.update_idletasks()
        width = 420
        height = 550
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def generate_product_id(self):
        """Generate next available product ID (PROD001, PROD002, etc.)"""
        # Get all product IDs that match PROD### pattern
        all_products = self.db.fetch_all("SELECT product_id FROM products WHERE product_id LIKE 'PROD%'")
        
        if not all_products:
            # No products yet, start with PROD001
            return "PROD001"
        
        # Extract numbers from existing IDs and find the maximum
        max_num = 0
        for product in all_products:
            product_id = product[0]
            try:
                # Extract number after "PROD" prefix (e.g., PROD001 -> 1)
                num_str = product_id[4:] if len(product_id) > 4 else ""
                if num_str.isdigit():
                    num = int(num_str)
                    if num > max_num:
                        max_num = num
            except:
                continue
        
        # Generate next ID
        next_num = max_num + 1
        return f"PROD{next_num:03d}"
    
    def save_product(self):
        """Save product to database"""
        try:
            name = self.entries["name"].get().strip()
            category = self.entries["category"].get()
            qty_str = self.entries["quantity"].get().strip()
            quantity = float(qty_str or 0)
            unit_price = float(self.entries["unit_price"].get())
            purchase_price_raw = self.entries.get("purchase_price").get().strip()
            try:
                purchase_price = float(purchase_price_raw or 0)
            except ValueError:
                purchase_price = 0.0
            unit_type = self.entries.get("unit_type").get().strip()
            brand = self.entries.get("brand").get().strip()
            expiry_date_str = self.entries["expiry_date"].get().strip()
            supplier_value = self.supplier_combo.get() if hasattr(self, "supplier_combo") else "-- None --"
            supplier_id = self.supplier_map.get(supplier_value) if supplier_value in self.supplier_map else None
            
            expiry_date = None
            if expiry_date_str:
                # Parse according to current date format setting, then store as ISO (YYYY-MM-DD)
                from utils.settings_manager import SettingsManager
                sm = SettingsManager()
                fmt = sm.get("date_format", "YYYY-MM-DD")
                try:
                    if fmt == "DD-MM-YYYY":
                        expiry_date = datetime.strptime(expiry_date_str, "%d-%m-%Y").date()
                    elif fmt == "MM/DD/YYYY":
                        expiry_date = datetime.strptime(expiry_date_str, "%m/%d/%Y").date()
                    else:
                        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Invalid Date", f"Please enter expiry date in {fmt} format.")
                    return

                # Do not allow past expiry dates
                today = datetime.now().date()
                if expiry_date < today:
                    messagebox.showerror("Invalid Date", "Expiry date cannot be in the past.")
                    return
            
            # Validate required fields
            if not name:
                messagebox.showerror("Error", "Product name is required")
                return
            if quantity < 0:
                messagebox.showerror("Error", "Quantity cannot be negative")
                return
            if unit_price < 0:
                messagebox.showerror("Error", "Unit price cannot be negative")
                return
            
            if self.product_data:
                # Update (keep existing product_id)
                old_quantity = float(self.product_data[4])
                quantity_change = quantity - old_quantity

                query = """UPDATE products SET name=?, category=?, quantity=?,
                          unit_price=?, expiry_date=?, brand=?, supplier_id=?, purchase_price=?, unit_type=?
                          WHERE id=?"""
                params = (
                    name,
                    category,
                    quantity,
                    unit_price,
                    expiry_date,
                    brand,
                    supplier_id,
                    purchase_price,
                    unit_type,
                    self.product_data[0],
                )
            else:
                # Insert with auto-generated product ID
                product_id = self.generate_product_id()
                quantity_change = quantity
                query = """INSERT INTO products (product_id, name, category, quantity, unit_price, expiry_date,
                          brand, supplier_id, purchase_price, unit_type) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (
                    product_id,
                    name,
                    category,
                    quantity,
                    unit_price,
                    expiry_date,
                    brand,
                    supplier_id,
                    purchase_price,
                    unit_type,
                )
            
            if self.db.execute_query(query, params):
                # Record product history for quantity change
                if quantity_change != 0:
                    prod_id = self.product_data[0] if self.product_data else self.db.fetch_one(
                        "SELECT id FROM products WHERE product_id = ?", (product_id,)
                    )[0]
                    change_type = "Initial Stock" if not self.product_data else "Edit Stock"
                    self.db.execute_query(
                        "INSERT INTO product_history (product_id, change_type, quantity_change, note) VALUES (?, ?, ?, ?)",
                        (prod_id, change_type, quantity_change, ""),
                    )
                # Check for low stock notifications after saving product
                from modules.notifications import check_low_stock
                check_low_stock(self.db)
                messagebox.showinfo("Success", "Product saved successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save product. Please check the database connection.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input values:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class QuickStockDialog(ctk.CTkToplevel):
    """Quick stock update dialog"""

    def __init__(self, parent, db, product_data):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.setup_dialog()

    def setup_dialog(self):
        self.title("Quick Stock Update")
        self.geometry("320x220")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        name_label = ctk.CTkLabel(
            container,
            text=self.product_data[2],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text'],
        )
        name_label.pack(pady=(0, 10))

        current_qty = self.product_data[4]
        current_label = ctk.CTkLabel(
            container,
            text=f"Current stock: {current_qty}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'],
        )
        current_label.pack(pady=(0, 10))

        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="New Quantity",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))

        self.qty_entry = ctk.CTkEntry(
            frame,
            placeholder_text=str(current_qty),
            height=38,
            font=ctk.CTkFont(size=12),
        )
        self.qty_entry.pack(fill="x")

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Update",
            command=self.save,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=36,
            font=ctk.CTkFont(size=13),
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)

    def save(self):
        try:
            qty_str = self.qty_entry.get().strip()
            new_qty = float(qty_str or 0)
            if new_qty < 0:
                messagebox.showerror("Error", "Quantity cannot be negative")
                return

            product_id = self.product_data[0]
            old_qty = float(self.product_data[4])
            change = new_qty - old_qty

            if not self.db.execute_query(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (new_qty, product_id),
            ):
                messagebox.showerror("Error", "Failed to update stock")
                return

            if change != 0:
                self.db.execute_query(
                    "INSERT INTO product_history (product_id, change_type, quantity_change, note) VALUES (?, ?, ?, ?)",
                    (product_id, "Quick Stock Update", change, ""),
                )

            messagebox.showinfo("Success", "Stock updated successfully")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity (number).")


class ProductHistoryDialog(ctk.CTkToplevel):
    """Product history dialog"""

    def __init__(self, parent, db, product_data):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.setup_dialog()

    def setup_dialog(self):
        product_name = self.product_data[2]
        product_id = self.product_data[0]

        self.title(f"History - {product_name}")
        self.geometry("520x380")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text=f"Product History - {product_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 15))

        table_frame = ctk.CTkFrame(container, fg_color=COLORS['background'], corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        headers_frame = ctk.CTkFrame(table_frame, fg_color=COLORS['surface'])
        headers_frame.pack(fill="x", padx=10, pady=10)

        headers = ["Date", "Type", "Qty Change", "Note"]
        widths = [140, 120, 80, 180]
        for i, (h, w) in enumerate(zip(headers, widths)):
            lbl = ctk.CTkLabel(
                headers_frame,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text'],
                width=w,
            )
            lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

        body = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        rows = self.db.fetch_all(
            "SELECT created_at, change_type, quantity_change, note FROM product_history WHERE product_id = ? ORDER BY created_at DESC",
            (product_id,),
        )

        if not rows:
            lbl = ctk.CTkLabel(
                body,
                text="No history available for this product.",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light'],
            )
            lbl.pack(pady=20)
        else:
            for r in rows:
                row_frame = ctk.CTkFrame(body, fg_color=COLORS['surface'], corner_radius=6)
                row_frame.pack(fill="x", pady=3, padx=4)

                date_str = str(r[0])
                ctype = r[1]
                qty_change = r[2]
                note = r[3] or ""

                vals = [date_str, ctype, f"{qty_change:+d}", note]
                for i, (val, w) in enumerate(zip(vals, widths)):
                    lbl = ctk.CTkLabel(
                        row_frame,
                        text=val,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text'],
                        width=w,
                        anchor="w",
                    )
                    lbl.grid(row=0, column=i, padx=8, pady=4, sticky="w")

        close_btn = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=34,
            font=ctk.CTkFont(size=12),
        )
        close_btn.pack(pady=(8, 0))


class ProductDetailDialog(ctk.CTkToplevel):
    """Read-only product details, including extra fields"""

    def __init__(self, parent, db, product_data):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.setup_dialog()

    def setup_dialog(self):
        p = self.product_data
        self.title(f"Product Details - {p[2]}")
        self.geometry("420x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        title_label = ctk.CTkLabel(
            container,
            text="Product Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 15))

        def row(label_text, value_text):
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", pady=4)
            ctk.CTkLabel(
                frame,
                text=label_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
                width=140,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                frame,
                text=value_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text'],
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

        product_id = p[1]
        name = p[2]
        category = p[3]
        quantity = p[4]
        unit_price = p[5]
        expiry_date = p[6]
        # products columns: id, product_id, name, category, quantity, unit_price,
        # expiry_date, created_at, updated_at, brand, supplier_id, purchase_price, unit_type
        brand = p[9] if len(p) > 9 else None
        supplier_id = p[10] if len(p) > 10 else None
        purchase_price = p[11] if len(p) > 11 else None
        unit_type = p[12] if len(p) > 12 else None

        supplier_name = "N/A"
        if supplier_id:
            row_sup = self.db.fetch_one("SELECT name FROM suppliers WHERE id = ?", (supplier_id,))
            if row_sup:
                supplier_name = row_sup[0]

        # Handle expiry as date or string
        if expiry_date:
            try:
                exp_str = expiry_date.strftime("%Y-%m-%d")
            except AttributeError:
                exp_str = str(expiry_date)
        else:
            exp_str = "N/A"

        row("Product ID", product_id)
        row("Name", name)
        row("Category", category)
        row("Quantity", str(quantity))
        row("Unit Price", f"₹ {unit_price:,.2f}")
        row("Purchase Price", f"₹ {purchase_price:,.2f}" if purchase_price is not None else "N/A")
        row("Unit Type", unit_type or "N/A")
        row("Brand", brand or "N/A")
        row("Supplier", supplier_name)
        row("Expiry Date", exp_str)

        close_btn = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=36,
            font=ctk.CTkFont(size=12),
        )
        close_btn.pack(pady=(16, 0))


class ProductSelectDialog(ctk.CTkToplevel):
    """Dialog to search & pick a single product (for editing)"""

    def __init__(self, parent, db, mode="edit"):
        super().__init__(parent)
        self.db = db
        self.mode = mode
        self.selected_product = None
        self.setup_dialog()

    def setup_dialog(self):
        self.title("Select Product")
        self.geometry("520x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text="Select a product to edit",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 10))

        search_entry = ctk.CTkEntry(
            container,
            placeholder_text="Search by name or ID...",
            height=34,
            font=ctk.CTkFont(size=12),
        )
        search_entry.pack(fill="x", pady=(0, 10))

        table = ctk.CTkScrollableFrame(container, fg_color=COLORS['background'])
        table.pack(fill="both", expand=True)

        self.rows_frame = table

        def reload(term=""):
            for w in self.rows_frame.winfo_children():
                w.destroy()
            query = "SELECT id, product_id, name, category, quantity FROM products WHERE 1=1"
            params = []
            if term:
                query += " AND (name LIKE ? OR product_id LIKE ?)"
                like = f"%{term}%"
                params.extend([like, like])
            query += " ORDER BY product_id"
            products = self.db.fetch_all(query, tuple(params) if params else None)
            for p in products:
                row = ctk.CTkFrame(self.rows_frame, fg_color=COLORS['surface'], corner_radius=6)
                row.pack(fill="x", pady=3, padx=4)
                text = f"{p[1]}  •  {p[2]}  •  {p[3]}  •  Qty: {p[4]}"
                lbl = ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text'],
                    anchor="w",
                )
                lbl.pack(fill="x", padx=10, pady=6)

                def on_click(_e=None, pid=p[0]):
                    product = self.db.fetch_one("SELECT * FROM products WHERE id = ?", (pid,))
                    if product:
                        self.selected_product = product
                        self.destroy()

                row.bind("<Button-1>", on_click)
                lbl.bind("<Button-1>", on_click)

        search_entry.bind("<KeyRelease>", lambda e: reload(search_entry.get()))
        reload()

        close_btn = ctk.CTkButton(
            container,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=34,
            font=ctk.CTkFont(size=12),
        )
        close_btn.pack(pady=(8, 0))


class ProductMultiDeleteDialog(ctk.CTkToplevel):
    """Dialog to multi-select products and delete them"""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.deleted_any = False
        self.check_vars = []
        self.products = []
        self.setup_dialog()

    def setup_dialog(self):
        self.title("Delete Products")
        self.geometry("540x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text="Select products to delete",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 10))

        search_entry = ctk.CTkEntry(
            container,
            placeholder_text="Search by name or ID...",
            height=34,
            font=ctk.CTkFont(size=12),
        )
        search_entry.pack(fill="x", pady=(0, 10))

        table = ctk.CTkScrollableFrame(container, fg_color=COLORS['background'])
        table.pack(fill="both", expand=True)

        self.rows_frame = table

        def reload(term=""):
            for w in self.rows_frame.winfo_children():
                w.destroy()
            self.check_vars.clear()
            self.products.clear()

            query = "SELECT id, product_id, name, category, quantity FROM products WHERE 1=1"
            params = []
            if term:
                query += " AND (name LIKE ? OR product_id LIKE ?)"
                like = f"%{term}%"
                params.extend([like, like])
            query += " ORDER BY product_id"
            products = self.db.fetch_all(query, tuple(params) if params else None)
            self.products = products

            for p in products:
                row = ctk.CTkFrame(self.rows_frame, fg_color=COLORS['surface'], corner_radius=6)
                row.pack(fill="x", pady=3, padx=4)

                var = ctk.BooleanVar(value=False)
                self.check_vars.append((var, p[0]))

                chk = ctk.CTkCheckBox(
                    row,
                    text="",
                    variable=var,
                    width=20,
                    checkbox_width=18,
                    checkbox_height=18,
                )
                chk.pack(side="left", padx=8)

                text = f"{p[1]}  •  {p[2]}  •  {p[3]}  •  Qty: {p[4]}"
                lbl = ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text'],
                    anchor="w",
                )
                lbl.pack(side="left", fill="x", expand=True, padx=4, pady=6)

        search_entry.bind("<KeyRelease>", lambda e: reload(search_entry.get()))
        reload()

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Selected",
            command=self.delete_selected,
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        delete_btn.pack(side="left", fill="x", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=34,
            font=ctk.CTkFont(size=12),
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)

    def delete_selected(self):
        ids_to_delete = [pid for var, pid in self.check_vars if var.get()]
        if not ids_to_delete:
            messagebox.showwarning("No Selection", "Please select at least one product to delete")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(ids_to_delete)} selected products?"):
            return
        ok = True
        for pid in ids_to_delete:
            if not self.db.execute_query("DELETE FROM products WHERE id = ?", (pid,)):
                ok = False
        if ok:
            messagebox.showinfo("Success", "Selected products deleted successfully")
            self.deleted_any = True
            self.destroy()
        else:
            messagebox.showerror("Error", "Some products could not be deleted")

