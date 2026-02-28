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
        
        # Total outstanding balance banner
        total_frame = ctk.CTkFrame(self, fg_color=COLORS['primary'], corner_radius=12)
        total_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        total_content = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_content.pack(fill="x", padx=30, pady=25)
        
        total_label = ctk.CTkLabel(
            total_content,
            text="Total Outstanding Balance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        total_label.pack(anchor="w", pady=(0, 8))
        
        self.total_amount_label = ctk.CTkLabel(
            total_content,
            text="₹ 0.00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        self.total_amount_label.pack(anchor="w", pady=(0, 5))
        
        due_label = ctk.CTkLabel(
            total_content,
            text="due across all customers",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        due_label.pack(anchor="w")
        
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
        
        # Update total outstanding
        total = sum(c[3] for c in customers)
        self.total_amount_label.configure(text=f"₹ {total:.2f}")
        
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
                # If it's already a datetime/date, strftime will work
                last_payment_str = last_payment.strftime("%Y-%m-%d")
            except AttributeError:
                # Otherwise assume it's a string like "YYYY-MM-DD" and show as-is
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
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=15, pady=12)
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=40,
            height=30,
            command=lambda cid=customer_id: self.select_customer(cid, "edit"),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            font=ctk.CTkFont(size=14)
        )
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=40,
            height=30,
            command=lambda cid=customer_id: self.delete_customer(cid),
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            font=ctk.CTkFont(size=14)
        )
        delete_btn.pack(side="left", padx=2)
        row_frame.customer_data = customer

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
        if not self.selected_customer:
            messagebox.showwarning("No Selection", "Please select a customer")
            return
        
        dialog = PaymentDialog(self, self.db, self.selected_customer, "customer")
        self.wait_window(dialog)
        self.selected_customer = None
        self.load_customers()
    
    def show_payment_history(self):
        """Show payment history"""
        if not self.selected_customer:
            messagebox.showwarning("No Selection", "Please select a customer")
            return
        
        dialog = PaymentHistoryDialog(self, self.db, self.selected_customer)
        self.wait_window(dialog)
    
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
        self.geometry("380x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog on screen
        self.update_idletasks()
        width = 380
        height = 320
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
        
        # Form fields
        fields = [
            ("Name", "name", "Customer Name"),
            ("Phone", "phone", "9876543210"),
        ]
        
        self.entries = {}
        
        for label, key, placeholder in fields:
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", pady=10)
            
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
        
        # Pre-fill if editing
        if self.customer_data:
            self.entries["name"].insert(0, self.customer_data[1])
            self.entries["phone"].insert(0, self.customer_data[2])
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save_customer,
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
    
    def save_customer(self):
        """Save customer to database"""
        try:
            name = self.entries["name"].get().strip()
            phone = self.entries["phone"].get().strip()
            
            if not name or not phone:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if self.customer_data:
                query = "UPDATE customers SET name=?, phone=? WHERE id=?"
                params = (name, phone, self.customer_data[0])
            else:
                query = "INSERT INTO customers (name, phone) VALUES (?, ?)"
                params = (name, phone)
            
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
        """Setup payment history dialog"""
        customer_name = self.customer_data[1]
        self.title(f"Payment History - {customer_name}")
        self.geometry("600x400")
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            container,
            text=f"Payment History - {customer_name}",
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
        
        headers = ["Date", "Amount"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text'],
                width=250
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Payments list
        scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load payments
        query = "SELECT payment_date, amount FROM payments WHERE customer_id = ? ORDER BY payment_date DESC"
        payments = self.db.fetch_all(query, (self.customer_data[0],))
        
        if not payments:
            no_data_label = ctk.CTkLabel(
                scroll_frame,
                text="No payment history found",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light']
            )
            no_data_label.pack(pady=20)
        else:
            for payment in payments:
                row_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS['surface'], corner_radius=5)
                row_frame.pack(fill="x", pady=2, padx=5)

                # payment_date can be stored as a datetime object or as a plain string in SQLite
                payment_date = payment[0]
                try:
                    date_str = payment_date.strftime("%Y-%m-%d %H:%M")
                except AttributeError:
                    # If it's already a string like "YYYY-MM-DD HH:MM:SS", just show it
                    date_str = str(payment_date)

                date_label = ctk.CTkLabel(
                    row_frame,
                    text=date_str,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=250
                )
                date_label.pack(side="left", padx=10, pady=8)

                amount_label = ctk.CTkLabel(
                    row_frame,
                    text=f"₹ {payment[1]:.2f}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=250
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

