"""
Supplier Management module
"""
import customtkinter as ctk
from tkinter import messagebox
from database import Database
from config import COLORS, DB_PATH
from datetime import datetime


class Suppliers(ctk.CTkFrame):
    """Supplier Management module"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent, fg_color=COLORS['background'])
        self.db = db if db else Database(DB_PATH)
        if not db:
            self.db.connect()  # Ensure connection is established
        self.selected_supplier = None
        self.setup_ui()
        self.load_suppliers()
    
    def setup_ui(self):
        """Setup suppliers UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Supplier Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(side="left")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        add_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Add Supplier",
            command=self.show_add_supplier_dialog,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit Supplier",
            command=self.show_edit_supplier_dialog,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        edit_btn.pack(side="left", padx=5)
        
        payment_btn = ctk.CTkButton(
            actions_frame,
            text="💰 Mark Payment",
            command=self.show_payment_dialog,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        payment_btn.pack(side="left", padx=5)
        
        # Suppliers table
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        table_label = ctk.CTkLabel(
            table_frame,
            text="Supplier List",
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
        
        headers = ["Supplier Name", "Contact", "Last Purchase", "Pending Payment", "Actions"]
        widths = [200, 150, 150, 150, 120]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text'],
                width=width
            )
            label.grid(row=0, column=i, padx=15, pady=14, sticky="w")
        
        # Suppliers list
        self.suppliers_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        self.suppliers_frame.pack(fill="x")
        
        # Pagination
        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.pack(pady=15)
        
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Showing 1-5 of 5 suppliers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        self.page_label.pack()
    
    def load_suppliers(self):
        """Load suppliers from database"""
        for widget in self.suppliers_frame.winfo_children():
            widget.destroy()
        
        query = "SELECT * FROM suppliers ORDER BY name"
        suppliers = self.db.fetch_all(query)
        
        for idx, supplier in enumerate(suppliers):
            self.create_supplier_row(supplier, idx % 2 == 0)
        
        # Update pagination
        count = len(suppliers)
        self.page_label.configure(text=f"Showing 1-{count} of {count} suppliers")
    
    def create_supplier_row(self, supplier, even_row=False):
        """Create a supplier row"""
        row_bg = COLORS.get('surface_hover', COLORS['surface']) if even_row else COLORS['background']
        row_frame = ctk.CTkFrame(
            self.suppliers_frame,
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
        
        supplier_id, name, contact, last_purchase, pending_payment = supplier[0], supplier[1], supplier[2], supplier[3], supplier[4]
        
        # Name
        name_label = ctk.CTkLabel(
            row_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=200
        )
        name_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        # Contact
        contact_label = ctk.CTkLabel(
            row_frame,
            text=contact,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            width=150
        )
        contact_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
        
        # Last Purchase
        if last_purchase:
            try:
                last_purchase_str = last_purchase.strftime("%Y-%m-%d")
            except AttributeError:
                last_purchase_str = str(last_purchase)
        else:
            last_purchase_str = "N/A"
        purchase_label = ctk.CTkLabel(
            row_frame,
            text=last_purchase_str,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light'] if last_purchase_str == "N/A" else COLORS['text'],
            width=150
        )
        purchase_label.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        
        # Pending Payment (negative means we owe them, positive means they owe us)
        payment_color = COLORS['error'] if pending_payment > 0 else (COLORS['success'] if pending_payment < 0 else COLORS['text'])
        payment_label = ctk.CTkLabel(
            row_frame,
            text=f"₹ {pending_payment:.2f}",
            font=ctk.CTkFont(size=12, weight="bold" if pending_payment != 0 else "normal"),
            text_color=payment_color,
            width=150
        )
        payment_label.grid(row=0, column=3, padx=15, pady=12, sticky="w")
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=15, pady=12)
        
        select_btn = ctk.CTkButton(
            actions_frame,
            text="Select",
            width=80,
            height=30,
            command=lambda sid=supplier_id: self.select_supplier(sid),
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            font=ctk.CTkFont(size=11)
        )
        select_btn.pack()
        row_frame.supplier_data = supplier

        def on_row_click(_event=None, sid=supplier_id):
            # Use existing selection logic
            self.select_supplier(sid)
            # Highlight selection across table
            for child in self.suppliers_frame.winfo_children():
                if hasattr(child, 'is_even'):
                    child.configure(fg_color=COLORS['surface'] if child.is_even else COLORS['background'])
            row_frame.configure(fg_color="#e5f7ec")

        row_frame.is_even = even_row

        for widget in (row_frame, name_label, contact_label, purchase_label, payment_label):
            widget.bind("<Button-1>", on_row_click)
            widget.configure(cursor="hand2")
    
    def select_supplier(self, supplier_id):
        """Select a supplier"""
        query = "SELECT * FROM suppliers WHERE id = ?"
        supplier = self.db.fetch_one(query, (supplier_id,))
        if supplier:
            self.selected_supplier = supplier
    
    def show_add_supplier_dialog(self):
        """Show add supplier dialog"""
        dialog = SupplierDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_suppliers()
    
    def show_edit_supplier_dialog(self):
        """Show edit supplier dialog"""
        if not self.selected_supplier:
            messagebox.showwarning("No Selection", "Please select a supplier to edit")
            return
        
        dialog = SupplierDialog(self, self.db, self.selected_supplier)
        self.wait_window(dialog)
        self.selected_supplier = None
        self.load_suppliers()
    
    def show_payment_dialog(self):
        """Show payment dialog"""
        if not self.selected_supplier:
            messagebox.showwarning("No Selection", "Please select a supplier")
            return
        
        dialog = PaymentDialog(self, self.db, self.selected_supplier, "supplier")
        self.wait_window(dialog)
        self.selected_supplier = None
        self.load_suppliers()


class SupplierDialog(ctk.CTkToplevel):
    """Supplier add/edit dialog"""
    
    def __init__(self, parent, db, supplier_data=None):
        super().__init__(parent)
        self.db = db
        self.supplier_data = supplier_data
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup dialog UI"""
        title = "Edit Supplier" if self.supplier_data else "Add Supplier"
        self.title(title)
        # Slightly taller so buttons are never clipped
        self.geometry("420x360")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog on screen
        self.update_idletasks()
        width = 420
        height = 360
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
            ("Supplier Name", "name", "Supplier Name"),
            ("Contact", "contact", "+91 98765 43210"),
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
        if self.supplier_data:
            self.entries["name"].insert(0, self.supplier_data[1])
            self.entries["contact"].insert(0, self.supplier_data[2])
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save_supplier,
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
    
    def save_supplier(self):
        """Save supplier to database"""
        try:
            name = self.entries["name"].get().strip()
            contact = self.entries["contact"].get().strip()
            
            if not name or not contact:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if self.supplier_data:
                query = "UPDATE suppliers SET name=?, contact=? WHERE id=?"
                params = (name, contact, self.supplier_data[0])
            else:
                query = "INSERT INTO suppliers (name, contact) VALUES (?, ?)"
                params = (name, contact)
            
            if self.db.execute_query(query, params):
                messagebox.showinfo("Success", "Supplier saved successfully")
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save supplier")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class PaymentDialog(ctk.CTkToplevel):
    """Payment dialog for suppliers or customers"""
    
    def __init__(self, parent, db, entity_data, entity_type):
        super().__init__(parent)
        self.db = db
        self.entity_data = entity_data
        self.entity_type = entity_type  # "supplier" or "customer"
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup payment dialog"""
        entity_name = self.entity_data[1]
        self.title(f"Payment - {entity_name}")
        # Slightly larger window so bottom buttons are clearly visible
        self.geometry("420x360")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        title_label = ctk.CTkLabel(
            container,
            text=f"Payment - {entity_name}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Current pending amount
        pending = self.entity_data[4] if self.entity_type == "supplier" else self.entity_data[3]
        pending_label = ctk.CTkLabel(
            container,
            text=f"Pending Amount: ₹ {pending:.2f}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text']
        )
        pending_label.pack(pady=(0, 20))
        
        # Payment amount
        amount_frame = ctk.CTkFrame(container, fg_color="transparent")
        amount_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            amount_frame,
            text="Payment Amount (₹)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.amount_entry = ctk.CTkEntry(
            amount_frame,
            placeholder_text="0.00",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.amount_entry.pack(fill="x")
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.record_payment,
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
    
    def record_payment(self):
        """Record payment"""
        try:
            amount = float(self.amount_entry.get())
            entity_id = self.entity_data[0]
            
            if amount <= 0:
                messagebox.showerror("Error", "Payment amount must be greater than 0")
                return
            
            # Record payment in payments table
            if self.entity_type == "supplier":
                query = "INSERT INTO supplier_payments (supplier_id, amount) VALUES (?, ?)"
                # Update supplier pending payment
                update_query = "UPDATE suppliers SET pending_payment = pending_payment - ? WHERE id = ?"
            else:
                query = "INSERT INTO payments (customer_id, amount) VALUES (?, ?)"
                # Update customer due amount
                update_query = "UPDATE customers SET due_amount = due_amount - ?, last_payment_date = date('now') WHERE id = ?"
            
            if self.db.execute_query(query, (entity_id, amount)):
                if self.db.execute_query(update_query, (amount, entity_id)):
                    messagebox.showinfo("Success", "Payment recorded successfully")
                    self.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update balance")
            else:
                messagebox.showerror("Error", "Failed to record payment")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

