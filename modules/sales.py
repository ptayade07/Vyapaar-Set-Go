"""Sales/Billing module"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime
import uuid
from modules.khata import CustomerDialog


class Sales(ctk.CTkFrame):
    """Sales/Billing module"""
    
    def __init__(self, parent, db=None, on_data_change=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.cart = []  # List of (product_id, name, quantity, unit_price, total)
        self.customer_options = []
        self.customer_display_map = {}
        self.selected_customer_id = None
        self.customer_combo = None
        self.on_data_change = on_data_change  # Callback to refresh other pages
        self.setup_ui()
        self.load_products()
        self.load_customers_for_billing()
    
    def setup_ui(self):
        """Setup sales UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Sales / Billing",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        # Main content - split into two panels
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Product Search
        left_panel = ctk.CTkFrame(main_frame, fg_color=COLORS['surface'], corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header section with icon
        header_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_section.pack(fill="x", padx=15, pady=(15, 10))
        
        product_label = ctk.CTkLabel(
            header_section,
            text="📦 Product Search",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        product_label.pack(side="left")
        
        # Search bar with improved styling
        search_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_container.pack(fill="x", padx=15, pady=(0, 15))
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="🔍 Search products by name or ID...",
            height=45,
            font=ctk.CTkFont(size=13),
            border_width=2,
            border_color=COLORS.get('border', COLORS['secondary'])
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_products())
        
        # Products grid with better layout
        self.products_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Container for product grid (will use grid layout)
        self.products_frame = ctk.CTkFrame(self.products_scroll, fg_color="transparent")
        self.products_frame.pack(fill="both", expand=True)
        
        # Right panel - Current Bill
        right_panel = ctk.CTkFrame(main_frame, fg_color=COLORS['surface'], corner_radius=12, width=400)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)

        # Header section
        bill_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        bill_header.pack(fill="x", padx=15, pady=(15, 10))
        
        bill_label = ctk.CTkLabel(
            bill_header,
            text="🧾 Current Bill",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        bill_label.pack(side="left")

        # Customer selection section
        customer_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        customer_frame.pack(fill="x", padx=15, pady=(0, 10))

        customer_label = ctk.CTkLabel(
            customer_frame,
            text="Customer",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
        )
        customer_label.pack(side="left")

        self.customer_combo = ctk.CTkComboBox(
            customer_frame,
            values=["Walk-in / Cash"],
            width=200,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.on_customer_selected,
        )
        self.customer_combo.pack(side="left", padx=(10, 5))
        self.customer_combo.set("Walk-in / Cash")

        add_customer_btn = ctk.CTkButton(
            customer_frame,
            text="+ Add",
            width=60,
            height=30,
            command=self.add_customer_from_billing,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            font=ctk.CTkFont(size=12),
        )
        add_customer_btn.pack(side="left")
        
        # Bill items
        self.bill_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.bill_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.bill_items_frame = ctk.CTkFrame(self.bill_scroll, fg_color="transparent")
        self.bill_items_frame.pack(fill="x")
        
        # Bill summary with improved styling
        summary_frame = ctk.CTkFrame(right_panel, fg_color=COLORS.get('surface_hover', COLORS['background']), corner_radius=10, border_width=1, border_color=COLORS.get('border', COLORS['secondary']))
        summary_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Subtotal
        subtotal_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        subtotal_frame.pack(fill="x", padx=15, pady=10)
        
        subtotal_label = ctk.CTkLabel(
            subtotal_frame,
            text="Subtotal:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        subtotal_label.pack(side="left")
        
        self.subtotal_label = ctk.CTkLabel(
            subtotal_frame,
            text="₹ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        self.subtotal_label.pack(side="right")
        
        # Discount
        discount_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        discount_frame.pack(fill="x", padx=15, pady=10)
        
        discount_label = ctk.CTkLabel(
            discount_frame,
            text="Discount:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        discount_label.pack(side="left")
        
        self.discount_entry = ctk.CTkEntry(
            discount_frame,
            placeholder_text="0",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.discount_entry.pack(side="right")
        self.discount_entry.bind("<KeyRelease>", lambda e: self.update_totals())

        # Amount Paid (by customer right now)
        amount_paid_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        amount_paid_frame.pack(fill="x", padx=15, pady=10)

        amount_paid_label = ctk.CTkLabel(
            amount_paid_frame,
            text="Amount Paid Now:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        amount_paid_label.pack(side="left")

        self.amount_paid_entry = ctk.CTkEntry(
            amount_paid_frame,
            placeholder_text="0",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.amount_paid_entry.pack(side="right")
        
        # Grand Total
        total_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        total_frame.pack(fill="x", padx=15, pady=10)
        
        total_label = ctk.CTkLabel(
            total_frame,
            text="Grand Total:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        total_label.pack(side="left")
        
        self.grand_total_label = ctk.CTkLabel(
            total_frame,
            text="₹ 0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['primary']
        )
        self.grand_total_label.pack(side="right")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        print_btn = ctk.CTkButton(
            btn_frame,
            text="🖨️ Print Bill",
            command=self.print_bill,
            fg_color=COLORS['surface'],
            hover_color=COLORS['background'],
            text_color=COLORS['text'],
            border_width=1,
            border_color=COLORS['secondary'],
            height=40,
            font=ctk.CTkFont(size=14)
        )
        print_btn.pack(fill="x", pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save Transaction",
            command=self.save_transaction,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(fill="x")
    
    def load_products(self, search_term=""):
        """Load products for sale"""
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        query = "SELECT id, product_id, name, unit_price, quantity FROM products WHERE quantity > 0"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR product_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY name"
        
        products = self.db.fetch_all(query, tuple(params) if params else None)
        
        # Configure grid for 3 columns (do this once before creating cards)
        for col in range(3):
            self.products_frame.grid_columnconfigure(col, weight=1, uniform="product_cols")
        
        # Display products in a grid layout (3 columns)
        products_per_row = 3
        for i, product in enumerate(products):
            row = i // products_per_row
            col = i % products_per_row
            self.create_product_card(product, row, col)

    def load_customers_for_billing(self):
        """Load customers into the billing customer dropdown"""
        customers = self.db.fetch_all(
            "SELECT id, name, phone FROM customers ORDER BY name"
        )

        self.customer_options = ["Walk-in / Cash"]
        self.customer_display_map = {}

        for row in customers:
            cid, name, phone = row[0], row[1], row[2]
            display = f"{name} ({phone})"
            self.customer_options.append(display)
            self.customer_display_map[display] = cid

        if self.customer_combo is not None:
            self.customer_combo.configure(values=self.customer_options)
            # Restore previous selection if possible
            if self.selected_customer_id is None:
                self.customer_combo.set("Walk-in / Cash")
            else:
                for display, cid in self.customer_display_map.items():
                    if cid == self.selected_customer_id:
                        self.customer_combo.set(display)
                        break

    def on_customer_selected(self, value: str):
        """Handle customer selection from dropdown"""
        if value == "Walk-in / Cash":
            self.selected_customer_id = None
        else:
            self.selected_customer_id = self.customer_display_map.get(value)

    def add_customer_from_billing(self):
        """Open the add-customer dialog from the billing screen"""
        dialog = CustomerDialog(self, self.db, None)
        self.wait_window(dialog)
        # Reload customers so the new one appears in the dropdown
        self.load_customers_for_billing()
    
    def create_product_card(self, product, row, col):
        """Create a product card with improved styling in grid layout"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        product_db_id, product_id, name, unit_price, quantity = product
        
        # Create card with surface color for better contrast
        card = ctk.CTkFrame(
            self.products_frame,
            fg_color=COLORS['surface'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary'])
        )
        # Use grid layout for better arrangement (3 columns)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Product name with better styling
        name_label = ctk.CTkLabel(
            card,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text'],
            wraplength=150,
            anchor="w"
        )
        name_label.pack(pady=(15, 8), padx=15, anchor="w")
        
        # Price with better styling
        price_label = ctk.CTkLabel(
            card,
            text=f"₹ {unit_price:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['primary']
        )
        price_label.pack(pady=(0, 12))
        
        # Stock indicator
        stock_label = ctk.CTkLabel(
            card,
            text=f"Stock: {quantity}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_light']
        )
        stock_label.pack(pady=(0, 10))
        
        # Quantity selector with improved design
        qty_frame = ctk.CTkFrame(card, fg_color="transparent")
        qty_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        minus_btn = ctk.CTkButton(
            qty_frame,
            text="−",
            width=35,
            height=35,
            command=lambda pid=product_db_id, pname=name, price=unit_price: self.decrease_quantity(pid, pname, price),
            fg_color=COLORS.get('surface_hover', COLORS['surface']),
            hover_color=COLORS['secondary'],
            text_color=COLORS['text'],
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=8
        )
        minus_btn.pack(side="left")
        
        qty_label = ctk.CTkLabel(
            qty_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text'],
            width=50,
            fg_color=COLORS['background'],
            corner_radius=8
        )
        qty_label.pack(side="left", padx=8)
        
        plus_btn = ctk.CTkButton(
            qty_frame,
            text="+",
            width=35,
            height=35,
            command=lambda pid=product_db_id, pname=name, price=unit_price, qty=quantity: self.increase_quantity(pid, pname, price, qty),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color="white",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=8
        )
        plus_btn.pack(side="left")
        
        # Store quantity label reference
        card.qty_label = qty_label
        card.product_data = product
    
    def increase_quantity(self, product_db_id, product_name, unit_price, available_qty):
        """Increase product quantity in cart"""
        # Find if product already in cart
        cart_item = None
        for item in self.cart:
            if item[0] == product_db_id:
                cart_item = item
                break
        
        if cart_item:
            current_qty = cart_item[2]
            if current_qty < available_qty:
                cart_item[2] += 1
                cart_item[4] = cart_item[2] * cart_item[3]
            else:
                messagebox.showwarning("Stock Limit", f"Only {available_qty} units available")
        else:
            if available_qty > 0:
                self.cart.append([product_db_id, product_name, 1, unit_price, unit_price])
            else:
                messagebox.showwarning("Out of Stock", "This product is out of stock")
        
        self.update_bill()
    
    def decrease_quantity(self, product_db_id, product_name, unit_price):
        """Decrease product quantity in cart"""
        for item in self.cart:
            if item[0] == product_db_id:
                if item[2] > 1:
                    item[2] -= 1
                    item[4] = item[2] * item[3]
                else:
                    self.cart.remove(item)
                break
        
        self.update_bill()
    
    def update_bill(self):
        """Update bill display"""
        # Clear bill items
        for widget in self.bill_items_frame.winfo_children():
            widget.destroy()
        
        if not self.cart:
            empty_label = ctk.CTkLabel(
                self.bill_items_frame,
                text="No items in cart",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            empty_label.pack(pady=20)
            self.subtotal_label.configure(text="₹ 0.00")
            self.grand_total_label.configure(text="₹ 0.00")
            return
        
        # Headers
        headers_frame = ctk.CTkFrame(self.bill_items_frame, fg_color=COLORS['background'], corner_radius=5)
        headers_frame.pack(fill="x", pady=(0, 5))
        
        headers = ["Item", "Qty", "Price", "Total", "Actions"]
        widths = [150, 50, 80, 80, 60]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text'],
                width=width
            )
            label.grid(row=0, column=i, padx=2, pady=5, sticky="w")
        
        # Bill items
        for item in self.cart:
            product_db_id, name, quantity, unit_price, total = item
            
            row_frame = ctk.CTkFrame(self.bill_items_frame, fg_color=COLORS['surface'], corner_radius=5)
            row_frame.pack(fill="x", pady=2)
            
            # Item name
            name_label = ctk.CTkLabel(
                row_frame,
                text=name[:20] + "..." if len(name) > 20 else name,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
                width=150,
                anchor="w"
            )
            name_label.grid(row=0, column=0, padx=2, pady=5, sticky="w")
            
            # Quantity
            qty_label = ctk.CTkLabel(
                row_frame,
                text=str(quantity),
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
                width=50
            )
            qty_label.grid(row=0, column=1, padx=2, pady=5, sticky="w")
            
            # Price
            price_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {unit_price:.2f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
                width=80
            )
            price_label.grid(row=0, column=2, padx=2, pady=5, sticky="w")
            
            # Total
            total_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {total:.2f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
                width=80
            )
            total_label.grid(row=0, column=3, padx=2, pady=5, sticky="w")
            
            # Remove button
            remove_btn = ctk.CTkButton(
                row_frame,
                text="-",
                width=30,
                height=25,
                command=lambda pid=product_db_id: self.remove_from_cart(pid),
                fg_color=COLORS['error'],
                hover_color="#dc2626",
                font=ctk.CTkFont(size=12)
            )
            remove_btn.grid(row=0, column=4, padx=2, pady=5)
        
        # Update totals
        self.update_totals()
    
    def remove_from_cart(self, product_db_id):
        """Remove item from cart"""
        self.cart = [item for item in self.cart if item[0] != product_db_id]
        self.update_bill()
    
    def update_totals(self):
        """Update bill totals"""
        subtotal = sum(item[4] for item in self.cart)
        self.subtotal_label.configure(text=f"₹ {subtotal:.2f}")
        
        # Discount
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        
        grand_total = max(0, subtotal - discount)
        self.grand_total_label.configure(text=f"₹ {grand_total:.2f}")
    
    def filter_products(self):
        """Filter products by search term"""
        search_term = self.search_entry.get()
        self.load_products(search_term)
    
    def save_transaction(self):
        """Save transaction to database and optionally link to a customer"""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add items to the cart")
            return
        
        try:
            # Calculate totals
            subtotal = sum(item[4] for item in self.cart)
            discount = float(self.discount_entry.get() or 0)
            grand_total = max(0, subtotal - discount)

            # How much customer is paying right now
            amount_paid_str = self.amount_paid_entry.get().strip() if hasattr(self, "amount_paid_entry") else ""
            amount_paid = float(amount_paid_str or 0)

            if amount_paid < 0:
                messagebox.showerror("Error", "Amount paid cannot be negative")
                return
            if amount_paid > grand_total:
                messagebox.showerror("Error", "Amount paid cannot be more than the grand total")
                return
            
            # Generate transaction ID
            transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"

            # Insert sale with optional customer_id
            sale_query = """INSERT INTO sales (transaction_id, total_amount, discount, final_amount, customer_id) 
                          VALUES (?, ?, ?, ?, ?)"""
            sale_params = (
                transaction_id,
                subtotal,
                discount,
                grand_total,
                self.selected_customer_id,
            )
            
            if not self.db.execute_query(sale_query, sale_params):
                messagebox.showerror("Error", "Failed to save transaction")
                return
            
            # Get sale ID
            sale_result = self.db.fetch_one("SELECT id FROM sales WHERE transaction_id = ?", (transaction_id,))
            if not sale_result:
                messagebox.showerror("Error", "Failed to retrieve sale ID")
                return
            
            sale_id = sale_result[0]

            # Insert sale items and update product quantities
            for item in self.cart:
                product_db_id, name, quantity, unit_price, total = item
                
                # Insert sale item
                item_query = """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price) 
                              VALUES (?, ?, ?, ?, ?)"""
                item_params = (sale_id, product_db_id, quantity, unit_price, total)
                
                if not self.db.execute_query(item_query, item_params):
                    messagebox.showerror("Error", f"Failed to save item: {name}")
                    return
                
                # Update product quantity
                update_query = "UPDATE products SET quantity = quantity - ? WHERE id = ?"
                if not self.db.execute_query(update_query, (quantity, product_db_id)):
                    messagebox.showerror("Error", f"Failed to update stock for: {name}")
                    return
            
            # Check for low stock notifications after sale
            from modules.notifications import check_low_stock
            check_low_stock(self.db)

            # If a customer is selected, update their Khata and record payment history
            if self.selected_customer_id is not None and grand_total > 0:
                # Unpaid portion goes to Khata
                unpaid_amount = grand_total - amount_paid

                if unpaid_amount > 0:
                    update_due_query = "UPDATE customers SET due_amount = due_amount + ? WHERE id = ?"
                    if not self.db.execute_query(update_due_query, (unpaid_amount, self.selected_customer_id)):
                        messagebox.showerror("Error", "Failed to update customer Khata")
                        return

                # Paid portion is stored as a payment record so it shows in history
                if amount_paid > 0:
                    payment_query = "INSERT INTO payments (customer_id, amount) VALUES (?, ?)"
                    if not self.db.execute_query(payment_query, (self.selected_customer_id, amount_paid)):
                        messagebox.showerror("Error", "Failed to record customer payment")
                        return

                    # Update last_payment_date for the customer
                    last_payment_update = "UPDATE customers SET last_payment_date = date('now') WHERE id = ?"
                    self.db.execute_query(last_payment_update, (self.selected_customer_id,))
            
            messagebox.showinfo("Success", f"Transaction saved successfully!\nTransaction ID: {transaction_id}")
            
            # Clear cart
            self.cart = []
            self.discount_entry.delete(0, "end")
            if hasattr(self, "amount_paid_entry"):
                self.amount_paid_entry.delete(0, "end")
            self.update_bill()
            self.load_products()
            
            # Refresh dashboard and other pages if callback is available
            if self.on_data_change:
                self.on_data_change()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def print_bill(self):
        """Print bill (placeholder - can be extended)"""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "No items to print")
            return
        
        # For now, just show a message
        # In a real application, this would generate a printable bill
        messagebox.showinfo("Print Bill", "Bill printing functionality can be implemented here")

