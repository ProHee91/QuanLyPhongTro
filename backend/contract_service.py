from database.db import get_connection
from backend.room_service import update_room_status


def get_all_contracts(status_filter=None):
    """Get all contracts with room and tenant info."""
    conn = get_connection()
    query = """
        SELECT c.*, r.room_number, r.price as room_price, t.name as tenant_name, t.phone as tenant_phone
        FROM contracts c
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
    """
    if status_filter and status_filter != "Tất cả":
        status_map = {"Đang hiệu lực": "active", "Hết hạn": "expired", "Đã hủy": "cancelled"}
        status = status_map.get(status_filter, status_filter)
        query += " WHERE c.status = ?"
        query += " ORDER BY c.created_at DESC"
        rows = conn.execute(query, (status,)).fetchall()
    else:
        query += " ORDER BY c.created_at DESC"
        rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contract_by_id(contract_id):
    """Get a single contract with room and tenant info."""
    conn = get_connection()
    row = conn.execute("""
        SELECT c.*, r.room_number, r.price as room_price, t.name as tenant_name, t.phone as tenant_phone
        FROM contracts c
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
        WHERE c.id = ?
    """, (contract_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_contract(room_id, tenant_id, start_date, end_date="", deposit=0):
    """Create a new contract and update room status."""
    conn = get_connection()
    try:
        # Check if room is available
        room = conn.execute("SELECT status FROM rooms WHERE id = ?", (room_id,)).fetchone()
        if not room or room["status"] != "available":
            return False, "Phòng không khả dụng!"

        conn.execute(
            "INSERT INTO contracts (room_id, tenant_id, start_date, end_date, deposit, status) VALUES (?, ?, ?, ?, ?, 'active')",
            (room_id, tenant_id, start_date, end_date, deposit)
        )
        conn.commit()
        conn.close()

        # Update room status to occupied
        update_room_status(room_id, "occupied")
        return True, "Tạo hợp đồng thành công!"
    except Exception as e:
        conn.close()
        return False, f"Lỗi: {str(e)}"


def cancel_contract(contract_id):
    """Cancel a contract and free up the room."""
    conn = get_connection()
    try:
        contract = conn.execute("SELECT room_id, status FROM contracts WHERE id = ?", (contract_id,)).fetchone()
        if not contract:
            return False, "Không tìm thấy hợp đồng!"
        if contract["status"] != "active":
            return False, "Hợp đồng không ở trạng thái hoạt động!"

        conn.execute("UPDATE contracts SET status = 'cancelled' WHERE id = ?", (contract_id,))
        conn.commit()
        room_id = contract["room_id"]
        conn.close()

        # Free up the room
        update_room_status(room_id, "available")
        return True, "Hủy hợp đồng thành công!"
    except Exception as e:
        conn.close()
        return False, f"Lỗi: {str(e)}"


def expire_contract(contract_id):
    """Mark a contract as expired and free up the room."""
    conn = get_connection()
    try:
        contract = conn.execute("SELECT room_id, status FROM contracts WHERE id = ?", (contract_id,)).fetchone()
        if not contract:
            return False, "Không tìm thấy hợp đồng!"
        if contract["status"] != "active":
            return False, "Hợp đồng không ở trạng thái hoạt động!"

        conn.execute("UPDATE contracts SET status = 'expired' WHERE id = ?", (contract_id,))
        conn.commit()
        room_id = contract["room_id"]
        conn.close()

        update_room_status(room_id, "available")
        return True, "Kết thúc hợp đồng thành công!"
    except Exception as e:
        conn.close()
        return False, f"Lỗi: {str(e)}"


def get_active_contracts():
    """Get all active contracts with room and tenant info."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, r.room_number, r.price as room_price, t.name as tenant_name
        FROM contracts c
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
        WHERE c.status = 'active'
        ORDER BY r.room_number
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
