def format_currency(amount):
    """Format a number as Vietnamese currency."""
    if amount is None:
        return "0 ₫"
    return f"{amount:,.0f} ₫"


def format_date(date_str):
    """Format a date string for display."""
    if not date_str:
        return "—"
    return date_str


def status_badge_room(status):
    """Get display text and color for room status."""
    mapping = {
        "available": ("🟢 Trống", "green"),
        "occupied": ("🔴 Đang thuê", "red"),
        "maintenance": ("🟡 Bảo trì", "orange"),
    }
    return mapping.get(status, ("❓ Không rõ", "gray"))


def status_badge_contract(status):
    """Get display text and color for contract status."""
    mapping = {
        "active": ("✅ Đang hiệu lực", "green"),
        "expired": ("⏰ Hết hạn", "orange"),
        "cancelled": ("❌ Đã hủy", "red"),
    }
    return mapping.get(status, ("❓ Không rõ", "gray"))


def status_badge_invoice(status):
    """Get display text and color for invoice status."""
    mapping = {
        "unpaid": ("🔴 Chưa thanh toán", "red"),
        "paid": ("🟢 Đã thanh toán", "green"),
    }
    return mapping.get(status, ("❓ Không rõ", "gray"))
