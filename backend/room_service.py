from database.db import get_connection


def get_all_rooms(status_filter=None):
    """Get all rooms, optionally filtered by status."""
    conn = get_connection()
    if status_filter and status_filter != "Tất cả":
        status_map = {"Trống": "available", "Đang thuê": "occupied", "Bảo trì": "maintenance"}
        status = status_map.get(status_filter, status_filter)
        rows = conn.execute("SELECT * FROM rooms WHERE status = ? ORDER BY room_number", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM rooms ORDER BY room_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_room_by_id(room_id):
    """Get a single room by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_room(room_number, floor, area, price, status="available", description=""):
    """Create a new room."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO rooms (room_number, floor, area, price, status, description) VALUES (?, ?, ?, ?, ?, ?)",
            (room_number, floor, area, price, status, description)
        )
        conn.commit()
        return True, "Thêm phòng thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_room(room_id, room_number, floor, area, price, status, description):
    """Update an existing room."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE rooms SET room_number=?, floor=?, area=?, price=?, status=?, description=? WHERE id=?",
            (room_number, floor, area, price, status, description, room_id)
        )
        conn.commit()
        return True, "Cập nhật phòng thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def delete_room(room_id):
    """Delete a room by ID."""
    conn = get_connection()
    try:
        # Check if room has active contracts
        active = conn.execute(
            "SELECT COUNT(*) as cnt FROM contracts WHERE room_id = ? AND status = 'active'",
            (room_id,)
        ).fetchone()
        if active["cnt"] > 0:
            return False, "Không thể xóa phòng đang có hợp đồng!"
        conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        return True, "Xóa phòng thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_room_stats():
    """Get room statistics."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as cnt FROM rooms").fetchone()["cnt"]
    available = conn.execute("SELECT COUNT(*) as cnt FROM rooms WHERE status='available'").fetchone()["cnt"]
    occupied = conn.execute("SELECT COUNT(*) as cnt FROM rooms WHERE status='occupied'").fetchone()["cnt"]
    maintenance = conn.execute("SELECT COUNT(*) as cnt FROM rooms WHERE status='maintenance'").fetchone()["cnt"]
    conn.close()
    return {
        "total": total,
        "available": available,
        "occupied": occupied,
        "maintenance": maintenance
    }


def get_available_rooms():
    """Get rooms that are available for contracts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms WHERE status = 'available' ORDER BY room_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_room_status(room_id, status):
    """Update room status."""
    conn = get_connection()
    conn.execute("UPDATE rooms SET status = ? WHERE id = ?", (status, room_id))
    conn.commit()
    conn.close()
