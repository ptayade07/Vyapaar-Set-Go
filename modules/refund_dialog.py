import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from datetime import datetime


class RefundDialog(ctk.CTkToplevel):
    """Simple dialog to record a return / refund against a previous sale."""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Return / Refund")
        self.configure(fg_color=COLORS['surface'])
        self.geometry("380x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            container,
            text="Record Return / Refund",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text'],
        )
        title.pack(pady=(0, 10))

        info = ctk.CTkLabel(
            container,
            text=(
                "Enter the original Transaction ID and refund amount.\n"
                "This will create a negative sale entry for reports."
            ),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light'],
            justify="left",
        )
        info.pack(pady=(0, 15))

        txn_label = ctk.CTkLabel(
            container,
            text="Original Transaction ID",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        )
        txn_label.pack(fill="x")
        self.txn_entry = ctk.CTkEntry(container, height=34, font=ctk.CTkFont(size=12))
        self.txn_entry.pack(fill="x", pady=(0, 10))

        amt_label = ctk.CTkLabel(
            container,
            text="Refund Amount (₹)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text'],
            anchor="w",
        )
        amt_label.pack(fill="x")
        self.amount_entry = ctk.CTkEntry(container, height=34, font=ctk.CTkFont(size=12))
        self.amount_entry.pack(fill="x", pady=(0, 15))

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Refund",
            command=self.save_refund,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=34,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            height=34,
            font=ctk.CTkFont(size=13),
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=5)

    def save_refund(self):
        try:
            txn_id = self.txn_entry.get().strip()
            if not txn_id:
                messagebox.showerror("Error", "Please enter the original Transaction ID.")
                return
            amt_str = self.amount_entry.get().strip()
            amount = float(amt_str or 0)
            if amount <= 0:
                messagebox.showerror("Error", "Refund amount must be greater than zero.")
                return

            # Find original sale
            original = self.db.fetch_one(
                "SELECT id, customer_id FROM sales WHERE transaction_id = ?",
                (txn_id,),
            )
            if not original:
                messagebox.showerror("Error", "No sale found with that Transaction ID.")
                return

            original_id, customer_id = original

            # Create a negative sale entry marked as return
            refund_txn = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            sale_query = """
                INSERT INTO sales (transaction_id, total_amount, discount, final_amount,
                                   tax_amount, payment_method, is_return, original_sale_id, customer_id)
                VALUES (?, 0, 0, ?, 0, 'Refund', 1, ?, ?)
            """
            if not self.db.execute_query(sale_query, (refund_txn, -amount, original_id, customer_id)):
                messagebox.showerror("Error", "Failed to save refund.")
                return

            messagebox.showinfo("Success", f"Refund of ₹ {amount:.2f} recorded.\nReference: {refund_txn}")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
