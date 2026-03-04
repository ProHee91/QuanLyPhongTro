from database.db import get_connection


def get_all_tenants(search_query=None):
    """Get all tenants, optionally filtered by search query."""
    conn = get_connection()
    if search_query:
        query = f"%{search_query}%"
        rows = conn.execute(
            "SELECT * FROM tenants WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
            (query, query)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tenants ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tenant_by_id(tenant_id):
    """Get a single tenant by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_tenant(name, phone, email="", id_card="", gender="", date_of_birth="", address=""):
    """Create a new tenant."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO tenants (name, phone, email, id_card, gender, date_of_birth, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, phone, email, id_card, gender, date_of_birth, address)
        )
        conn.commit()
        return True, "Thêm khách thuê thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_tenant(tenant_id, name, phone, email, id_card, gender, date_of_birth, address):
    """Update an existing tenant."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tenants SET name=?, phone=?, email=?, id_card=?, gender=?, date_of_birth=?, address=? WHERE id=?",
            (name, phone, email, id_card, gender, date_of_birth, address, tenant_id)
        )
        conn.commit()
        return True, "Cập nhật thông tin thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def delete_tenant(tenant_id):
    """Delete a tenant by ID."""
    conn = get_connection()
    try:
        active = conn.execute(
            "SELECT COUNT(*) as cnt FROM contracts WHERE tenant_id = ? AND status = 'active'",
            (tenant_id,)
        ).fetchone()
        if active["cnt"] > 0:
            return False, "Không thể xóa khách đang có hợp đồng!"
        conn.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
        conn.commit()
        return True, "Xóa khách thuê thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_tenants_without_contract():
    """Get tenants that don't have an active contract."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.* FROM tenants t
        WHERE t.id NOT IN (
            SELECT tenant_id FROM contracts WHERE status = 'active'
        )
        ORDER BY t.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
