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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

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
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

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
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

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
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

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

