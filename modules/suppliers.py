"""
Supplier Management module
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
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
        self.total_suppliers_value = None
        self.total_pending_value = None
        self.suppliers_with_pending_value = None
        self.suppliers_frame = None
        self.page_label = None

        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        """Setup suppliers UI"""

        # Top: title + search + actions in one container
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.pack(fill="x", padx=20, pady=20)

        # Left: Title
        header_frame = ctk.CTkFrame(top_container, fg_color="transparent")
        header_frame.pack(side="left", fill="x", expand=True)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Supplier Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(anchor="w")

        # Right: search + actions stacked
        right_top_frame = ctk.CTkFrame(top_container, fg_color="transparent")
        right_top_frame.pack(side="right", fill="x")

        # Search bar (by name or contact)
        search_frame = ctk.CTkFrame(right_top_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 8))

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search suppliers by name or contact...",
            height=36,
            font=ctk.CTkFont(size=12),
        )
        search_entry.pack(fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_suppliers(search_entry.get()))

        # Action buttons row – add, log, refresh
        actions_frame = ctk.CTkFrame(right_top_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(2, 0))

        btn_font = ctk.CTkFont(size=12)

        add_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Add Supplier",
            command=self.show_add_supplier_dialog,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
        )
        add_btn.pack(side="left", padx=3)

        log_btn = ctk.CTkButton(
            actions_frame,
            text="📝 Add Purchase Log",
            command=self.show_add_purchase_log_dialog,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=38,
            width=160,
            corner_radius=8,
            font=btn_font,
        )
        log_btn.pack(side="left", padx=3)

        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="⟳ Refresh",
            command=self.refresh_page,
            fg_color=COLORS['surface'],
            hover_color=COLORS.get("surface_hover", COLORS['surface']),
            text_color=COLORS['text'],
            height=38,
            width=110,
            corner_radius=8,
            font=btn_font,
            border_width=1,
            border_color=COLORS.get("border", COLORS['secondary']),
        )
        refresh_btn.pack(side="left", padx=3)

        # Summary cards row
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

        self.total_suppliers_value = create_summary_card(summary_frame, "Total Suppliers")
        self.total_pending_value = create_summary_card(summary_frame, "Total Pending Payment")
        self.suppliers_with_pending_value = create_summary_card(summary_frame, "Suppliers With Pending Dues")

        # Main split area: left = suppliers table, right = logs table (50/50)
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configure a green-themed Treeview style for both tables
        style = ttk.Style()
        # Use a base theme that allows custom colors
        try:
            style.theme_use("clam")
        except Exception:
            pass

        primary_color = COLORS['primary']
        text_color = COLORS['text']
        bg_color = COLORS['surface']
        header_bg = COLORS.get("surface_hover", bg_color)
        style.configure(
            "VSG.Treeview",
            background=bg_color,
            fieldbackground=bg_color,
            foreground=text_color,
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "VSG.Treeview.Heading",
            background=header_bg,
            foreground=text_color,
            relief="flat",
        )
        style.map(
            "VSG.Treeview",
            background=[("selected", primary_color)],
            foreground=[("selected", "white")],
        )

        # Left: suppliers table as a proper ttk.Treeview (takes half the width)
        table_frame = ctk.CTkFrame(main_split, fg_color=COLORS['surface'], corner_radius=10)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        table_label = ctk.CTkLabel(
            table_frame,
            text="Supplier List",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        table_label.pack(pady=12, padx=15, anchor="w")

        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        columns = ("name", "contact", "products", "last_purchase", "pending", "total", "status")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=12,
            style="VSG.Treeview",
        )
        # Headings
        self.tree.heading("name", text="Supplier Name")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("products", text="Products / Category")
        self.tree.heading("last_purchase", text="Last Purchase")
        self.tree.heading("pending", text="Pending")
        self.tree.heading("total", text="Total")
        self.tree.heading("status", text="Status")

        # Click-to-sort on headings (proper table behavior)
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_treeview(self.tree, c))

        # Column widths
        self.tree.column("name", width=170, anchor="w")
        self.tree.column("contact", width=120, anchor="w")
        self.tree.column("products", width=150, anchor="w")
        self.tree.column("last_purchase", width=100, anchor="w")
        self.tree.column("pending", width=100, anchor="e")
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("status", width=80, anchor="center")

        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Row action buttons under the table for selected supplier
        actions_bar = ctk.CTkFrame(table_frame, fg_color="transparent")
        actions_bar.pack(fill="x", padx=12, pady=(0, 8))

        small_font = ctk.CTkFont(size=11)
        self.view_btn = ctk.CTkButton(
            actions_bar,
            text="View",
            width=70,
            height=30,
            font=small_font,
            command=self.view_selected_supplier,
            fg_color=COLORS['surface'],
            hover_color=COLORS.get("surface_hover", COLORS['surface']),
            text_color=COLORS['text'],
            border_width=1,
            border_color=COLORS.get("border", COLORS['secondary']),
        )
        self.view_btn.pack(side="left", padx=4)

        self.pay_btn = ctk.CTkButton(
            actions_bar,
            text="Pay",
            width=70,
            height=30,
            font=small_font,
            command=self.pay_selected_supplier,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
        )
        self.pay_btn.pack(side="left", padx=4)

        self.hist_btn = ctk.CTkButton(
            actions_bar,
            text="History",
            width=80,
            height=30,
            font=small_font,
            command=self.history_selected_supplier,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
        )
        self.hist_btn.pack(side="left", padx=4)

        # bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda _e: self.view_selected_supplier())

        # Pagination/info label
        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.pack(pady=(0, 12))

        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Showing 0 of 0 suppliers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        self.page_label.pack()

        # Right: recent purchase logs as a proper ttk.Treeview table
        logs_frame = ctk.CTkFrame(main_split, fg_color=COLORS['surface'], corner_radius=10)
        logs_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))

        logs_label = ctk.CTkLabel(
            logs_frame,
            text="Recent Purchase Logs",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text'],
        )
        logs_label.pack(pady=12, padx=15, anchor="w")

        logs_container = ctk.CTkFrame(logs_frame, fg_color="transparent")
        logs_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.logs_tree = ttk.Treeview(
            logs_container,
            columns=("date", "supplier", "details", "amount"),
            show="headings",
            height=12,
            style="VSG.Treeview",
        )
        self.logs_tree.heading("date", text="Date")
        self.logs_tree.heading("supplier", text="Supplier")
        self.logs_tree.heading("details", text="Details")
        self.logs_tree.heading("amount", text="Amount")

        # Click-to-sort for logs table too
        for col in ("date", "supplier", "details", "amount"):
            self.logs_tree.heading(col, command=lambda c=col: self.sort_treeview(self.logs_tree, c))

        self.logs_tree.column("date", width=110, anchor="w")
        self.logs_tree.column("supplier", width=140, anchor="w")
        self.logs_tree.column("details", width=220, anchor="w")
        self.logs_tree.column("amount", width=90, anchor="e")

        logs_scroll = ttk.Scrollbar(logs_container, orient="vertical", command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scroll.set)
        self.logs_tree.pack(side="left", fill="both", expand=True)
        logs_scroll.pack(side="right", fill="y")

        self.logs_hint = ctk.CTkLabel(
            logs_frame,
            text="Select a supplier on the left to see their logs.\nIf none selected, showing latest logs for all.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light'],
            justify="left",
        )
        self.logs_hint.pack(padx=12, pady=(0, 10), anchor="w")

        # initial load of logs
        self.load_logs()

    def sort_treeview(self, tree: ttk.Treeview, col: str):
        """Sort a ttk.Treeview by column; toggles asc/desc per column."""
        # Remember last sort direction per tree/column
        key = f"_sort_{id(tree)}_{col}"
        reverse = bool(getattr(self, key, False))
        setattr(self, key, not reverse)

        def to_num(v: str):
            try:
                cleaned = str(v).replace("₹", "").replace(",", "").strip()
                return float(cleaned)
            except Exception:
                return None

        rows = []
        for iid in tree.get_children(""):
            val = tree.set(iid, col)
            num = to_num(val)
            rows.append((num if num is not None else str(val).lower(), iid))

        rows.sort(reverse=reverse, key=lambda x: x[0])
        for idx, (_val, iid) in enumerate(rows):
            tree.move(iid, "", idx)

    # ------------------------------------------------------------------
    # Data loading & filtering
    # ------------------------------------------------------------------
    def load_suppliers(self, search_term: str = ""):
        """Load suppliers from database, optionally filtered by search term"""
        # Clear existing rows from the tree
        if hasattr(self, "tree"):
            for item in self.tree.get_children():
                self.tree.delete(item)

        query = "SELECT * FROM suppliers WHERE 1=1"
        params = []

        if search_term:
            query += " AND (name LIKE ? OR contact LIKE ?)"
            like = f"%{search_term}%"
            params.extend([like, like])

        query += " ORDER BY name"

        suppliers = self.db.fetch_all(query, tuple(params) if params else None)

        # Summary cards
        total_suppliers = len(suppliers)
        total_pending = sum(s[4] for s in suppliers) if suppliers else 0
        suppliers_with_pending = len([s for s in suppliers if s[4] > 0])

        self.total_suppliers_value.configure(text=str(total_suppliers))
        self.total_pending_value.configure(text=f"₹ {total_pending:,.2f}")
        self.suppliers_with_pending_value.configure(text=str(suppliers_with_pending))

        # Populate tree
        if suppliers and hasattr(self, "tree"):
            for supplier in suppliers:
                supplier_id, name, contact, last_purchase, pending_payment = (
                    supplier[0], supplier[1], supplier[2], supplier[3], supplier[4]
                )
                # format date
                if last_purchase:
                    try:
                        last_purchase_str = last_purchase.strftime("%Y-%m-%d")
                    except AttributeError:
                        last_purchase_str = str(last_purchase)
                else:
                    last_purchase_str = "N/A"

                # total purchases
                purchases_sum = self.db.fetch_one(
                    "SELECT COALESCE(SUM(total_amount), 0) FROM purchases WHERE supplier_id = ?",
                    (supplier_id,),
                )
                total_purchases = purchases_sum[0] if purchases_sum else 0.0

                # status
                if pending_payment > 0:
                    status_text = "Due"
                elif pending_payment < 0:
                    status_text = "Advance"
                else:
                    status_text = "Cleared"

                products_text = supplier[15] if len(supplier) > 15 and supplier[15] else "—"

                self.tree.insert(
                    "",
                    "end",
                    iid=str(supplier_id),
                    values=(
                        name,
                        contact,
                        products_text,
                        last_purchase_str,
                        f"₹ {pending_payment:,.2f}",
                        f"₹ {total_purchases:,.2f}",
                        status_text,
                    ),
                )
        else:
            # nothing to show
            pass

        count = len(suppliers)
        if count == 0:
            self.page_label.configure(text="Showing 0 of 0 suppliers")
        else:
            self.page_label.configure(text=f"Showing 1-{count} of {count} suppliers")

        # Refresh logs whenever the list changes (keep current selection filter if any)
        self.load_logs()

    def filter_suppliers(self, search_term: str):
        """Filter suppliers list based on search term"""
        self.load_suppliers(search_term=search_term)

    def on_tree_select(self, _event=None):
        """Handle selection in the treeview"""
        if not hasattr(self, "tree"):
            return
        selected = self.tree.selection()
        if not selected:
            return
        supplier_id = int(selected[0])
        self.select_supplier(supplier_id)

    def select_supplier(self, supplier_id):
        """Select a supplier"""
        query = "SELECT * FROM suppliers WHERE id = ?"
        supplier = self.db.fetch_one(query, (supplier_id,))
        if supplier:
            self.selected_supplier = supplier
            # When a supplier is selected, reload logs filtered for them
            self.load_logs()

    def load_logs(self):
        """Load recent purchase logs (filtered by selected supplier if any)"""
        # Clear existing rows in logs table
        if hasattr(self, "logs_tree"):
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)

        # Decide filter
        params = ()
        if self.selected_supplier:
            supplier_id = self.selected_supplier[0]
            self.logs_hint.configure(
                text=f"Showing recent logs for {self.selected_supplier[1]}."
            )
            query = """
                SELECT p.purchase_date, s.name, p.product, p.total_amount
                FROM purchases p
                JOIN suppliers s ON s.id = p.supplier_id
                WHERE p.supplier_id = ?
                ORDER BY p.purchase_date DESC, p.id DESC
                LIMIT 30
            """
            params = (supplier_id,)
        else:
            self.logs_hint.configure(
                text="Showing latest purchase logs across all suppliers."
            )
            query = """
                SELECT p.purchase_date, s.name, p.product, p.total_amount
                FROM purchases p
                JOIN suppliers s ON s.id = p.supplier_id
                ORDER BY p.purchase_date DESC, p.id DESC
                LIMIT 30
            """

        logs = self.db.fetch_all(query, params if params else None)

        if not logs or not hasattr(self, "logs_tree"):
            return

        for purchase_date, supplier_name, product, total_amount in logs:
            try:
                date_str = purchase_date.strftime("%Y-%m-%d")
            except AttributeError:
                date_str = str(purchase_date)

            self.logs_tree.insert(
                "",
                "end",
                values=(
                    date_str,
                    supplier_name,
                    product,
                    f"₹ {total_amount:,.2f}",
                ),
            )

    # Helpers for row action buttons
    def edit_supplier_from_row(self, supplier_id):
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if supplier:
            dialog = SupplierDialog(self, self.db, supplier)
            self.wait_window(dialog)
            self.load_suppliers()

    def pay_supplier_from_row(self, supplier_id):
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if supplier:
            dialog = PaymentDialog(self, self.db, supplier, "supplier")
            self.wait_window(dialog)
            self.load_suppliers()

    def history_from_row(self, supplier_id):
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if supplier:
            dialog = SupplierPaymentHistoryDialog(self, self.db, supplier)
            self.wait_window(dialog)

    # New helpers for actions based on currently selected supplier in tree
    def _get_selected_supplier_id(self):
        if not hasattr(self, "tree"):
            return None
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a supplier in the table first.")
            return None
        try:
            return int(sel[0])
        except ValueError:
            return None

    def view_selected_supplier(self):
        supplier_id = self._get_selected_supplier_id()
        if supplier_id is not None:
            self.view_supplier_details(supplier_id)

    def pay_selected_supplier(self):
        supplier_id = self._get_selected_supplier_id()
        if supplier_id is None:
            return
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if supplier:
            dialog = PaymentDialog(self, self.db, supplier, "supplier")
            self.wait_window(dialog)
            self.load_suppliers()

    def history_selected_supplier(self):
        supplier_id = self._get_selected_supplier_id()
        if supplier_id is None:
            return
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if supplier:
            dialog = SupplierPaymentHistoryDialog(self, self.db, supplier)
            self.wait_window(dialog)

    def view_supplier_details(self, supplier_id):
        supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if not supplier:
            messagebox.showerror("Error", "Supplier record not found")
            return
        dialog = SupplierDetailDialog(self, self.db, supplier)
        self.wait_window(dialog)

    # ------------------------------------------------------------------
    # Actions from top buttons
    # ------------------------------------------------------------------
    def show_add_supplier_dialog(self):
        dialog = SupplierDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_suppliers()

    def show_add_purchase_log_dialog(self):
        """Open dialog to record what was bought and when"""
        dialog = SupplierPurchaseLogDialog(self, self.db)
        self.wait_window(dialog)
        # Refresh suppliers so last purchase / pending updates reflect
        self.load_suppliers()

    def refresh_page(self):
        """Manually refresh suppliers list and logs"""
        self.selected_supplier = None
        self.load_suppliers()

    def show_edit_supplier_dialog(self):
        """Open search+select dialog, then edit the chosen supplier"""
        dialog = SupplierSelectDialog(self, self.db, mode="edit")
        self.wait_window(dialog)
        supplier = getattr(dialog, "selected_supplier", None)
        if supplier:
            edit_dialog = SupplierDialog(self, self.db, supplier)
            self.wait_window(edit_dialog)
            self.load_suppliers()

    def show_payment_history(self):
        """Open search+select dialog, then show history for chosen supplier"""
        dialog = SupplierSelectDialog(self, self.db, mode="history")
        self.wait_window(dialog)
        supplier = getattr(dialog, "selected_supplier", None)
        if supplier:
            hist_dialog = SupplierPaymentHistoryDialog(self, self.db, supplier)
            self.wait_window(hist_dialog)

    def delete_supplier(self):
        """Open multi-select delete dialog for suppliers"""
        dialog = SupplierMultiDeleteDialog(self, self.db)
        self.wait_window(dialog)
        if getattr(dialog, "deleted_any", False):
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
        self.geometry("460x460")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])
        
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog on screen
        self.update_idletasks()
        width = 460
        height = 460
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
        title_label.pack(pady=(0, 16))
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, pady=(0, 12))
        
        # Form fields (basic and extended profile)
        field_defs = [
            ("Supplier Name", "name", "Supplier Name"),
            ("Primary Contact", "contact", "+91 98765 43210"),
            ("Alternate Contact", "alt_contact", ""),
            ("Email", "email", "supplier@example.com"),
            ("Address", "address", "Shop / Street"),
            ("City", "city", "City"),
            ("State", "state", "State"),
            ("GST Number", "gst_number", "27XXXXXXXXX1Z5"),
            ("Supplier Type", "supplier_type", "Wholesaler / Distributor"),
            ("Brands (comma separated)", "brands", "Tata, Aashirvaad"),
            ("Products (comma separated)", "products", "Atta, Rice, Oil"),
            ("Credit Limit (₹)", "credit_limit", "0"),
        ]

        self.entries = {}
        
        for label_text, key, placeholder in field_defs:
            frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
            frame.pack(fill="x", pady=6)

            ctk.CTkLabel(
                frame,
                text=label_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text'],
                anchor="w"
            ).pack(fill="x", pady=(0, 3))

            entry = ctk.CTkEntry(
                frame,
                placeholder_text=placeholder,
                height=32,
                font=ctk.CTkFont(size=12)
            )
            entry.pack(fill="x")
            self.entries[key] = entry
        
        # Notes as a multiline field
        notes_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        notes_frame.pack(fill="x", pady=6)

        ctk.CTkLabel(
            notes_frame,
            text="Notes / Remarks",
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

        # Pre-fill if editing (indices based on suppliers table definition)
        if self.supplier_data:
            self.entries["name"].insert(0, self.supplier_data[1])
            self.entries["contact"].insert(0, self.supplier_data[2])
            # created_at (5) and updated_at (6) are between basics and extended fields
            self.entries["alt_contact"].insert(0, self.supplier_data[7] or "")
            self.entries["email"].insert(0, self.supplier_data[8] or "")
            self.entries["address"].insert(0, self.supplier_data[9] or "")
            self.entries["city"].insert(0, self.supplier_data[10] or "")
            self.entries["state"].insert(0, self.supplier_data[11] or "")
            self.entries["gst_number"].insert(0, self.supplier_data[12] or "")
            self.entries["supplier_type"].insert(0, self.supplier_data[13] or "")
            self.entries["brands"].insert(0, self.supplier_data[14] or "")
            self.entries["products"].insert(0, self.supplier_data[15] or "")
            # notes at index 16, credit_limit at 17
            if self.supplier_data[16]:
                self.notes_text.insert("1.0", self.supplier_data[16])
            self.entries["credit_limit"].insert(0, str(self.supplier_data[17] or 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save_supplier,
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
    
    def save_supplier(self):
        """Save supplier to database"""
        try:
            name = self.entries["name"].get().strip()
            contact = self.entries["contact"].get().strip()
            alt_contact = self.entries["alt_contact"].get().strip()
            email = self.entries["email"].get().strip()
            address = self.entries["address"].get().strip()
            city = self.entries["city"].get().strip()
            state = self.entries["state"].get().strip()
            gst_number = self.entries["gst_number"].get().strip()
            supplier_type = self.entries["supplier_type"].get().strip()
            brands = self.entries["brands"].get().strip()
            products = self.entries["products"].get().strip()
            notes = self.notes_text.get("1.0", "end").strip()

            credit_raw = self.entries["credit_limit"].get().strip()
            try:
                credit_limit = float(credit_raw or 0)
            except ValueError:
                credit_limit = 0.0

            if not name or not contact:
                messagebox.showerror("Error", "Please fill at least name and primary contact")
                return

            if self.supplier_data:
                query = """
                    UPDATE suppliers
                    SET name=?,
                        contact=?,
                        alt_contact=?,
                        email=?,
                        address=?,
                        city=?,
                        state=?,
                        gst_number=?,
                        supplier_type=?,
                        brands=?,
                        products=?,
                        notes=?,
                        credit_limit=?
                    WHERE id=?
                """
                params = (
                    name,
                    contact,
                    alt_contact,
                    email,
                    address,
                    city,
                    state,
                    gst_number,
                    supplier_type,
                    brands,
                    products,
                    notes,
                    credit_limit,
                    self.supplier_data[0],
                )
            else:
                query = """
                    INSERT INTO suppliers (
                        name, contact, alt_contact, email, address, city, state,
                        gst_number, supplier_type, brands, products, notes, credit_limit
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    name,
                    contact,
                    alt_contact,
                    email,
                    address,
                    city,
                    state,
                    gst_number,
                    supplier_type,
                    brands,
                    products,
                    notes,
                    credit_limit,
                )

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
                pending = self.entity_data[4]
                if amount > pending:
                    messagebox.showerror("Error", "Payment cannot exceed pending amount for suppliers")
                    return
                query = "INSERT INTO supplier_payments (supplier_id, amount) VALUES (?, ?)"
                # Update supplier pending payment and last interaction
                update_query = """
                    UPDATE suppliers
                    SET pending_payment = pending_payment - ?,
                        last_interaction_date = date('now')
                    WHERE id = ?
                """
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


class SupplierPaymentHistoryDialog(ctk.CTkToplevel):
    """Payment history dialog for a supplier"""

    def __init__(self, parent, db, supplier_data):
        super().__init__(parent)
        self.db = db
        self.supplier_data = supplier_data
        self.setup_dialog()

    def setup_dialog(self):
        """Setup supplier payment history dialog"""
        supplier_name = self.supplier_data[1]
        self.title(f"Supplier Payments - {supplier_name}")
        self.geometry("640x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text=f"Payment History - {supplier_name}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text'],
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
                width=250,
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")

        # Payments list
        scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Load payments from supplier_payments table
        query = "SELECT payment_date, amount FROM supplier_payments WHERE supplier_id = ? ORDER BY payment_date DESC"
        payments = self.db.fetch_all(query, (self.supplier_data[0],))

        if not payments:
            no_data_label = ctk.CTkLabel(
                scroll_frame,
                text="No payment history found for this supplier",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_light'],
            )
            no_data_label.pack(pady=20)
        else:
            for payment in payments:
                row_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS['surface'], corner_radius=5)
                row_frame.pack(fill="x", pady=2, padx=5)

                payment_date = payment[0]
                try:
                    date_str = payment_date.strftime("%Y-%m-%d %H:%M")
                except AttributeError:
                    date_str = str(payment_date)

                date_label = ctk.CTkLabel(
                    row_frame,
                    text=date_str,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=250,
                )
                date_label.pack(side="left", padx=10, pady=8)

                amount_label = ctk.CTkLabel(
                    row_frame,
                    text=f"₹ {payment[1]:,.2f}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    width=250,
                )
                amount_label.pack(side="left", padx=10, pady=8)

        # Close button
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=36,
            font=ctk.CTkFont(size=12),
        )
        close_btn.pack(pady=10)


class SupplierDetailDialog(ctk.CTkToplevel):
    """Supplier detail dialog with logs"""

    def __init__(self, parent, db, supplier_data):
        super().__init__(parent)
        self.db = db
        self.supplier_data = supplier_data
        self.setup_dialog()

    def setup_dialog(self):
        supplier_id, name, contact, last_purchase, pending_payment = (
            self.supplier_data[0],
            self.supplier_data[1],
            self.supplier_data[2],
            self.supplier_data[3],
            self.supplier_data[4],
        )

        self.title(f"Supplier Details - {name}")
        self.geometry("460x460")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        width = 460
        height = 460
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        title_label = ctk.CTkLabel(
            container,
            text="Supplier Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 12))

        # Basic info section
        def info_row(parent, label_text, value_text):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", pady=4)

            label = ctk.CTkLabel(
                frame,
                text=label_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
                width=140,
                anchor="w",
            )
            label.pack(side="left")

            value = ctk.CTkLabel(
                frame,
                text=value_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text'],
                anchor="w",
            )
            value.pack(side="left", fill="x", expand=True)

        if last_purchase:
            try:
                last_purchase_str = last_purchase.strftime("%Y-%m-%d")
            except AttributeError:
                last_purchase_str = str(last_purchase)
        else:
            last_purchase_str = "N/A"

        purchases = self.db.fetch_all(
            "SELECT COALESCE(SUM(total_amount), 0) FROM purchases WHERE supplier_id = ?",
            (supplier_id,),
        )
        total_purchases = purchases[0][0] if purchases and purchases[0] else 0.0

        last_interaction_row = self.db.fetch_one(
            "SELECT last_interaction_date FROM suppliers WHERE id = ?",
            (supplier_id,),
        )
        last_interaction = last_interaction_row[0] if last_interaction_row else None
        last_interaction_str = str(last_interaction) if last_interaction else "N/A"

        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 8))

        info_row(info_frame, "Supplier Name", name)
        info_row(info_frame, "Contact", contact)
        info_row(info_frame, "Last Purchase Date", last_purchase_str)
        info_row(info_frame, "Total Purchases", f"₹ {total_purchases:,.2f}")
        info_row(info_frame, "Pending Balance", f"₹ {pending_payment:,.2f}")
        info_row(info_frame, "Last Interaction", last_interaction_str)

        # Logs section
        logs_frame = ctk.CTkFrame(container, fg_color=COLORS['surface'], corner_radius=10)
        logs_frame.pack(fill="both", expand=True, pady=(8, 0))

        logs_header = ctk.CTkLabel(
            logs_frame,
            text="Supplier Logs",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text'],
        )
        logs_header.pack(anchor="w", padx=12, pady=(8, 4))

        logs_list = ctk.CTkScrollableFrame(logs_frame, fg_color="transparent", height=140)
        logs_list.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        logs = self.db.fetch_all(
            "SELECT created_at, note FROM supplier_logs WHERE supplier_id = ? ORDER BY created_at DESC",
            (supplier_id,),
        )

        if not logs:
            ctk.CTkLabel(
                logs_list,
                text="No logs yet for this supplier.",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_light'],
            ).pack(pady=8)
        else:
            for created_at, note in logs:
                entry_frame = ctk.CTkFrame(logs_list, fg_color=COLORS['surface'], corner_radius=6)
                entry_frame.pack(fill="x", pady=3)

                date_str = str(created_at)
                ctk.CTkLabel(
                    entry_frame,
                    text=date_str,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_light'],
                    anchor="w",
                ).pack(fill="x", padx=8, pady=(4, 0))

                ctk.CTkLabel(
                    entry_frame,
                    text=note,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text'],
                    anchor="w",
                    wraplength=360,
                ).pack(fill="x", padx=8, pady=(0, 4))

        # Add log section
        add_log_frame = ctk.CTkFrame(container, fg_color="transparent")
        add_log_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            add_log_frame,
            text="Add Log Entry",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))

        log_text = ctk.CTkTextbox(
            add_log_frame,
            height=60,
            font=ctk.CTkFont(size=11),
        )
        log_text.pack(fill="x")

        def save_log():
            text = log_text.get("1.0", "end").strip()
            if not text:
                return
            if self.db.execute_query(
                "INSERT INTO supplier_logs (supplier_id, note) VALUES (?, ?)",
                (supplier_id, text),
            ):
                self.destroy()
                SupplierDetailDialog(self.master, self.db, self.supplier_data)

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))

        save_log_btn = ctk.CTkButton(
            btn_row,
            text="Save Log",
            command=save_log,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        save_log_btn.pack(side="left", fill="x", expand=True, padx=5)

        close_btn = ctk.CTkButton(
            btn_row,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        close_btn.pack(side="left", fill="x", expand=True, padx=5)


class SupplierPurchaseLogDialog(ctk.CTkToplevel):
    """Dialog to record what was bought from a supplier and when"""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setup_dialog()

    def setup_dialog(self):
        self.title("Add Purchase Log")
        self.geometry("500x440")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        width = 480
        height = 420
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        title_label = ctk.CTkLabel(
            container,
            text="Add Purchase Log",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 16))

        # Scrollable form so content never gets cut off
        form_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, pady=(0, 8))

        form = ctk.CTkFrame(form_scroll, fg_color="transparent")
        form.pack(fill="both", expand=True)

        # Supplier dropdown
        supplier_row = ctk.CTkFrame(form, fg_color="transparent")
        supplier_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            supplier_row,
            text="Supplier",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))

        suppliers = self.db.fetch_all("SELECT id, name, contact FROM suppliers ORDER BY name")
        self.supplier_map = {}
        supplier_values = []
        for sid, name, contact in suppliers:
            display = f"{name} ({contact})"
            self.supplier_map[display] = sid
            supplier_values.append(display)

        self.supplier_combo = ctk.CTkComboBox(
            supplier_row,
            values=supplier_values,
            state="readonly" if supplier_values else "disabled",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.supplier_combo.pack(fill="x")

        # What was bought (single product name for inventory)
        item_row = ctk.CTkFrame(form, fg_color="transparent")
        item_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            item_row,
            text="What was bought",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        self.item_entry = ctk.CTkEntry(
            item_row,
            placeholder_text="e.g. Rice 10kg",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.item_entry.pack(fill="x")

        # Quantity
        qty_row = ctk.CTkFrame(form, fg_color="transparent")
        qty_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            qty_row,
            text="Quantity",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        self.qty_entry = ctk.CTkEntry(
            qty_row,
            placeholder_text="e.g. 10",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.qty_entry.pack(fill="x")

        # Per unit price
        price_row = ctk.CTkFrame(form, fg_color="transparent")
        price_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            price_row,
            text="Price per unit (₹)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        self.price_entry = ctk.CTkEntry(
            price_row,
            placeholder_text="e.g. 50",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.price_entry.pack(fill="x")

        # Amount paid now
        paid_row = ctk.CTkFrame(form, fg_color="transparent")
        paid_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            paid_row,
            text="Amount paid now (₹)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        self.paid_entry = ctk.CTkEntry(
            paid_row,
            placeholder_text="e.g. 0 (if nothing paid now)",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.paid_entry.pack(fill="x")

        # Date (optional; defaults to today)
        date_row = ctk.CTkFrame(form, fg_color="transparent")
        date_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            date_row,
            text="Purchase date (YYYY-MM-DD, optional)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        self.date_entry = ctk.CTkEntry(
            date_row,
            placeholder_text="Leave empty for today",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self.date_entry.pack(fill="x")

        # Buttons
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 0))

        save_btn = ctk.CTkButton(
            btn_row,
            text="Save Log",
            command=self.save_log,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)

    def save_log(self):
        try:
            supplier_label = self.supplier_combo.get().strip()
            if not supplier_label or supplier_label not in self.supplier_map:
                messagebox.showerror("Error", "Please select a supplier")
                return
            supplier_id = self.supplier_map[supplier_label]

            item_desc = self.item_entry.get().strip()
            if not item_desc:
                messagebox.showerror("Error", "Please enter what was bought")
                return

            qty_raw = self.qty_entry.get().strip()
            price_raw = self.price_entry.get().strip()
            paid_raw = self.paid_entry.get().strip()

            try:
                quantity = float(qty_raw or 0)
                unit_price = float(price_raw or 0)
                amount_paid = float(paid_raw or 0)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity, price and amount paid")
                return

            if quantity <= 0 or unit_price < 0 or amount_paid < 0:
                messagebox.showerror("Error", "Quantity must be > 0, price must be ≥ 0 and amount paid must be ≥ 0")
                return

            total_amount = quantity * unit_price
            if amount_paid > total_amount:
                messagebox.showerror("Error", "Amount paid cannot be more than total purchase amount")
                return

            purchase_date = self.date_entry.get().strip()
            if purchase_date:
                # Basic sanity check; SQLite will still store as text if needed
                try:
                    datetime.strptime(purchase_date, "%Y-%m-%d")
                    date_value = purchase_date
                except ValueError:
                    messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
                    return
            else:
                date_value = None

            # Insert into purchases table
            if date_value:
                purchase_query = """
                    INSERT INTO purchases (supplier_id, product, quantity, unit_price, total_amount, purchase_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                purchase_params = (supplier_id, item_desc, quantity, unit_price, total_amount, date_value)
            else:
                purchase_query = """
                    INSERT INTO purchases (supplier_id, product, quantity, unit_price, total_amount)
                    VALUES (?, ?, ?, ?, ?)
                """
                purchase_params = (supplier_id, item_desc, quantity, unit_price, total_amount)

            ok = self.db.execute_query(purchase_query, purchase_params)
            if not ok:
                messagebox.showerror("Error", "Failed to save purchase log")
                return

            # Update supplier pending_payment and dates
            pending_increment = total_amount - amount_paid
            update_query = """
                UPDATE suppliers
                SET pending_payment = COALESCE(pending_payment, 0) + ?,
                    last_purchase_date = COALESCE(?, last_purchase_date),
                    last_interaction_date = date('now')
                WHERE id = ?
            """
            self.db.execute_query(update_query, (pending_increment, date_value, supplier_id))

            # If some amount is paid now, also record it in supplier_payments
            if amount_paid > 0:
                self.db.execute_query(
                    "INSERT INTO supplier_payments (supplier_id, amount) VALUES (?, ?)",
                    (supplier_id, amount_paid),
                )

            # Also update/create inventory product stock
            try:
                # Try to find existing product by name for this supplier
                existing_product = self.db.fetch_one(
                    "SELECT id, quantity FROM products WHERE name = ? AND supplier_id = ?",
                    (item_desc, supplier_id),
                )
                purchase_qty_int = int(quantity)

                if existing_product:
                    prod_id, current_qty = existing_product
                    new_qty = (current_qty or 0) + purchase_qty_int
                    self.db.execute_query(
                        """
                        UPDATE products
                        SET quantity = ?,
                            purchase_price = ?,
                            supplier_id = ?
                        WHERE id = ?
                        """,
                        (new_qty, unit_price, supplier_id, prod_id),
                    )
                else:
                    # Auto-generate a product_id
                    product_id = f"AUTO-{int(datetime.now().timestamp())}"
                    self.db.execute_query(
                        """
                        INSERT INTO products (
                            product_id, name, category, quantity,
                            unit_price, expiry_date, brand,
                            supplier_id, purchase_price, unit_type
                        )
                        VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)
                        """,
                        (
                            product_id,
                            item_desc,
                            "Others",
                            purchase_qty_int,
                            unit_price,
                            "",
                            supplier_id,
                            unit_price,
                            "p",
                        ),
                    )
            except Exception:
                # Silent fail – inventory update should not block purchase logging
                pass

            # Also drop a human-readable note into supplier_logs
            note = (
                f"Bought {item_desc} (qty {quantity}, ₹{unit_price:.2f} per unit, "
                f"total ₹{total_amount:.2f}, paid now ₹{amount_paid:.2f}, "
                f"pending added ₹{pending_increment:.2f})"
            )
            self.db.execute_query(
                "INSERT INTO supplier_logs (supplier_id, note) VALUES (?, ?)",
                (supplier_id, note),
            )

            messagebox.showinfo("Success", "Purchase log saved")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class SupplierSelectDialog(ctk.CTkToplevel):
    """Dialog to search & select a supplier (for edit/history)"""

    def __init__(self, parent, db, mode="edit"):
        super().__init__(parent)
        self.db = db
        self.mode = mode
        self.selected_supplier = None
        self.setup_dialog()

    def setup_dialog(self):
        title = "Select Supplier to Edit" if self.mode == "edit" else "Select Supplier for History"
        self.title(title)
        self.geometry("580x420")
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
            placeholder_text="Search suppliers by name or contact...",
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
            query = "SELECT id, name, contact, pending_payment FROM suppliers WHERE 1=1"
            params = []
            if term:
                query += " AND (name LIKE ? OR contact LIKE ?)"
                like = f"%{term}%"
                params.extend([like, like])
            query += " ORDER BY name"
            suppliers = self.db.fetch_all(query, tuple(params) if params else None)

            for s in suppliers:
                row = ctk.CTkFrame(self.rows_frame, fg_color=COLORS['surface'], corner_radius=6)
                row.pack(fill="x", pady=3, padx=4)

                balance = s[3]
                text = f"{s[1]} ({s[2]})  •  Pending: ₹ {balance:.2f}"
                lbl = ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text'],
                    anchor="w",
                )
                lbl.pack(fill="x", padx=10, pady=6)

                def on_click(_e=None, sid=s[0]):
                    supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (sid,))
                    if supplier:
                        self.selected_supplier = supplier
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


class SupplierMultiDeleteDialog(ctk.CTkToplevel):
    """Dialog to multi-select suppliers and delete them"""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.deleted_any = False
        self.check_vars = []
        self.setup_dialog()

    def setup_dialog(self):
        self.title("Delete Suppliers")
        self.geometry("600x420")
        self.configure(fg_color=COLORS['surface'])

        self.transient(self.master)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            container,
            text="Select suppliers to delete",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title_label.pack(pady=(0, 10))

        search_entry = ctk.CTkEntry(
            container,
            placeholder_text="Search suppliers by name or contact...",
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

            query = "SELECT id, name, contact, pending_payment FROM suppliers WHERE 1=1"
            params = []
            if term:
                query += " AND (name LIKE ? OR contact LIKE ?)"
                like = f"%{term}%"
                params.extend([like, like])
            query += " ORDER BY name"
            suppliers = self.db.fetch_all(query, tuple(params) if params else None)

            for s in suppliers:
                row = ctk.CTkFrame(self.rows_frame, fg_color=COLORS['surface'], corner_radius=6)
                row.pack(fill="x", pady=3, padx=4)

                var = ctk.BooleanVar(value=False)
                self.check_vars.append((var, s[0]))

                chk = ctk.CTkCheckBox(
                    row,
                    text="",
                    variable=var,
                    width=20,
                    checkbox_width=18,
                    checkbox_height=18,
                )
                chk.pack(side="left", padx=8)

                text = f"{s[1]} ({s[2]})  •  Pending: ₹ {s[3]:.2f}"
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
        ids = [sid for var, sid in self.check_vars if var.get()]
        if not ids:
            messagebox.showwarning("No Selection", "Please select at least one supplier to delete")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(ids)} selected suppliers?"):
            return
        ok = True
        for sid in ids:
            if not self.db.execute_query("DELETE FROM suppliers WHERE id = ?", (sid,)):
                ok = False
        if ok:
            messagebox.showinfo("Success", "Selected suppliers deleted successfully")
            self.deleted_any = True
            self.destroy()
        else:
            messagebox.showerror("Error", "Some suppliers could not be deleted")

