import sqlite3
import os
import hashlib

# Use the working directory as base - works in both Docker (/app) and local environments
_BASE_DIR = os.environ.get("APP_DATA_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_BASE_DIR, "phong_tro.db")


def get_connection():
    """Get a database connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin', 'user')),
            tenant_id INTEGER DEFAULT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            floor INTEGER DEFAULT 1,
            area REAL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'maintenance')),
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT DEFAULT '',
            id_card TEXT DEFAULT '',
            gender TEXT DEFAULT '' CHECK(gender IN ('', 'Nam', 'Nữ')),
            date_of_birth TEXT DEFAULT '',
            address TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            tenant_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT DEFAULT '',
            deposit REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            electric_old REAL DEFAULT 0,
            electric_new REAL DEFAULT 0,
            water_old REAL DEFAULT 0,
            water_new REAL DEFAULT 0,
            electric_price REAL DEFAULT 3500,
            water_price REAL DEFAULT 15000,
            room_price REAL DEFAULT 0,
            other_fees REAL DEFAULT 0,
            other_fees_note TEXT DEFAULT '',
            total REAL DEFAULT 0,
            meter_updated INTEGER DEFAULT 0,
            user_meter_submitted INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'unpaid' CHECK(status IN ('unpaid', 'paid')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        );
    """)

    # ─── Auto-migration: add new columns to existing tables ──
    existing_cols = [c[1] for c in cursor.execute("PRAGMA table_info(invoices)").fetchall()]
    if "user_meter_submitted" not in existing_cols:
        cursor.execute("ALTER TABLE invoices ADD COLUMN user_meter_submitted INTEGER DEFAULT 0")

    # Seed default admin user if no users exist
    existing = cursor.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
    if existing[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Quản trị viên", "admin")
        )

    conn.commit()
    conn.close()

