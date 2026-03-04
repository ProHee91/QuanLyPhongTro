from database.db import get_connection, hash_password


def authenticate(username, password):
    """Authenticate a user. Returns user dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    """Get a user by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    """Get all users."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.*, t.name as tenant_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        ORDER BY u.role, u.username
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username, password, display_name, role="user", tenant_id=None):
    """Create a new user account."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role, tenant_id) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), display_name, role, tenant_id)
        )
        conn.commit()
        return True, "Tạo tài khoản thành công!"
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Tên đăng nhập đã tồn tại!"
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_user(user_id, display_name, role, tenant_id=None, new_password=None):
    """Update a user account."""
    conn = get_connection()
    try:
        if new_password:
            conn.execute(
                "UPDATE users SET display_name=?, role=?, tenant_id=?, password_hash=? WHERE id=?",
                (display_name, role, tenant_id, hash_password(new_password), user_id)
            )
        else:
            conn.execute(
                "UPDATE users SET display_name=?, role=?, tenant_id=? WHERE id=?",
                (display_name, role, tenant_id, user_id)
            )
        conn.commit()
        return True, "Cập nhật thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user (cannot delete yourself)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "Xóa tài khoản thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def change_password(user_id, old_password, new_password):
    """Change user password."""
    conn = get_connection()
    user = conn.execute(
        "SELECT password_hash FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if not user or user["password_hash"] != hash_password(old_password):
        conn.close()
        return False, "Mật khẩu cũ không đúng!"
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        return True, "Đổi mật khẩu thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_tenant_id_for_user(user_id):
    """Get the tenant_id associated with a user."""
    conn = get_connection()
    row = conn.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row["tenant_id"] if row and row["tenant_id"] else None
