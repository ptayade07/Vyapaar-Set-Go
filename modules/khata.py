"""
Customer Khata (Credit Book) module
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime
from modules.suppliers import PaymentDialog


class Khata(ctk.CTkFrame):
    """Customer Khata (Credit Book) module"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.selected_customer = None
        self.setup_ui()
        self.load_customers()
    
    def setup_ui(self):
        """Setup khata UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Customer Khata",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        # Total balances banner (two separate cards)
        total_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        total_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        total_content = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_content.pack(fill="x", pady=0)

        # Decide card colors based on theme (lighter in light mode, stronger in dark)
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
        except Exception:
            is_dark = False

        if is_dark:
            due_bg = COLORS["primary"]
            due_title_color = "white"
            adv_bg = "#14532d"
            adv_border = COLORS["primary"]
        else:
            due_bg = "#bbf7d0"  # soft green
            due_title_color = "#166534"
            adv_bg = "#ecfdf3"
            adv_border = "#bbf7d0"

        # Left: Total Due Balance
        due_container = ctk.CTkFrame(
            total_content,
            fg_color=due_bg,
            corner_radius=16
        )
        due_container.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=0)

        due_inner = ctk.CTkFrame(due_container, fg_color="transparent")
        due_inner.pack(fill="both", expand=True, padx=20, pady=16)

        due_title = ctk.CTkLabel(
            due_inner,
            text="Total Due Balance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=due_title_color,
        )
        due_title.pack(anchor="w")

        self.total_due_label = ctk.CTkLabel(
            due_inner,
            text="₹ 0.00",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=due_title_color,
        )
        self.total_due_label.pack(anchor="w", pady=(4, 2))

        due_sub = ctk.CTkLabel(
            due_inner,
            text="Customers owing you",
            font=ctk.CTkFont(size=12),
            text_color=due_title_color,
        )
        due_sub.pack(anchor="w")

        # Right: Total Advance Balance (softer card)
        adv_container = ctk.CTkFrame(
            total_content,
            fg_color=adv_bg,
            corner_radius=16,
            border_width=2,
            border_color=adv_border,
        )
        adv_container.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=0)

        adv_inner = ctk.CTkFrame(adv_container, fg_color="transparent")
        adv_inner.pack(fill="both", expand=True, padx=20, pady=16)

        adv_title = ctk.CTkLabel(
            adv_inner,
            text="Total Advance Balance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary'],
        )
        adv_title.pack(anchor="w")

        self.total_advance_label = ctk.CTkLabel(
            adv_inner,
            text="₹ 0.00",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORS['primary'],
        )
        self.total_advance_label.pack(anchor="w", pady=(4, 2))

        adv_sub = ctk.CTkLabel(
            adv_inner,
            text="Customer advance with you",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'],
        )
        adv_sub.pack(anchor="w")
        
        # Search and actions
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Search bar
        search_frame = ctk.CTkFrame(actions_frame, fg_color=COLORS['surface'], corner_radius=8)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search customers by name or phone...",
            height=40,
            font=ctk.CTkFont(size=12),
            border_width=0
        )
        search_entry.pack(fill="x", expand=True, padx=15, pady=10)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_customers(search_entry.get()))
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        add_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Add New Customer",
            command=self.show_add_customer_dialog,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        add_btn.pack(side="left", padx=5)
        
        payment_btn = ctk.CTkButton(
            buttons_frame,
            text="💰 Update Payment",
            command=self.show_payment_dialog,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        payment_btn.pack(side="left", padx=5)
        
        history_btn = ctk.CTkButton(
            buttons_frame,
            text="🕐 View Payment History",
            command=self.show_payment_history,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        history_btn.pack(side="left", padx=5)
        
        # Customers table
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        table_label = ctk.CTkLabel(
            table_frame,
            text="Customer List",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        table_label.pack(pady=15)
        
        # Scrollable table
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
        
        headers = ["Name", "Phone", "Due Amount", "Last Payment Date", "Actions"]
        widths = [200, 150, 150, 150, 150]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text'],
                width=width
            )
            label.grid(row=0, column=i, padx=15, pady=14, sticky="w")
        
        # Customers list
        self.customers_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        self.customers_frame.pack(fill="x")
        
        # Pagination
        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.pack(pady=15)
        
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Showing 1-5 of 5 customers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        self.page_label.pack()
    
    def load_customers(self, search_term=""):
        """Load customers from database"""
        for widget in self.customers_frame.winfo_children():
            widget.destroy()
        
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY name"
        
        customers = self.db.fetch_all(query, tuple(params) if params else None)
        
        # Update total due and advance balances
        total_due = sum(c[3] for c in customers if c[3] > 0)
        total_advance = sum(-c[3] for c in customers if c[3] < 0)
        self.total_due_label.configure(text=f"₹ {total_due:.2f}")
        self.total_advance_label.configure(text=f"₹ {total_advance:.2f}")
        
        # Display customers
        for idx, customer in enumerate(customers):
            self.create_customer_row(customer, idx % 2 == 0)
        
        # Update pagination
        count = len(customers)
        self.page_label.configure(text=f"Showing 1-{count} of {count} customers")
    
    def create_customer_row(self, customer, even_row=False):
        """Create a customer row"""
        row_bg = COLORS.get('surface_hover', COLORS['surface']) if even_row else COLORS['background']
        row_frame = ctk.CTkFrame(
            self.customers_frame,
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
        
        customer_id, name, phone, due_amount, last_payment = customer[0], customer[1], customer[2], customer[3], customer[4]
        
        # Name
        name_label = ctk.CTkLabel(
            row_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=200
        )
        name_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        # Phone
        phone_label = ctk.CTkLabel(
            row_frame,
            text=phone,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=150
        )
        phone_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
        
        # Due Amount (show negative amounts in red, positive in green)
        due_color = COLORS['error'] if due_amount > 0 else (COLORS['success'] if due_amount < 0 else COLORS['text'])
        due_label = ctk.CTkLabel(
            row_frame,
            text=f"₹ {due_amount:.2f}",
            font=ctk.CTkFont(size=12, weight="bold" if due_amount != 0 else "normal"),
            text_color=due_color,
            width=150
        )
        due_label.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        
        # Last Payment Date (can be stored as string or datetime in DB)
        if last_payment:
            try:
                # If it's already a datetime/date, format nicely
                last_payment_str = last_payment.strftime("%d %b %Y")
            except AttributeError:
                # Otherwise try to parse common string formats
                try:
                    parsed = datetime.strptime(str(last_payment)[:10], "%Y-%m-%d")
                    last_payment_str = parsed.strftime("%d %b %Y")
                except Exception:
                    last_payment_str = str(last_payment)
        else:
            last_payment_str = "N/A"
        payment_label = ctk.CTkLabel(
            row_frame,
            text=last_payment_str,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'] if last_payment_str == "N/A" else COLORS['text'],
            width=150
        )
        payment_label.grid(row=0, column=3, padx=15, pady=12, sticky="w")

        # Optional credit limit (last column, shown below actions if set)
        credit_limit = 0.0
        if len(customer) > 9 and customer[9] is not None:
            try:
                credit_limit = float(customer[9])
            except (TypeError, ValueError):
                credit_limit = 0.0
        
        # Actions: View Ledger, Add Payment, Edit, Delete
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=15, pady=12)

        btn_font = ctk.CTkFont(size=11)

        ledger_btn = ctk.CTkButton(
            actions_frame,
            text="Ledger",
            width=60,
            height=28,
            command=lambda cid=customer_id: self.view_ledger(cid),
            fg_color=COLORS['surface'],
            hover_color=COLORS.get('surface_hover', COLORS['surface']),
            text_color=COLORS['text'],
            border_width=1,
            border_color=COLORS.get('border', COLORS['secondary']),
            font=btn_font,
            corner_radius=6,
        )
        ledger_btn.pack(side="left", padx=2)

        pay_btn = ctk.CTkButton(
            actions_frame,
            text="Pay",
            width=50,
            height=28,
            command=lambda cid=customer_id: self.add_payment(cid),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color="white",
            font=btn_font,
            corner_radius=6,
        )
        pay_btn.pack(side="left", padx=2)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=50,
            height=28,
            command=lambda cid=customer_id: self.select_customer(cid, "edit"),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            text_color="white",
            font=btn_font,
            corner_radius=6,
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=60,
            height=28,
            command=lambda cid=customer_id: self.delete_customer(cid),
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            text_color="white",
            font=btn_font,
            corner_radius=6,
        )
        delete_btn.pack(side="left", padx=2)
        row_frame.customer_data = customer

        # Show credit limit text under the buttons if a limit is set
        if credit_limit > 0:
            limit_label = ctk.CTkLabel(
                row_frame,
                text=f"Limit: ₹ {credit_limit:.2f}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
            )
            limit_label.grid(row=1, column=4, padx=15, pady=(0, 8), sticky="w")

        def on_row_click(_event=None, cid=customer_id):
            self.selected_customer = customer
            # Highlight selection
            for child in self.customers_frame.winfo_children():
                if hasattr(child, 'is_even'):
                    child.configure(fg_color=COLORS['surface'] if child.is_even else COLORS['background'])
            row_frame.configure(fg_color="#e5f7ec")

        row_frame.is_even = even_row

        for widget in (row_frame, name_label, phone_label, due_label, payment_label):
            widget.bind("<Button-1>", on_row_click)
            widget.configure(cursor="hand2")
    
    def select_customer(self, customer_id, action="edit"):
        """Select a customer"""
        query = "SELECT * FROM customers WHERE id = ?"
        customer = self.db.fetch_one(query, (customer_id,))
        if customer:
            self.selected_customer = customer
            if action == "edit":
                self.show_edit_customer_dialog()
    
    def view_ledger(self, customer_id):
        """Open payment history (ledger) for a specific customer"""
        customer = self.db.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
        if customer:
            dialog = PaymentHistoryDialog(self, self.db, customer)
            self.wait_window(dialog)

    def add_payment(self, customer_id):
        """Open add payment dialog for a specific customer"""
        customer = self.db.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
        if customer:
            dialog = PaymentDialog(self, self.db, customer, "customer")
            self.wait_window(dialog)
            self.load_customers()
    
    def filter_customers(self, search_term):
        """Filter customers by search term"""
        self.load_customers(search_term=search_term)
    
    def show_add_customer_dialog(self):
        """Show add customer dialog"""
        dialog = CustomerDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_customers()
    
    def show_edit_customer_dialog(self):
        """Show edit customer dialog"""
        if not self.selected_customer:
            messagebox.showwarning("No Selection", "Please select a customer to edit")
            return
        
        dialog = CustomerDialog(self, self.db, self.selected_customer)
        self.wait_window(dialog)
        self.selected_customer = None
        self.load_customers()
    
    def show_payment_dialog(self):
        """Show payment dialog"""
        dialog = CustomerSelectDialog(self, self.db, mode="payment")
        self.wait_window(dialog)
        selected = getattr(dialog, "selected_customer", None)
        if selected:
            pay_dialog = PaymentDialog(self, self.db, selected, "customer")
            self.wait_window(pay_dialog)
            self.load_customers()
    
    def show_payment_history(self):
        """Show payment history"""
        dialog = CustomerSelectDialog(self, self.db, mode="history")
        self.wait_window(dialog)
        selected = getattr(dialog, "selected_customer", None)
        if selected:
            hist_dialog = PaymentHistoryDialog(self, self.db, selected)
            self.wait_window(hist_dialog)
    
    def delete_customer(self, customer_id):
        """Delete customer"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
            if self.db.execute_query("DELETE FROM customers WHERE id = ?", (customer_id,)):
                messagebox.showinfo("Success", "Customer deleted successfully")
                self.load_customers()
            else:
                messagebox.showerror("Error", "Failed to delete customer")


class CustomerDialog(ctk.CTkToplevel):
    """Customer add/edit dialog"""
    
    def __init__(self, parent, db, customer_data=None):
        super().__init__(parent)
        self.db = db
        self.customer_data = customer_data
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup dialog UI"""
        title = "Edit Customer" if self.customer_data else "Add Customer"
        self.title(title)
        self.geometry("420x420")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog on screen
        self.update_idletasks()
        width = 420
        height = 420
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)
        
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 20))

        # Scrollable area for form fields
        form_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, pady=(0, 15))
        
        # Form fields
        fields = [
            ("Customer Name", "name", "Customer Name"),
            ("Phone Number", "phone", "9876543210"),
            ("Address", "address", "Street, Area, City"),
            ("Opening Balance (₹)", "opening_balance", "0.00"),
            ("Credit Limit (₹)", "credit_limit", "0.00"),
        ]
        
        self.entries = {}
        
        for label, key, placeholder in fields:
            frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
            frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text'],
                anchor="w"
            ).pack(fill="x", pady=(0, 3))
            
            entry = ctk.CTkEntry(
                frame,
                placeholder_text=placeholder,
                height=38,
                font=ctk.CTkFont(size=12)
            )
            entry.pack(fill="x")
            self.entries[key] = entry

        # Notes as multiline field
        notes_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        notes_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            notes_frame,
            text="Notes",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(fill="x", pady=(0, 3))

        self.notes_text = ctk.CTkTextbox(
            notes_frame,
            height=60,
            font=ctk.CTkFont(size=12)
        )
        self.notes_text.pack(fill="x")
        
        # Pre-fill if editing
        if self.customer_data:
            self.entries["name"].insert(0, self.customer_data[1])
            self.entries["phone"].insert(0, self.customer_data[2])
            # address (index 7) and notes (index 8) if present
            if len(self.customer_data) > 7:
                self.entries["address"].insert(0, self.customer_data[7] or "")
            if len(self.customer_data) > 8 and self.customer_data[8]:
                self.notes_text.insert("1.0", self.customer_data[8])
            # opening balance from current due_amount (index 3)
            self.entries["opening_balance"].insert(0, str(self.customer_data[3] or 0))
            # credit limit (index 9 if present)
            if len(self.customer_data) > 9:
                self.entries["credit_limit"].insert(0, str(self.customer_data[9] or 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save_customer,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=15)
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)
    
    def save_customer(self):
        """Save customer to database"""
        try:
            name = self.entries["name"].get().strip()
            phone = self.entries["phone"].get().strip()
            address = self.entries["address"].get().strip()
            opening_raw = self.entries["opening_balance"].get().strip()
            credit_raw = self.entries["credit_limit"].get().strip()
            notes = self.notes_text.get("1.0", "end").strip()

            try:
                opening_balance = float(opening_raw or 0)
            except ValueError:
                opening_balance = 0.0
            try:
                credit_limit = float(credit_raw or 0)
            except ValueError:
                credit_limit = 0.0
            
            if not name or not phone:
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            if self.customer_data:
                query = "UPDATE customers SET name=?, phone=?, due_amount=?, address=?, notes=?, credit_limit=? WHERE id=?"
                params = (name, phone, opening_balance, address, notes, credit_limit, self.customer_data[0])
            else:
                query = "INSERT INTO customers (name, phone, due_amount, address, notes, credit_limit) VALUES (?, ?, ?, ?, ?, ?)"
                params = (name, phone, opening_balance, address, notes, credit_limit)
            
            if self.db.execute_query(query, params):
                messagebox.showinfo("Success", "Customer saved successfully")
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save customer")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class PaymentHistoryDialog(ctk.CTkToplevel):
    """Payment history dialog"""
    
    def __init__(self, parent, db, customer_data):
        super().__init__(parent)
        self.db = db
        self.customer_data = customer_data
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup customer ledger dialog (sales + payments)"""
        customer_name = self.customer_data[1]
        self.title(f"Customer Ledger - {customer_name}")
        self.geometry("600x400")
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            container,
            text=f"Customer Ledger - {customer_name}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Table
        table_frame = ctk.CTkFrame(container, fg_color=COLORS['background'], corner_radius=10)
        table_frame.pack(fill="both", expand=True)
        
        # Headers
        headers_frame = ctk.CTkFrame(table_frame, fg_color=COLORS['surface'], corner_radius=5)
        headers_frame.pack(fill="x", padx=10, pady=10)
        
        headers = ["Date", "Type", "Amount"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text'],
                width=200
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Ledger list
        scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load sales and payments into a unified ledger
        ledger_query = """
            SELECT sale_date AS dt, 'Sale' AS kind, final_amount AS amount
            FROM sales
            WHERE customer_id = ?
          UNION ALL
            SELECT payment_date AS dt, 'Payment' AS kind, amount AS amount
            FROM payments
            WHERE customer_id = ?
          ORDER BY dt DESC
        """
        rows = self.db.fetch_all(ledger_query, (self.customer_data[0], self.customer_data[0]))
        
        if not rows:
            no_data_label = ctk.CTkLabel(
                scroll_frame,
                text="No transactions found for this customer",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data_label.pack(pady=20)
        else:
            for dt, kind, amount in rows:
                row_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS['surface'], corner_radius=5)
                row_frame.pack(fill="x", pady=2, padx=5)

                # dt can be stored as a datetime object or as a plain string in SQLite
                try:
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                except AttributeError:
                    # If it's already a string like "YYYY-MM-DD HH:MM:SS", just show it
                    date_str = str(dt)

                date_label = ctk.CTkLabel(
                    row_frame,
                    text=date_str,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=200
                )
                date_label.pack(side="left", padx=10, pady=8)

                type_label = ctk.CTkLabel(
                    row_frame,
                    text=kind,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=120
                )
                type_label.pack(side="left", padx=10, pady=8)

                amount_label = ctk.CTkLabel(
                    row_frame,
                    text=f"₹ {float(amount):.2f}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=160
                )
                amount_label.pack(side="left", padx=10, pady=8)
        
        # Close button
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        close_btn.pack(pady=10)


class CustomerSelectDialog(ctk.CTkToplevel):
    """Dialog to search & select a customer (used for payment / history)"""

    def __init__(self, parent, db, mode="payment"):
        super().__init__(parent)
        self.db = db
        self.mode = mode
        self.selected_customer = None
        self.setup_dialog()

    def setup_dialog(self):
        title = "Select Customer for Payment" if self.mode == "payment" else "Select Customer for Ledger"
        self.title(title)
        self.geometry("520x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 10))

        search_entry = ctk.CTkEntry(
            container,
            placeholder_text="Search customers by name or phone...",
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
            query = "SELECT id, name, phone, due_amount FROM customers WHERE 1=1"
            params = []
            if term:
                query += " AND (name LIKE ? OR phone LIKE ?)"
                like = f"%{term}%"
                params.extend([like, like])
            query += " ORDER BY name"
            customers = self.db.fetch_all(query, tuple(params) if params else None)

            for c in customers:
                row = ctk.CTkFrame(self.rows_frame, fg_color=COLORS['surface'], corner_radius=6)
                row.pack(fill="x", pady=3, padx=4)
                due = c[3]
                text = f"{c[1]} ({c[2]})  •  Balance: ₹ {due:.2f}"
                lbl = ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text'],
                    anchor="w",
                )
                lbl.pack(fill="x", padx=10, pady=6)

                def on_click(_e=None, cid=c[0]):
                    cust = self.db.fetch_one("SELECT * FROM customers WHERE id = ?", (cid,))
                    if cust:
                        self.selected_customer = cust
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

