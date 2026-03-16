"""
Database connection and initialization module for VyapaarSetGo
"""
import sqlite3
from typing import Optional, List, Tuple


class Database:
    """Database connection and operations handler"""

    def __init__(self, db_path: str = "vyapaarsetgo.db"):
        self.connection: Optional[sqlite3.Connection] = None
        self.db_path = db_path

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return False

    def fetch_all(self, query: str, params: Tuple = None) -> List[Tuple]:
        """Fetch all rows from a SELECT query"""
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return [tuple(row) for row in results]
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_one(self, query: str, params: Tuple = None) -> Optional[Tuple]:
        """Fetch one row from a SELECT query"""
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return tuple(result) if result else None
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None

    # -------------------------------------------------------------------------
    # MAIN DATABASE INITIALIZATION (for login users only)
    # -------------------------------------------------------------------------
    def initialize_database(self):
        """Create main database with users table"""
        try:
            self.connect()
            cursor = self.connection.cursor()

            cursor.execute("PRAGMA foreign_keys = ON")

            # Users table exists ONLY in main database
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'shop_owner',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    avatar_path TEXT,
                    full_name TEXT,
                    phone TEXT,
                    email TEXT
                )
            """)

            # Ensure new user columns exist for older databases
            cursor.execute("PRAGMA table_info(users)")
            existing_user_cols = {row[1] for row in cursor.fetchall()}
            if "avatar_path" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT")
            if "full_name" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            if "phone" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            if "email" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

            self.connection.commit()
            cursor.close()

            print("User database initialized successfully!")
            return True

        except sqlite3.Error as e:
            print(f"Error initializing user database: {e}")
            return False

    # -------------------------------------------------------------------------
    # USER-SPECIFIC DATABASE INITIALIZATION (NO USERS TABLE HERE)
    # -------------------------------------------------------------------------
    def initialize_user_database(self):
        """Create user-specific database tables (NO users table here!)"""
        try:
            self.connect()
            cursor = self.connection.cursor()

            cursor.execute("PRAGMA foreign_keys = ON")

            # ---------------- Products Table ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit_price REAL NOT NULL,
                    expiry_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    brand TEXT,
                    supplier_id INTEGER,
                    purchase_price REAL,
                    unit_type TEXT,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            """)

            # Ensure new product columns exist for older databases
            cursor.execute("PRAGMA table_info(products)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            # Add columns one by one if they are missing
            if "brand" not in existing_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN brand TEXT")
            if "supplier_id" not in existing_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER")
            if "purchase_price" not in existing_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN purchase_price REAL")
            if "unit_type" not in existing_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN unit_type TEXT")

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_products_timestamp
                AFTER UPDATE ON products
                BEGIN
                    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)

            # ---------------- Suppliers Table ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    last_purchase_date DATE,
                    pending_payment REAL DEFAULT 0.00,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alt_contact TEXT,
                    email TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    gst_number TEXT,
                    supplier_type TEXT,
                    brands TEXT,
                    products TEXT,
                    notes TEXT,
                    credit_limit REAL DEFAULT 0.00,
                    last_interaction_date DATE
                )
            """)

            # Ensure new supplier columns exist for older databases
            cursor.execute("PRAGMA table_info(suppliers)")
            existing_supplier_cols = {row[1] for row in cursor.fetchall()}
            if "alt_contact" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN alt_contact TEXT")
            if "email" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN email TEXT")
            if "address" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN address TEXT")
            if "city" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN city TEXT")
            if "state" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN state TEXT")
            if "gst_number" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN gst_number TEXT")
            if "supplier_type" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN supplier_type TEXT")
            if "brands" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN brands TEXT")
            if "products" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN products TEXT")
            if "notes" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN notes TEXT")
            if "credit_limit" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN credit_limit REAL DEFAULT 0.00")
            if "last_interaction_date" not in existing_supplier_cols:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN last_interaction_date DATE")

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_suppliers_timestamp
                AFTER UPDATE ON suppliers
                BEGIN
                    UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)

            # ---------------- Customers Table ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    due_amount REAL DEFAULT 0.00,
                    last_payment_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    address TEXT,
                    notes TEXT
                )
            """)

            # Ensure new customer columns exist for older databases
            cursor.execute("PRAGMA table_info(customers)")
            existing_customer_cols = {row[1] for row in cursor.fetchall()}
            if "address" not in existing_customer_cols:
                cursor.execute("ALTER TABLE customers ADD COLUMN address TEXT")
            if "notes" not in existing_customer_cols:
                cursor.execute("ALTER TABLE customers ADD COLUMN notes TEXT")

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_customers_timestamp
                AFTER UPDATE ON customers
                BEGIN
                    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)

            # ---------------- Sales Table ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT UNIQUE NOT NULL,
                    total_amount REAL NOT NULL,
                    discount REAL DEFAULT 0.00,
                    final_amount REAL NOT NULL,
                    customer_id INTEGER,
                    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
                )
            """)

            # ---------------- Sale Items Table ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Customer Payments ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Supplier Payments ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS supplier_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Supplier Purchases ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    product TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Supplier Logs ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS supplier_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    note TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Product History ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    note TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)

            # ---------------- Notifications ----------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            cursor.close()

            print("User-specific database initialized successfully!")
            return True

        except sqlite3.Error as e:
            print(f"Error initializing user-specific database: {e}")
            return False

