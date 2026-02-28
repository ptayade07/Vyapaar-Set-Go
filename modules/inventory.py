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
            values=["All Categories", "Grains", "Dairy", "Staples", "Produce", "Bakery", "Beverages"],
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
        
        headers = ["Product ID", "Name", "Category", "Quantity", "Unit Price (₹)", "Expiry Date", "Actions"]
        widths = [100, 200, 100, 80, 120, 120, 100]
        
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
        query = "SELECT id, product_id, name, category, quantity, unit_price, expiry_date FROM products WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR product_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if category and category != "All Categories":
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY product_id"
        
        products = self.db.fetch_all(query, tuple(params) if params else None)
        
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

        product_id, name, category, quantity, unit_price, expiry_date = product[1:7]
        product_db_id = product[0]

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
            width=100,
        )
        id_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Name
        name_label = ctk.CTkLabel(
            row_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=200,
            anchor="w",
        )
        name_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")

        # Category
        cat_label = ctk.CTkLabel(
            row_frame,
            text=category,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=100,
        )
        cat_label.grid(row=0, column=2, padx=15, pady=12, sticky="w")

        # Quantity
        qty_label = ctk.CTkLabel(
            row_frame,
            text=str(quantity),
            font=ctk.CTkFont(size=12, weight="bold" if quantity <= 10 else "normal"),
            text_color=COLORS['error'] if quantity <= 10 else COLORS['text'],
            width=80,
        )
        qty_label.grid(row=0, column=3, padx=15, pady=12, sticky="w")

        # Unit Price
        price_label = ctk.CTkLabel(
            row_frame,
            text=f"₹ {unit_price:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=120,
        )
        price_label.grid(row=0, column=4, padx=15, pady=12, sticky="w")

        # Expiry Date
        exp_date = expiry_date.strftime("%Y-%m-%d") if expiry_date else "N/A"
        exp_label = ctk.CTkLabel(
            row_frame,
            text=exp_date,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=120,
        )
        exp_label.grid(row=0, column=5, padx=15, pady=12, sticky="w")

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=6, padx=15, pady=12)

        select_btn = ctk.CTkButton(
            actions_frame,
            text="⋯",
            width=30,
            height=30,
            command=lambda pid=product_db_id: self.select_product(pid),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            font=ctk.CTkFont(size=16),
        )
        select_btn.pack()

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
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to edit")
            return

        dialog = ProductDialog(self, self.db, self.selected_product)
        self.wait_window(dialog)
        self.selected_product = None
        self.load_products()

    def delete_product(self):
        """Delete selected product"""
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            product_id = self.selected_product[0]
            if self.db.execute_query("DELETE FROM products WHERE id = ?", (product_id,)):
                messagebox.showinfo("Success", "Product deleted successfully")
                self.selected_product = None
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to delete product")


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
        fields = [
            ("Name", "name", "Product Name"),
            ("Category", "category", "Grains"),
            ("Quantity", "quantity", "0"),
            ("Unit Price (₹)", "unit_price", "0.00"),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date", "2025-12-31"),
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
                    values=["Grains", "Dairy", "Staples", "Produce", "Bakery", "Beverages"],
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
        
        # Pre-fill if editing
        if self.product_data:
            self.entries["name"].insert(0, self.product_data[2])
            self.entries["category"].set(self.product_data[3])
            self.entries["quantity"].insert(0, str(self.product_data[4]))
            self.entries["unit_price"].insert(0, str(self.product_data[5]))
            if self.product_data[6]:
                self.entries["expiry_date"].insert(0, self.product_data[6].strftime("%Y-%m-%d"))
        
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
            quantity = int(self.entries["quantity"].get())
            unit_price = float(self.entries["unit_price"].get())
            expiry_date_str = self.entries["expiry_date"].get().strip()
            
            expiry_date = None
            if expiry_date_str:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            
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
                query = """UPDATE products SET name=?, category=?, quantity=?, 
                          unit_price=?, expiry_date=? WHERE id=?"""
                params = (name, category, quantity, unit_price, expiry_date, self.product_data[0])
            else:
                # Insert with auto-generated product ID
                product_id = self.generate_product_id()
                query = """INSERT INTO products (product_id, name, category, quantity, unit_price, expiry_date) 
                          VALUES (?, ?, ?, ?, ?, ?)"""
                params = (product_id, name, category, quantity, unit_price, expiry_date)
            
            if self.db.execute_query(query, params):
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

