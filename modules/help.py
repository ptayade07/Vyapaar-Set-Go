"""Help page for VyapaarSetGo"""
import customtkinter as ctk
from config import COLORS, APP_NAME


class Help(ctk.CTkFrame):
    """Help and documentation page"""

    def __init__(self, parent, on_navigate=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS["background"])
        self.on_navigate = on_navigate
        self.setup_ui()

    def setup_ui(self):
        """Setup help page UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Main container (regular frame, no vertical scrollbar)
        main_container = ctk.CTkFrame(self, fg_color=COLORS["background"])
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header Section - use standard surface color so it matches theme
        header_section = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["surface"],
            corner_radius=16,
        )
        header_section.pack(fill="x", pady=(0, 30))

        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=40)

        title = ctk.CTkLabel(
            header_content,
            text="How can we help?",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w", pady=(0, 20))

        # Search bar
        search_frame = ctk.CTkFrame(
            header_content,
            fg_color=COLORS["surface"],
            corner_radius=999,
            border_width=1,
            border_color=COLORS.get("border", COLORS["secondary"]),
        )
        search_frame.pack(fill="x", pady=(0, 18))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search for help topics, e.g. 'sales', 'inventory', 'suppliers'...",
            height=42,
            font=ctk.CTkFont(size=14),
            border_width=0,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(18, 8), pady=8)

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.perform_search,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            height=36,
            width=90,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=999,
        )
        search_btn.pack(side="right", padx=(0, 14), pady=8)
        # Hitting Enter in the search box will also trigger search
        self.search_entry.bind("<Return>", lambda _e: self.perform_search())

        # Help Cards Section
        cards_label = ctk.CTkLabel(
            main_container,
            text="Browse by Topic",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"],
        )
        cards_label.pack(anchor="w", pady=(10, 20))

        # Cards grid (store master list for searching)
        self.cards_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 30))

        self.help_cards_master = [
            ("🏠", "Dashboard", "View your business overview, sales trends, and key metrics to track your store's performance.", "dashboard"),
            ("📦", "Inventory", "Manage your products - add, edit, delete items, track stock levels, and organize by categories.", "inventory"),
            ("📒", "Customer Khata", "Keep track of customer accounts, pending dues, and payment history for credit management.", "khata"),
            ("🚚", "Suppliers", "Manage supplier information, contacts, and track pending payments to suppliers.", "suppliers"),
            ("🛒", "Sales & Billing", "Process sales transactions, generate bills, and automatically update inventory stock levels.", "sales"),
            ("📊", "Reports", "View detailed reports and analytics including daily, monthly sales trends and business insights.", "reports"),
            ("👤", "Profile & Settings", "Manage your account settings, change password, and update profile information.", "profile"),
            ("❓", "Getting Started", "Learn the basics of using VyapaarSetGo with step-by-step guides and tutorials.", None),
        ]

        self.render_help_cards(self.help_cards_master)

    def render_help_cards(self, cards_data):
        """Render help cards grid from a list of (icon, title, description, page)."""
        # Import COLORS fresh to get current theme colors
        from config import COLORS

        # Clear previous cards
        for child in self.cards_frame.winfo_children():
            child.destroy()

        if not cards_data:
            empty = ctk.CTkLabel(
                self.cards_frame,
                text="No help topics found. Try a different search.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_light"],
            )
            empty.pack(pady=10)
            return

        # Create cards in grid (2 rows, 4 columns)
        row_frames = []
        for i, (icon, title, description, page) in enumerate(cards_data):
            row = i // 4
            col = i % 4

            if col == 0:
                row_frame = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=(0, 15))
                row_frames.append(row_frame)
            else:
                row_frame = row_frames[row]

            card = self.create_help_card(row_frame, icon, title, description, page)
            card.pack(side="left", fill="both", expand=True, padx=(0, 15) if col < 3 else (0, 0))

    def perform_search(self):
        """Filter help cards based on search text."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self.render_help_cards(self.help_cards_master)
            return

        filtered = []
        for icon, title, desc, page in self.help_cards_master:
            text = f"{title} {desc}".lower()
            if query in text:
                filtered.append((icon, title, desc, page))

        self.render_help_cards(filtered)

    def create_help_card(self, parent, icon, title, description, page):
        """Create a help card (original simpler layout)"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=40),
            text_color=COLORS["primary"],
        )
        icon_label.pack(pady=(25, 15))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(pady=(0, 10), padx=20)
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_light"],
            wraplength=250,
            justify="left",
        )
        desc_label.pack(pady=(0, 20), padx=20)
        
        # FAQ link
        link_label = ctk.CTkLabel(
            card,
            text="View FAQ →",
            font=ctk.CTkFont(size=12, underline=True),
            text_color=COLORS["primary"],
            cursor="hand2" if page else "arrow",
        )
        link_label.pack(pady=(0, 25))
        
        # Make card clickable if page is provided
        if page:
            def show_faq(_event=None):
                if self.on_navigate:
                    # Navigate to FAQ page with selected topic
                    self.on_navigate("faq", page)
                else:
                    # Show FAQ dialog as fallback
                    FAQDialog(self, title, page)
            
            for widget in [card, icon_label, title_label, desc_label, link_label]:
                widget.bind("<Button-1>", show_faq)
        
        return card


class FAQDialog:
    """Dialog for showing FAQ for a specific topic"""
    
    def __init__(self, parent, topic, page):
        self.topic = topic
        self.page = page
        
        # Create top-level window
        self.top = ctk.CTkToplevel(parent)
        self.top.title(f"FAQ - {topic}")
        self.top.geometry("700x600")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the window
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.top.winfo_screenheight() // 2) - (600 // 2)
        self.top.geometry(f"700x600+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup FAQ dialog UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        main_frame = ctk.CTkFrame(self.top, fg_color=COLORS["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Frequently Asked Questions - {self.topic}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(pady=(10, 20))
        
        # Scrollable FAQ content
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Get FAQ content based on page
        faqs = self.get_faqs_for_page(self.page)
        
        for i, (question, answer) in enumerate(faqs):
            faq_card = ctk.CTkFrame(scroll_frame, fg_color=COLORS["background"], corner_radius=8)
            faq_card.pack(fill="x", pady=(0, 15), padx=10)
            
            # Question
            question_label = ctk.CTkLabel(
                faq_card,
                text=f"Q{i+1}. {question}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text"],
                anchor="w",
                justify="left",
            )
            question_label.pack(anchor="w", padx=15, pady=(15, 8))
            
            # Answer
            answer_label = ctk.CTkLabel(
                faq_card,
                text=f"A: {answer}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_light"],
                anchor="w",
                justify="left",
                wraplength=600,
            )
            answer_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            command=self.top.destroy,
        )
        close_btn.pack(pady=(10, 0))
    
    def get_faqs_for_page(self, page):
        """Get FAQ content for a specific page"""
        faqs_by_page = {
            "dashboard": [
                ("How do I view my business metrics?", "The dashboard displays key metrics including total products, customers, today's sales, and pending dues. These are automatically calculated from your data."),
                ("What does 'Pending Dues' mean?", "Pending Dues shows the total amount owed by customers who have credit accounts (Khata). This helps you track outstanding payments."),
                ("How often is the dashboard updated?", "The dashboard updates in real-time. Refresh the page or navigate away and back to see the latest data."),
            ],
            "inventory": [
                ("How do I add a new product?", "Go to Inventory → Click 'Add Product' → Fill in product details (ID, name, category, quantity, price) → Click Save."),
                ("Can I edit product information?", "Yes, click on any product in the list and use the Edit button to modify its details."),
                ("What happens when I sell a product?", "When you process a sale, the product quantity is automatically reduced from your inventory."),
                ("How do I track low stock items?", "Products with low quantity will be highlighted. You can also filter products by stock level."),
            ],
            "khata": [
                ("What is Customer Khata?", "Khata is a credit account system where customers can make purchases on credit and pay later."),
                ("How do I add a customer?", "Go to Khata → Click 'Add Customer' → Enter customer details → Set initial due amount if any → Save."),
                ("How do I record a payment?", "Select a customer → Click 'Record Payment' → Enter payment amount → The due amount will be updated automatically."),
                ("Can I see payment history?", "Yes, click on a customer to view their complete payment history and transaction details."),
            ],
            "suppliers": [
                ("How do I add a supplier?", "Go to Suppliers → Click 'Add Supplier' → Enter supplier information (name, contact, address) → Save."),
                ("How do I track supplier payments?", "Each supplier has a pending payment amount. You can record payments to update the balance."),
                ("Can I edit supplier information?", "Yes, select a supplier and click Edit to modify their details."),
            ],
            "sales": [
                ("How do I process a sale?", "Go to Sales → Search for products → Add to cart with quantities → Apply discount if needed → Generate Bill."),
                ("Can I print the bill?", "Yes, after generating a bill, you can print it. The bill includes all transaction details."),
                ("What happens to inventory after a sale?", "Product quantities are automatically deducted from your inventory when you complete a sale."),
                ("Can I apply discounts?", "Yes, you can apply a discount percentage before generating the bill."),
            ],
            "reports": [
                ("What reports are available?", "You can view daily, monthly, and custom date range reports with sales trends and profit analysis."),
                ("Can I export reports?", "Yes, you can download reports as CSV or print them directly from the Reports page."),
                ("How is profit calculated?", "Profit is calculated based on your sales data. The system shows profit trends over time."),
            ],
            "profile": [
                ("How do I change my password?", "Go to Profile → Click 'Change Password' → Enter current and new password → Save."),
                ("Can I edit my username?", "Yes, click 'Edit Profile' to change your username. Make sure the new username is unique."),
                ("What information is shown in my profile?", "Your profile displays your user ID, username, role, and account statistics."),
            ],
        }
        
        return faqs_by_page.get(page, [
            ("How do I get started?", "Start by adding products to your inventory, then add customers and suppliers. You can then begin processing sales."),
            ("Where can I find help?", "Check the Help section for detailed guides on each feature of VyapaarSetGo."),
        ])

