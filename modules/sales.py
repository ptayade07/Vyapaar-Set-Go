"""Sales/Billing module"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime
import uuid
import webbrowser
import tempfile
import os
from modules.khata import CustomerDialog
from modules.refund_dialog import RefundDialog


class Sales(ctk.CTkFrame):
    """Sales/Billing module"""
    
    def __init__(self, parent, db=None, on_data_change=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.cart = []  # List of [product_id, name, quantity, unit_price, total]
        self.product_card_map = {}  # product_id -> card widget (for qty label updates)
        self.customer_options = []
        self.customer_display_map = {}
        self.selected_customer_id = None
        self.customer_combo = None
        self.on_data_change = on_data_change  # Callback to refresh other pages
        # Per-item discounts (rupees per line) keyed by product_id
        self.line_discounts = {}
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
        
        # Right panel - Current Bill (made wider so everything fits comfortably)
        right_panel = ctk.CTkFrame(main_frame, fg_color=COLORS['surface'], corner_radius=12, width=520)
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
        customer_frame.pack(fill="x", padx=15, pady=(0, 4))

        # First row: label + dropdown + add button
        customer_top_row = ctk.CTkFrame(customer_frame, fg_color="transparent")
        customer_top_row.pack(fill="x")

        customer_label = ctk.CTkLabel(
            customer_top_row,
            text="Customer",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
        )
        customer_label.pack(side="left")

        self.customer_combo = ctk.CTkComboBox(
            customer_top_row,
            values=["Walk-in / Cash"],
            width=220,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.on_customer_selected,
        )
        self.customer_combo.pack(side="left", padx=(10, 5))
        self.customer_combo.set("Walk-in / Cash")

        add_customer_btn = ctk.CTkButton(
            customer_top_row,
            text="+ Add",
            width=60,
            height=30,
            command=self.add_customer_from_billing,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            font=ctk.CTkFont(size=12),
        )
        add_customer_btn.pack(side="left")

        # Balance banner: visible card for Khata due / Advance (only shown when customer selected)
        self.customer_balance_frame = ctk.CTkFrame(
            customer_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        self.customer_balance_frame.pack(fill="x", pady=(6, 0))

        self.customer_balance_label = ctk.CTkLabel(
            self.customer_balance_frame,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_light'],
            anchor="w",
            justify="left",
        )
        self.customer_balance_label.pack(fill="x")
        # Inner colored banner (visibility controlled in on_customer_selected)
        self.customer_balance_banner = ctk.CTkFrame(
            self.customer_balance_frame,
            fg_color=COLORS.get('surface_hover', COLORS['background']),
            corner_radius=10,
            border_width=0,
        )
        self.customer_balance_banner.pack(fill="x", pady=(6, 0))
        self.customer_balance_banner_inner = ctk.CTkLabel(
            self.customer_balance_banner,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text'],
            anchor="w",
            justify="left",
        )
        self.customer_balance_banner_inner.pack(fill="x", padx=14, pady=12)
        # Hide banner until a customer with balance is selected
        self.customer_balance_banner.pack_forget()
        
        # Bill items
        self.bill_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.bill_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.bill_items_frame = ctk.CTkFrame(self.bill_scroll, fg_color="transparent")
        self.bill_items_frame.pack(fill="x")
        
        # Bill summary with improved styling
        summary_frame = ctk.CTkFrame(
            right_panel,
            fg_color=COLORS.get('surface_hover', COLORS['background']),
            corner_radius=10,
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary'])
        )
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

        # Tax / GST
        tax_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        tax_frame.pack(fill="x", padx=15, pady=10)

        tax_label = ctk.CTkLabel(
            tax_frame,
            text="GST (%):",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        tax_label.pack(side="left")

        self.tax_entry = ctk.CTkEntry(
            tax_frame,
            placeholder_text="0",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.tax_entry.pack(side="right")
        self.tax_entry.bind("<KeyRelease>", lambda e: self.update_totals())

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

        # Payment method selector
        payment_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        payment_frame.pack(fill="x", padx=15, pady=(0, 10))

        payment_label = ctk.CTkLabel(
            payment_frame,
            text="Payment Method:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        payment_label.pack(side="left")

        self.payment_method_combo = ctk.CTkComboBox(
            payment_frame,
            values=["Cash", "UPI", "Card", "Other"],
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
        )
        self.payment_method_combo.pack(side="right")
        self.payment_method_combo.set("Cash")
        
        # Hint about how Khata/advance is handled for customers
        self.khata_hint_label = ctk.CTkLabel(
            summary_frame,
            text="For saved customers, extra payment is stored as advance and existing Khata balance automatically adjusts this bill.",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_light'],
            wraplength=420,
            justify="left"
        )
        self.khata_hint_label.pack(fill="x", padx=15, pady=(0, 5))
        
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

        # Return / Refund button (opens a simple dialog)
        refund_btn = ctk.CTkButton(
            btn_frame,
            text="↩ Return / Refund",
            command=self.open_refund_dialog,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=36,
            font=ctk.CTkFont(size=13),
        )
        refund_btn.pack(fill="x", pady=(8, 0))

    def open_refund_dialog(self):
        """Open a simple dialog to record a return / refund against an existing bill."""
        RefundDialog(self, self.db)
    
    def load_products(self, search_term=""):
        """Load products for sale"""
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        # Reset mapping from product id to card when reloading
        self.product_card_map = {}
        
        query = "SELECT id, product_id, name, unit_price, quantity FROM products WHERE quantity > 0"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR product_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY name"
        
        products = self.db.fetch_all(query, tuple(params) if params else None)
        
        # Configure grid for 4 columns (tighter cards)
        for col in range(4):
            self.products_frame.grid_columnconfigure(col, weight=1, uniform="product_cols")
        
        # Display products in a grid layout (4 columns)
        products_per_row = 4
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

            # Enable basic search: filter dropdown options as user types
            def on_customer_search(_event=None):
                term = self.customer_combo.get().strip().lower()
                if not term:
                    filtered = self.customer_options
                else:
                    filtered = [opt for opt in self.customer_options if term in opt.lower()]
                    if not filtered:
                        filtered = self.customer_options
                self.customer_combo.configure(values=filtered)

            # Bind key release once (idempotent if called multiple times)
            try:
                self.customer_combo.unbind("<KeyRelease>")
            except Exception:
                pass
            self.customer_combo.bind("<KeyRelease>", on_customer_search)

    def on_customer_selected(self, value: str):
        """Handle customer selection from dropdown"""
        if value == "Walk-in / Cash":
            self.selected_customer_id = None
            if hasattr(self, "customer_balance_label") and self.customer_balance_label is not None:
                self.customer_balance_label.configure(text="", text_color=COLORS['text_light'])
            if hasattr(self, "customer_balance_banner"):
                self.customer_balance_banner.pack_forget()
        else:
            self.selected_customer_id = self.customer_display_map.get(value)
            if self.selected_customer_id is not None:
                row = self.db.fetch_one(
                    "SELECT due_amount FROM customers WHERE id = ?",
                    (self.selected_customer_id,),
                )
                balance = row[0] if row else 0
                try:
                    is_dark = ctk.get_appearance_mode() == "Dark"
                except Exception:
                    is_dark = False
                if balance > 0:
                    text = f"Khata due: ₹ {balance:,.2f}"
                    color = COLORS['error']
                    bg = "#7f1d1d" if is_dark else "#fef2f2"
                elif balance < 0:
                    text = f"Advance: ₹ {abs(balance):,.2f}"
                    color = COLORS['success']
                    bg = "#14532d" if is_dark else "#dcfce7"
                else:
                    text = "No Khata balance"
                    color = COLORS['text_light']
                    bg = COLORS.get('surface_hover', COLORS['background'])
                if hasattr(self, "customer_balance_label") and self.customer_balance_label is not None:
                    self.customer_balance_label.configure(text="Customer balance", text_color=COLORS['text_light'])
                if hasattr(self, "customer_balance_banner") and hasattr(self, "customer_balance_banner_inner"):
                    self.customer_balance_banner.configure(fg_color=bg)
                    self.customer_balance_banner_inner.configure(text=text, text_color=color)
                    self.customer_balance_banner.pack(fill="x", pady=(6, 0))

    def add_customer_from_billing(self):
        """Open the add-customer dialog from the billing screen"""
        dialog = CustomerDialog(self, self.db, None)
        self.wait_window(dialog)
        # Reload customers so the new one appears in the dropdown
        self.load_customers_for_billing()
    
    def create_product_card(self, product, row, col):
        """Create a product card: name + stock top, price below, centered qty controls."""
        from config import COLORS

        product_db_id, product_id, name, unit_price, quantity = product

        # Choose palette based on theme so it looks good in light and dark
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
        except Exception:
            is_dark = False

        if is_dark:
            card_bg = COLORS.get("surface_hover", "#111827")
            card_border = COLORS.get("border", "#374151")
            text_main = COLORS["text"]
            text_muted = COLORS["text_light"]
            qty_bg = COLORS.get("surface", "#020617")
            minus_bg = COLORS.get("surface", "#020617")
            minus_border = COLORS.get("border", "#374151")
        else:
            card_bg = "#f1f5f9"
            card_border = "#e2e8f0"
            text_main = "#1e293b"
            text_muted = "#64748b"
            qty_bg = "#ffffff"
            minus_bg = "#e2e8f0"
            minus_border = "#cbd5e1"

        card = ctk.CTkFrame(
            self.products_frame,
            fg_color=card_bg,
            corner_radius=14,
            border_width=1,
            border_color=card_border,
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        # Top row: name left, stock top-right
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(14, 6))
        display_name = name if len(name) <= 22 else name[:19] + "..."
        name_label = ctk.CTkLabel(
            top_row,
            text=display_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=text_main,
            anchor="w",
        )
        name_label.pack(side="left")
        stock_label = ctk.CTkLabel(
            top_row,
            text=f"Stock {quantity}",
            font=ctk.CTkFont(size=11),
            text_color=text_muted,
            anchor="e",
        )
        stock_label.pack(side="right")

        # Price: use project primary green
        price_label = ctk.CTkLabel(
            card,
            text=f"₹ {unit_price:.2f}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["primary"],
        )
        price_label.pack(pady=(0, 12))

        # Quantity controls: centered in the card
        qty_wrapper = ctk.CTkFrame(card, fg_color="transparent")
        qty_wrapper.pack(fill="x", pady=(0, 14))
        qty_frame = ctk.CTkFrame(qty_wrapper, fg_color="transparent")
        qty_frame.pack(anchor="center")

        minus_btn = ctk.CTkButton(
            qty_frame,
            text="−",
            width=32,
            height=32,
            command=lambda pid=product_db_id, pname=name, price=unit_price: self.decrease_quantity(pid, pname, price),
            fg_color=minus_bg,
            hover_color=COLORS.get("surface_hover", minus_bg),
            text_color=text_main,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            border_width=1,
            border_color=minus_border,
        )
        minus_btn.pack(side="left")

        qty_label = ctk.CTkLabel(
            qty_frame,
            text="0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=text_main,
            width=44,
            fg_color=qty_bg,
            corner_radius=8,
        )
        qty_label.pack(side="left", padx=6)

        plus_btn = ctk.CTkButton(
            qty_frame,
            text="+",
            width=32,
            height=32,
            command=lambda pid=product_db_id, pname=name, price=unit_price, qty=quantity: self.increase_quantity(pid, pname, price, qty),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
        )
        plus_btn.pack(side="left")

        card.qty_label = qty_label
        card.product_data = product
        # Keep reference so we can update quantity label when cart changes
        if hasattr(self, "product_card_map"):
            self.product_card_map[product_db_id] = card
    
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
        
        # Reflect new quantity on the card
        self._update_product_qty_label(product_db_id)
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
        
        self._update_product_qty_label(product_db_id)
        self.update_bill()

    def _get_cart_quantity(self, product_db_id):
        """Return current quantity of a product in the cart."""
        for item in self.cart:
            if item[0] == product_db_id:
                return item[2]
        return 0

    def _update_product_qty_label(self, product_db_id):
        """Sync the 0 / quantity label on the product card with cart."""
        card = getattr(self, "product_card_map", {}).get(product_db_id)
        if not card or not hasattr(card, "qty_label"):
            return
        qty = self._get_cart_quantity(product_db_id)
        card.qty_label.configure(text=str(qty))
    
    def update_bill(self):
        """Update bill display"""
        # Clear bill items
        for widget in self.bill_items_frame.winfo_children():
            widget.destroy()
        
        if not self.cart:
            # Reset all product card quantity labels to 0 when cart is empty
            for card in getattr(self, "product_card_map", {}).values():
                if hasattr(card, "qty_label"):
                    card.qty_label.configure(text="0")
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

        # Make this behave like a proper table: 6 uniform columns, shared between header and rows.
        headers = ["Item", "Qty", "Price", "Disc", "Total", "Actions"]
        for i in range(len(headers)):
            headers_frame.grid_columnconfigure(i, weight=1, uniform="bill_cols")

        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text'],
                anchor="center",
            )
            label.grid(row=0, column=i, padx=4, pady=5, sticky="nsew")
        
        # Bill items
        for item in self.cart:
            product_db_id, name, quantity, unit_price, total = item
            
            row_frame = ctk.CTkFrame(self.bill_items_frame, fg_color=COLORS['surface'], corner_radius=5)
            row_frame.pack(fill="x", pady=2)

            # Match the same 6 uniform columns as header
            for col in range(6):
                row_frame.grid_columnconfigure(col, weight=1, uniform="bill_cols")
            
            # Item name
            name_label = ctk.CTkLabel(
                row_frame,
                text=name[:20] + "..." if len(name) > 20 else name,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
                anchor="w",
            )
            name_label.grid(row=0, column=0, padx=6, pady=5, sticky="nsew")
            
            # Quantity
            qty_label = ctk.CTkLabel(
                row_frame,
                text=str(quantity),
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
            )
            qty_label.grid(row=0, column=1, padx=4, pady=5, sticky="nsew")
            
            # Price
            price_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {unit_price:.2f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
            )
            price_label.grid(row=0, column=2, padx=4, pady=5, sticky="nsew")
            
            # Per-line discount entry
            line_discount_val = self.line_discounts.get(product_db_id, 0.0)
            disc_entry = ctk.CTkEntry(
                row_frame,
                width=70,
                height=25,
                font=ctk.CTkFont(size=10)
            )
            disc_entry.insert(0, f"{line_discount_val:.2f}" if line_discount_val else "0")
            disc_entry.grid(row=0, column=3, padx=4, pady=5, sticky="nsew")

            def on_disc_change(event, pid=product_db_id, entry=disc_entry):
                try:
                    val = float(entry.get() or 0)
                except ValueError:
                    val = 0
                self.line_discounts[pid] = max(0.0, val)
                self.update_totals()

            disc_entry.bind("<KeyRelease>", on_disc_change)

            # Total
            total_label = ctk.CTkLabel(
                row_frame,
                text=f"₹ {total:.2f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text'],
            )
            total_label.grid(row=0, column=4, padx=4, pady=5, sticky="nsew")
            
            # Remove button
            remove_btn = ctk.CTkButton(
                row_frame,
                text="-",
                width=32,
                height=25,
                command=lambda pid=product_db_id: self.remove_from_cart(pid),
                fg_color=COLORS['error'],
                hover_color="#dc2626",
                font=ctk.CTkFont(size=12)
            )
            remove_btn.grid(row=0, column=5, padx=4, pady=5, sticky="nsew")
        
        # Update totals
        self.update_totals()
    
    def remove_from_cart(self, product_db_id):
        """Remove item from cart"""
        self.cart = [item for item in self.cart if item[0] != product_db_id]
        # Remove any per-line discount for this product
        if product_db_id in self.line_discounts:
            del self.line_discounts[product_db_id]
        self._update_product_qty_label(product_db_id)
        self.update_bill()
    
    def update_totals(self):
        """Update bill totals"""
        subtotal = sum(item[4] for item in self.cart)
        self.subtotal_label.configure(text=f"₹ {subtotal:.2f}")

        # Overall bill discount
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0.0

        # Per-line discounts (sum of rupee values)
        line_discount_total = sum(self.line_discounts.values()) if hasattr(self, "line_discounts") else 0.0

        # Tax / GST percentage
        try:
            gst_pct = float(self.tax_entry.get() or 0)
        except (ValueError, AttributeError):
            gst_pct = 0.0

        # Tax is applied on (subtotal - all discounts)
        taxable_base = max(0.0, subtotal - discount - line_discount_total)
        tax_amount = taxable_base * (gst_pct / 100.0)

        grand_total = max(0.0, taxable_base + tax_amount)
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
            # Include per-line discounts and GST
            line_discount_total = sum(self.line_discounts.values()) if hasattr(self, "line_discounts") else 0.0
            try:
                gst_pct = float(self.tax_entry.get() or 0)
            except (ValueError, AttributeError):
                gst_pct = 0.0
            taxable_base = max(0.0, subtotal - discount - line_discount_total)
            tax_amount = taxable_base * (gst_pct / 100.0)
            grand_total = max(0.0, taxable_base + tax_amount)

            # How much customer is paying right now
            amount_paid_str = self.amount_paid_entry.get().strip() if hasattr(self, "amount_paid_entry") else ""
            amount_paid = float(amount_paid_str or 0)

            if amount_paid < 0:
                messagebox.showerror("Error", "Amount paid cannot be negative")
                return
            # For walk-in customers we still don't track Khata/advance,
            # so they cannot pay more than the bill amount.
            if self.selected_customer_id is None and amount_paid > grand_total:
                messagebox.showerror("Error", "Amount paid cannot be more than the grand total for walk-in customers")
                return

            # For saved customers, if they pay MORE than the bill, ask whether to
            # store the extra as advance in Khata. If they choose "No", we only
            # consider the bill amount as paid and ignore the extra.
            if self.selected_customer_id is not None and amount_paid > grand_total:
                extra = amount_paid - grand_total
                add_advance = messagebox.askyesno(
                    "Add Extra as Advance?",
                    (
                        f"Bill amount is ₹ {grand_total:.2f}, but customer is paying ₹ {amount_paid:.2f}.\n\n"
                        f"Do you want to add the extra ₹ {extra:.2f} as advance in this customer's Khata?"
                    ),
                )
                if not add_advance:
                    # Use only the bill amount as the effective payment
                    amount_paid = grand_total
                    try:
                        # Reflect the adjusted amount back in the UI field
                        self.amount_paid_entry.delete(0, "end")
                        self.amount_paid_entry.insert(0, f"{grand_total:.2f}")
                    except Exception:
                        pass
            
            # Generate transaction ID
            transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"

            # Insert sale with optional customer_id
            sale_query = """INSERT INTO sales (transaction_id, total_amount, discount, final_amount,
                          tax_amount, payment_method, is_return, original_sale_id, customer_id) 
                          VALUES (?, ?, ?, ?, ?, ?, 0, NULL, ?)"""
            sale_params = (
                transaction_id,
                subtotal,
                discount,
                grand_total,
                tax_amount,
                self.payment_method_combo.get() if hasattr(self, "payment_method_combo") else None,
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
                line_discount_val = self.line_discounts.get(product_db_id, 0.0) if hasattr(self, "line_discounts") else 0.0
                item_query = """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price, line_discount) 
                              VALUES (?, ?, ?, ?, ?, ?)"""
                item_params = (sale_id, product_db_id, quantity, unit_price, total, line_discount_val)
                
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

            # If a customer is selected, update their Khata/advance and record payment history.
            # We treat due_amount as a running balance:
            #   positive  -> customer owes the shop (Khata due)
            #   negative  -> customer has advance/credit with the shop
            if self.selected_customer_id is not None and grand_total > 0:
                # Fetch current balance
                row = self.db.fetch_one(
                    "SELECT due_amount FROM customers WHERE id = ?",
                    (self.selected_customer_id,),
                )
                current_balance = row[0] if row else 0.0

                # 1) If they are paying LESS than the bill, ask whether to push the remaining
                #    amount into Khata for this customer.
                if amount_paid < grand_total:
                    remaining = grand_total - amount_paid
                    add_to_khata = messagebox.askyesno(
                        "Add Remaining to Khata?",
                        (
                            f"Bill amount is ₹ {grand_total:.2f}, but customer is paying ₹ {amount_paid:.2f}.\n\n"
                            f"Do you want to add the remaining ₹ {remaining:.2f} to this customer's Khata?"
                        ),
                    )
                    if not add_to_khata:
                        messagebox.showinfo(
                            "Payment Cancelled",
                            "Please adjust the amount paid or confirm adding the remaining amount to Khata.",
                        )
                        return

                # 2) If they already have an ADVANCE (negative balance), ask whether to use it.
                use_advance = True
                if current_balance < 0:
                    use_advance = messagebox.askyesno(
                        "Use Advance Balance?",
                        (
                            f"This customer has an advance balance of ₹ {abs(current_balance):.2f}.\n\n"
                            "Do you want to use their advance towards this bill?\n"
                            "Choose 'No' to let them pay the full amount and keep the Khata balance unchanged."
                        ),
                    )
                    # If they do NOT want to use advance, the bill must be fully paid now
                    # so that the Khata balance can remain exactly the same.
                    if not use_advance and abs(amount_paid - grand_total) > 0.0001:
                        messagebox.showerror(
                            "Invalid Amount",
                            "When not using the advance, the customer must pay the full bill amount.",
                        )
                        return

                # Compute new balance based on the user's choices.
                if use_advance:
                    # Normal behavior: bill and payment both affect the running balance.
                    # balance_new = old_balance + bill_amount - amount_paid_now
                    new_balance = current_balance + grand_total - amount_paid
                else:
                    # Do not touch existing Khata/advance balance; enforce full payment above.
                    new_balance = current_balance

                # Record any payment made so it appears in history
                if amount_paid > 0:
                    payment_query = "INSERT INTO payments (customer_id, amount) VALUES (?, ?)"
                    if not self.db.execute_query(payment_query, (self.selected_customer_id, amount_paid)):
                        messagebox.showerror("Error", "Failed to record customer payment")
                        return

                # Update customer's running Khata balance and last_payment_date when needed
                update_due_query = """
                    UPDATE customers
                    SET due_amount = ?,
                        last_payment_date = CASE WHEN ? > 0 THEN date('now') ELSE last_payment_date END
                    WHERE id = ?
                """
                if not self.db.execute_query(update_due_query, (new_balance, amount_paid, self.selected_customer_id)):
                    messagebox.showerror("Error", "Failed to update customer Khata")
                    return
            
            messagebox.showinfo("Success", f"Transaction saved successfully!\nTransaction ID: {transaction_id}")

            # Ask whether to print the bill (use snapshot before clearing cart)
            bill_data = {
                "transaction_id": transaction_id,
                "items": [list(item) for item in self.cart],
                "subtotal": subtotal,
                "discount": discount,
            "line_discount_total": line_discount_total,
            "tax_amount": tax_amount,
            "grand_total": grand_total,
                "customer": self.customer_combo.get() if self.customer_combo else "Walk-in / Cash",
                "amount_paid": amount_paid,
            "payment_method": self.payment_method_combo.get() if hasattr(self, "payment_method_combo") else "Cash",
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            }
            if messagebox.askyesno("Print Bill", "Do you want to print the bill?"):
                self._open_bill_for_print(bill_data)
            
            # Clear cart
            self.cart = []
            self.discount_entry.delete(0, "end")
            if hasattr(self, "amount_paid_entry"):
                self.amount_paid_entry.delete(0, "end")
            self.update_bill()
            self.load_products()

            # Refresh the displayed Khata/advance balance for the selected customer
            if self.selected_customer_id is not None and hasattr(self, "customer_combo") and self.customer_combo is not None:
                try:
                    current_display = self.customer_combo.get()
                    self.on_customer_selected(current_display)
                except Exception:
                    pass
            
            # Refresh dashboard and other pages if callback is available
            if self.on_data_change:
                self.on_data_change()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def _open_bill_for_print(self, bill_data):
        """Generate HTML bill and open in browser so user can print (Ctrl+P)."""
        html = self._bill_to_html(bill_data)
        fd, path = tempfile.mkstemp(suffix=".html", prefix="vyapaar_bill_")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open("file://" + path)
        except Exception as e:
            messagebox.showerror("Print", f"Could not open bill: {e}")

    def _bill_to_html(self, bill_data):
        """Build a simple printable HTML bill."""
        lines = []
        total_amt = 0.0
        for item in bill_data["items"]:
            name, qty, price, total = item[1], item[2], item[3], item[4]
            total_amt += total
            lines.append(f"<tr><td>{name}</td><td>{qty}</td><td>₹ {price:.2f}</td><td>₹ {total:.2f}</td></tr>")
        rows = "\n".join(lines)
        sub = bill_data["subtotal"]
        disc = bill_data["discount"]
        line_disc = bill_data.get("line_discount_total", 0.0)
        tax_amt = bill_data.get("tax_amount", 0.0)
        grand = bill_data["grand_total"]
        paid = bill_data["amount_paid"]
        cust = bill_data["customer"]
        txn = bill_data["transaction_id"]
        date = bill_data["date"]
        pay_method = bill_data.get("payment_method", "Cash")
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Bill - {txn}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 400px; margin: 24px auto; padding: 16px; }}
h1 {{ font-size: 1.25rem; margin-bottom: 4px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
th, td {{ padding: 6px 8px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
th {{ font-weight: 600; }}
.totals {{ margin-top: 12px; }}
.grand {{ font-size: 1.1rem; font-weight: 700; }}
@media print {{ body {{ margin: 12px; }} }}
</style></head><body>
<h1>VyapaarSetGo - Bill</h1>
<p style="color:#6b7280;font-size:0.9rem;">{date}<br>Transaction: {txn}<br>Customer: {cust}<br>Payment: {pay_method}</p>
<table>
<thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<div class="totals">
<p>Subtotal: ₹ {sub:.2f}</p>
<p>Bill Discount: ₹ {disc:.2f}</p>
<p>Per-item Discounts: ₹ {line_disc:.2f}</p>
<p>GST / Tax: ₹ {tax_amt:.2f}</p>
<p class="grand">Grand Total: ₹ {grand:.2f}</p>
<p>Amount Paid: ₹ {paid:.2f}</p>
</div>
<p style="margin-top:20px;font-size:0.85rem;color:#6b7280;">Thank you!</p>
</body></html>"""

    def print_bill(self):
        """Open current bill in browser for printing (or prompt to save first)."""
        if not self.cart:
            messagebox.showwarning("Print Bill", "Cart is empty. Save a transaction first, then choose to print when prompted.")
            return
        subtotal = sum(item[4] for item in self.cart)
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        line_discount_total = sum(self.line_discounts.values()) if hasattr(self, "line_discounts") else 0.0
        try:
            gst_pct = float(self.tax_entry.get() or 0)
        except (ValueError, AttributeError):
            gst_pct = 0.0
        taxable_base = max(0.0, subtotal - discount - line_discount_total)
        tax_amount = taxable_base * (gst_pct / 100.0)
        grand_total = max(0.0, taxable_base + tax_amount)
        customer = self.customer_combo.get() if self.customer_combo else "Walk-in / Cash"
        try:
            amount_paid = float(self.amount_paid_entry.get() or 0)
        except ValueError:
            amount_paid = 0
        bill_data = {
            "transaction_id": "DRAFT",
            "items": [list(item) for item in self.cart],
            "subtotal": subtotal,
            "discount": discount,
            "line_discount_total": line_discount_total,
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "customer": customer,
            "amount_paid": amount_paid,
            "payment_method": self.payment_method_combo.get() if hasattr(self, "payment_method_combo") else "Cash",
            "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        }
        self._open_bill_for_print(bill_data)

