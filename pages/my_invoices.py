import streamlit as st
import pandas as pd
from backend.invoice_service import get_all_invoices, update_meter_readings
from backend.auth_service import get_tenant_id_for_user, change_password
from utils.helpers import format_currency, status_badge_invoice
from datetime import datetime


def render():
    """Render tenant's own invoice view with meter reading input."""
    st.markdown('<p class="main-header">💰 Hóa Đơn Của Tôi</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Xem và cập nhật chỉ số điện nước hóa đơn phòng trọ</p>', unsafe_allow_html=True)

    user = st.session_state.get("user")
    if not user:
        st.error("Vui lòng đăng nhập!")
        return

    tenant_id = user.get("tenant_id")
    if not tenant_id:
        st.warning("⚠️ Tài khoản của bạn chưa được liên kết với khách thuê nào. Vui lòng liên hệ quản trị viên.")
        return

    # Get invoices linked to this tenant's contracts
    from database.db import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.*, c.room_id, c.tenant_id, r.room_number, t.name as tenant_name
        FROM invoices i
        JOIN contracts c ON i.contract_id = c.id
        JOIN rooms r ON c.room_id = r.id
        JOIN tenants t ON c.tenant_id = t.id
        WHERE c.tenant_id = ?
        ORDER BY i.year DESC, i.month DESC
    """, (tenant_id,)).fetchall()
    conn.close()
    invoices = [dict(r) for r in rows]

    if not invoices:
        st.info("Bạn chưa có hóa đơn nào.")
        return

    # Separate: user can update if user_meter_submitted=0 and unpaid
    pending_meter = [inv for inv in invoices if not inv.get("user_meter_submitted", 0) and inv["status"] == "unpaid"]
    other_invoices = [inv for inv in invoices if inv.get("user_meter_submitted", 0) or inv["status"] == "paid"]

    # Summary metrics
    total_unpaid = sum(inv["total"] for inv in invoices if inv["status"] == "unpaid")
    total_paid = sum(inv["total"] for inv in invoices if inv["status"] == "paid")
    pending_count = len(pending_meter)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Chờ nhập chỉ số", f"{pending_count} hóa đơn")
    with col2:
        st.metric("💸 Tổng nợ", format_currency(total_unpaid))
    with col3:
        st.metric("✅ Đã thanh toán", format_currency(total_paid))

    # ─── Pending Meter Input Section ─────────────────────────
    if pending_meter:
        st.markdown("---")
        st.subheader("📝 Hóa đơn cần nhập chỉ số điện/nước")
        st.info("💡 Vui lòng nhập chỉ số điện/nước cho các hóa đơn bên dưới. Tổng tiền sẽ được tự động tính lại sau khi bạn lưu.")

        for inv in pending_meter:
            with st.expander(
                f"⚡ Tháng {inv['month']}/{inv['year']} — **Phòng {inv['room_number']}** — ⏳ Chờ nhập chỉ số",
                expanded=True
            ):
                # Show current invoice info
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**Tiền phòng:** {format_currency(inv['room_price'])}")
                    st.markdown(f"**Giá điện:** {format_currency(inv['electric_price'])}/kWh")
                with col_info2:
                    st.markdown(f"**Giá nước:** {format_currency(inv['water_price'])}/m³")
                    if inv["other_fees"] > 0:
                        note = f" ({inv['other_fees_note']})" if inv["other_fees_note"] else ""
                        st.markdown(f"**Phí khác:** {format_currency(inv['other_fees'])}{note}")

                st.markdown("---")

                # Meter reading input form
                with st.form(f"meter_form_{inv['id']}"):
                    st.markdown("**📊 Nhập chỉ số điện nước**")
                    col_e, col_w = st.columns(2)
                    with col_e:
                        st.markdown(f"**Chỉ số điện cũ:** {inv['electric_old']:.0f} kWh")
                        e_new = st.number_input(
                            "Chỉ số điện mới (kWh)", min_value=0.0, value=float(inv["electric_new"]),
                            step=1.0, key=f"en_{inv['id']}"
                        )
                    with col_w:
                        st.markdown(f"**Chỉ số nước cũ:** {inv['water_old']:.0f} m³")
                        w_new = st.number_input(
                            "Chỉ số nước mới (m³)", min_value=0.0, value=float(inv["water_new"]),
                            step=1.0, key=f"wn_{inv['id']}"
                        )

                    # Live preview
                    e_old = inv["electric_old"]
                    w_old = inv["water_old"]
                    e_cost = max(0, (e_new - e_old)) * inv["electric_price"]
                    w_cost = max(0, (w_new - w_old)) * inv["water_price"]
                    est_total = inv["room_price"] + e_cost + w_cost + inv["other_fees"]

                    st.markdown("---")
                    p1, p2, p3, p4 = st.columns(4)
                    with p1:
                        st.metric("Tiền phòng", format_currency(inv["room_price"]))
                    with p2:
                        st.metric("Tiền điện", format_currency(e_cost))
                    with p3:
                        st.metric("Tiền nước", format_currency(w_cost))
                    with p4:
                        st.metric("🧾 TỔNG CỘNG", format_currency(est_total))

                    submitted = st.form_submit_button("💾 Lưu chỉ số điện nước", use_container_width=True)
                    if submitted:
                        success, msg = update_meter_readings(inv["id"], e_new, w_new)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ─── Completed Invoices Section ──────────────────────────
    if other_invoices:
        st.markdown("---")
        st.subheader("📋 Lịch sử hóa đơn")

        # Filter
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            filter_status = st.selectbox(
                "Trạng thái",
                ["Tất cả", "Chưa thanh toán", "Đã thanh toán"],
                key="my_inv_status"
            )

        if filter_status == "Chưa thanh toán":
            other_invoices = [inv for inv in other_invoices if inv["status"] == "unpaid"]
        elif filter_status == "Đã thanh toán":
            other_invoices = [inv for inv in other_invoices if inv["status"] == "paid"]

        for inv in other_invoices:
            status_text, _ = status_badge_invoice(inv["status"])
            electric_used = inv["electric_new"] - inv["electric_old"]
            water_used = inv["water_new"] - inv["water_old"]

            with st.expander(
                f"📄 Tháng {inv['month']}/{inv['year']} — **Phòng {inv['room_number']}** — "
                f"{format_currency(inv['total'])} — {status_text}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Phòng:** {inv['room_number']}")
                    st.markdown(f"**Kỳ:** Tháng {inv['month']}/{inv['year']}")
                    st.markdown(f"**Tiền phòng:** {format_currency(inv['room_price'])}")
                with col2:
                    st.markdown(f"**Tiền điện:** {format_currency(electric_used * inv['electric_price'])} ({electric_used:.0f} kWh)")
                    st.markdown(f"**Tiền nước:** {format_currency(water_used * inv['water_price'])} ({water_used:.0f} m³)")
                    if inv["other_fees"] > 0:
                        note = f" ({inv['other_fees_note']})" if inv["other_fees_note"] else ""
                        st.markdown(f"**Phí khác:** {format_currency(inv['other_fees'])}{note}")

                st.markdown(f"### 🧾 Tổng cộng: {format_currency(inv['total'])}")
                st.markdown(f"**Trạng thái:** {status_text}")
                if inv["paid_at"]:
                    st.markdown(f"**Ngày thanh toán:** {inv['paid_at']}")


def render_change_password():
    """Render password change form."""
    st.markdown('<p class="main-header">🔑 Đổi Mật Khẩu</p>', unsafe_allow_html=True)

    with st.form("change_password_form"):
        old_password = st.text_input("Mật khẩu cũ", type="password")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password")
        submitted = st.form_submit_button("💾 Đổi mật khẩu", use_container_width=True)

        if submitted:
            if not old_password or not new_password:
                st.error("Vui lòng nhập đầy đủ thông tin!")
            elif new_password != confirm_password:
                st.error("Mật khẩu mới không khớp!")
            elif len(new_password) < 4:
                st.error("Mật khẩu mới phải có ít nhất 4 ký tự!")
            else:
                success, msg = change_password(st.session_state.user_id, old_password, new_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
