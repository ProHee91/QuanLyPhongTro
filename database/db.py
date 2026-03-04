import os
import hashlib
import sqlite3

# Try libsql for Turso cloud, fall back to sqlite3 for local dev
try:
    import libsql_experimental as libsql
    HAS_LIBSQL = True
except ImportError:
    HAS_LIBSQL = False


def _get_turso_url():
    """Get Turso database URL from Streamlit secrets or env vars."""
    try:
        import streamlit as st
        return st.secrets["TURSO_DATABASE_URL"]
    except Exception:
        return os.environ.get("TURSO_DATABASE_URL", "")


def _get_turso_token():
    """Get Turso auth token from Streamlit secrets or env vars."""
    try:
        import streamlit as st
        return st.secrets["TURSO_AUTH_TOKEN"]
    except Exception:
        return os.environ.get("TURSO_AUTH_TOKEN", "")


def get_connection():
    """Get a database connection. Uses Turso if available, otherwise local SQLite."""
    url = _get_turso_url()
    token = _get_turso_token()

    if HAS_LIBSQL and url and token:
        conn = libsql.connect(database=url, auth_token=token)
    else:
        _base = os.environ.get(
            "APP_DATA_DIR",
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        db_path = os.path.join(_base, "phong_tro.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()

    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            tenant_id INTEGER DEFAULT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            floor INTEGER DEFAULT 1,
            area REAL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'available',
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT DEFAULT '',
            id_card TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            date_of_birth TEXT DEFAULT '',
            address TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            tenant_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT DEFAULT '',
            deposit REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )""",
        """CREATE TABLE IF NOT EXISTS invoices (
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
            status TEXT NOT NULL DEFAULT 'unpaid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        )""",
    ]

    for sql in tables:
        conn.execute(sql)

    # Seed default admin user if no users exist
    existing = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
    if existing[0] == 0:
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Quản trị viên", "admin")
        )

    conn.commit()
    conn.close()
