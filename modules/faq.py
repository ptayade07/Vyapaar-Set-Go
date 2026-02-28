"""FAQ page for VyapaarSetGo"""
import customtkinter as ctk
from config import COLORS


class FAQ(ctk.CTkFrame):
    """FAQ page with all frequently asked questions"""

    def __init__(self, parent, selected_topic=None):
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        super().__init__(parent, fg_color=COLORS["background"])
        self.selected_topic = selected_topic
        self.setup_ui()

    def setup_ui(self):
        """Setup FAQ page UI"""
        # Import COLORS fresh to get current theme colors
        from config import COLORS
        
        # Main container
        main_container = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"])
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))

        title = ctk.CTkLabel(
            header_frame,
            text="Frequently Asked Questions",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w", pady=(0, 10))

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Find answers to common questions about VyapaarSetGo",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"],
        )
        subtitle.pack(anchor="w")

        # Topic filter buttons
        topics_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        topics_frame.pack(fill="x", pady=(0, 30))

        topics = [
            ("All", None),
            ("Dashboard", "dashboard"),
            ("Inventory", "inventory"),
            ("Customer Khata", "khata"),
            ("Suppliers", "suppliers"),
            ("Sales & Billing", "sales"),
            ("Reports", "reports"),
            ("Profile", "profile"),
        ]

        self.topic_buttons = {}
        for topic_name, topic_id in topics:
            btn = ctk.CTkButton(
                topics_frame,
                text=topic_name,
                command=lambda t=topic_id: self.filter_by_topic(t),
                fg_color=COLORS["primary"] if topic_id == self.selected_topic else COLORS["secondary"],
                hover_color=COLORS["primary_dark"] if topic_id == self.selected_topic else "#4b5563",
                height=35,
                font=ctk.CTkFont(size=12),
            )
            btn.pack(side="left", padx=5)
            self.topic_buttons[topic_id] = btn

        # FAQ content
        self.faq_content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.faq_content_frame.pack(fill="x")

        # Load FAQs
        self.load_faqs()

    def filter_by_topic(self, topic_id):
        """Filter FAQs by topic"""
        self.selected_topic = topic_id
        
        # Update button colors
        for tid, btn in self.topic_buttons.items():
            if tid == topic_id:
                btn.configure(fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"])
            else:
                btn.configure(fg_color=COLORS["secondary"], hover_color="#4b5563")
        
        # Reload FAQs
        for widget in self.faq_content_frame.winfo_children():
            widget.destroy()
        self.load_faqs()

    def load_faqs(self):
        """Load and display FAQs"""
        all_faqs = self.get_all_faqs()
        
        # Filter by selected topic
        if self.selected_topic:
            faqs_to_show = all_faqs.get(self.selected_topic, [])
            if faqs_to_show:
                self.create_faq_section(self.faq_content_frame, self.get_topic_name(self.selected_topic), faqs_to_show)
        else:
            # Show all FAQs grouped by topic
            for topic_id, faqs in all_faqs.items():
                if faqs:
                    self.create_faq_section(self.faq_content_frame, self.get_topic_name(topic_id), faqs)

    def create_faq_section(self, parent, topic_name, faqs):
        """Create a FAQ section for a topic"""
        section_frame = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        section_frame.pack(fill="x", pady=(0, 20))

        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=topic_name,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 15))

        # FAQ items
        for i, (question, answer) in enumerate(faqs):
            faq_item = ctk.CTkFrame(section_frame, fg_color=COLORS["background"], corner_radius=8)
            faq_item.pack(fill="x", padx=20, pady=(0, 15))

            # Question
            question_label = ctk.CTkLabel(
                faq_item,
                text=f"Q{i+1}. {question}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text"],
                anchor="w",
                justify="left",
            )
            question_label.pack(anchor="w", padx=15, pady=(15, 8))

            # Answer
            answer_label = ctk.CTkLabel(
                faq_item,
                text=f"A: {answer}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_light"],
                anchor="w",
                justify="left",
                wraplength=900,
            )
            answer_label.pack(anchor="w", padx=15, pady=(0, 15))

    def get_topic_name(self, topic_id):
        """Get display name for topic"""
        names = {
            "dashboard": "Dashboard",
            "inventory": "Inventory Management",
            "khata": "Customer Khata",
            "suppliers": "Suppliers",
            "sales": "Sales & Billing",
            "reports": "Reports & Analytics",
            "profile": "Profile & Settings",
        }
        return names.get(topic_id, "General")

    def get_all_faqs(self):
        """Get all FAQs organized by topic"""
        return {
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

