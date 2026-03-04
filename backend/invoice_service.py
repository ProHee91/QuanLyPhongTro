from database.db import get_connection
from datetime import datetime


def get_all_invoices(month=None, year=None, status_filter=None):
    """Get all invoices with contract/room/tenant info."""
    conn = get_connection()
    query = """
        SELECT i.*, c.room_id, c.tenant_id, r.room_number, t.name as tenant_name
        FROM invoices i
        JOIN contracts c ON i.contract_id = c.id
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
        WHERE 1=1
    """
    params = []

    if month:
        query += " AND i.month = ?"
        params.append(month)
    if year:
        query += " AND i.year = ?"
        params.append(year)
    if status_filter and status_filter != "Tất cả":
        status_map = {"Chưa thanh toán": "unpaid", "Đã thanh toán": "paid"}
        status = status_map.get(status_filter, status_filter)
        query += " AND i.status = ?"
        params.append(status)

    query += " ORDER BY i.year DESC, i.month DESC, r.room_number"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_by_id(invoice_id):
    """Get a single invoice with full details."""
    conn = get_connection()
    row = conn.execute("""
        SELECT i.*, c.room_id, c.tenant_id, r.room_number, r.price as current_room_price,
               t.name as tenant_name, t.phone as tenant_phone
        FROM invoices i
        JOIN contracts c ON i.contract_id = c.id
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
        WHERE i.id = ?
    """, (invoice_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_invoice(contract_id, month, year, electric_old, electric_new,
                   water_old, water_new, electric_price, water_price,
                   room_price, other_fees=0, other_fees_note=""):
    """Create a new invoice with auto-calculated total."""
    electric_cost = (electric_new - electric_old) * electric_price
    water_cost = (water_new - water_old) * water_price
    total = room_price + electric_cost + water_cost + other_fees

    conn = get_connection()
    try:
        # Check if invoice already exists for this contract/month/year
        existing = conn.execute(
            "SELECT id FROM invoices WHERE contract_id = ? AND month = ? AND year = ?",
            (contract_id, month, year)
        ).fetchone()
        if existing:
            return False, "Hóa đơn cho tháng này đã tồn tại!"

        conn.execute(
            """INSERT INTO invoices (contract_id, month, year, electric_old, electric_new,
               water_old, water_new, electric_price, water_price, room_price,
               other_fees, other_fees_note, total, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'unpaid')""",
            (contract_id, month, year, electric_old, electric_new,
             water_old, water_new, electric_price, water_price, room_price,
             other_fees, other_fees_note, total)
        )
        conn.commit()
        return True, "Tạo hóa đơn thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def pay_invoice(invoice_id):
    """Mark an invoice as paid."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE invoices SET status = 'paid', paid_at = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), invoice_id)
        )
        conn.commit()
        return True, "Thanh toán thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def delete_invoice(invoice_id):
    """Delete an invoice (admin only)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        conn.commit()
        return True, "Xóa hóa đơn thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_meter_readings(invoice_id, electric_new, water_new):
    """Update only NEW meter readings for an invoice and recalculate total.
    Used by tenants — old readings are kept from DB, not editable.
    Once user saves, they cannot update again (user_meter_submitted=1)."""
    conn = get_connection()
    try:
        inv = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if not inv:
            return False, "Không tìm thấy hóa đơn!"
        if inv["status"] == "paid":
            return False, "Hóa đơn đã thanh toán, không thể cập nhật!"
        if inv["user_meter_submitted"]:
            return False, "Bạn đã lưu chỉ số rồi, không thể cập nhật lại!"

        electric_old = inv["electric_old"]
        water_old = inv["water_old"]

        # Validate readings
        if electric_new < electric_old:
            return False, "Chỉ số điện mới phải lớn hơn hoặc bằng chỉ số cũ!"
        if water_new < water_old:
            return False, "Chỉ số nước mới phải lớn hơn hoặc bằng chỉ số cũ!"

        # Recalculate total
        electric_cost = (electric_new - electric_old) * inv["electric_price"]
        water_cost = (water_new - water_old) * inv["water_price"]
        total = inv["room_price"] + electric_cost + water_cost + inv["other_fees"]

        conn.execute(
            """UPDATE invoices SET electric_new=?, water_new=?,
               total=?, meter_updated=1, user_meter_submitted=1 WHERE id=?""",
            (electric_new, water_new, total, invoice_id)
        )
        conn.commit()
        return True, "Cập nhật chỉ số điện nước thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_invoice_admin(invoice_id, electric_old, electric_new, water_old, water_new,
                         electric_price, water_price, room_price, other_fees, other_fees_note):
    """Admin full update — can edit all fields of an unpaid invoice."""
    conn = get_connection()
    try:
        inv = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if not inv:
            return False, "Không tìm thấy hóa đơn!"
        if inv["status"] == "paid":
            return False, "Hóa đơn đã thanh toán, không thể cập nhật!"

        if electric_new < electric_old:
            return False, "Chỉ số điện mới phải lớn hơn hoặc bằng chỉ số cũ!"
        if water_new < water_old:
            return False, "Chỉ số nước mới phải lớn hơn hoặc bằng chỉ số cũ!"

        electric_cost = (electric_new - electric_old) * electric_price
        water_cost = (water_new - water_old) * water_price
        total = room_price + electric_cost + water_cost + other_fees

        meter_updated = 1 if (electric_new > 0 or water_new > 0) else 0

        conn.execute(
            """UPDATE invoices SET electric_old=?, electric_new=?, water_old=?, water_new=?,
               electric_price=?, water_price=?, room_price=?, other_fees=?, other_fees_note=?,
               total=?, meter_updated=? WHERE id=?""",
            (electric_old, electric_new, water_old, water_new,
             electric_price, water_price, room_price, other_fees, other_fees_note,
             total, meter_updated, invoice_id)
        )
        conn.commit()
        return True, "Cập nhật hóa đơn thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_monthly_revenue(year=None):
    """Get monthly revenue data for charts."""
    conn = get_connection()
    if not year:
        year = datetime.now().year
    rows = conn.execute("""
        SELECT month, SUM(total) as revenue, COUNT(*) as invoice_count
        FROM invoices
        WHERE year = ? AND status = 'paid'
        GROUP BY month
        ORDER BY month
    """, (year,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unpaid_count():
    """Get count of unpaid invoices."""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM invoices WHERE status = 'unpaid'").fetchone()
    conn.close()
    return row["cnt"]


def get_total_revenue_this_month():
    """Get total revenue for the current month."""
    now = datetime.now()
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(total), 0) as revenue FROM invoices WHERE month = ? AND year = ? AND status = 'paid'",
        (now.month, now.year)
    ).fetchone()
    conn.close()
    return row["revenue"]
