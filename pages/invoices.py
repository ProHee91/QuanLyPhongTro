import streamlit as st
import pandas as pd
from backend.invoice_service import get_all_invoices, create_invoice, pay_invoice, get_invoice_by_id, update_invoice_admin, delete_invoice
from backend.contract_service import get_active_contracts
from utils.helpers import format_currency, status_badge_invoice
from datetime import datetime


def render():
    st.markdown('<p class="main-header">💰 Hóa Đơn &amp; Thanh Toán</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Quản lý hóa đơn tiền phòng, điện, nước</p>', unsafe_allow_html=True)

    tab_list, tab_add = st.tabs(["📋 Danh sách hóa đơn", "➕ Tạo hóa đơn mới"])

    with tab_add:
        st.subheader("Tạo hóa đơn mới")
        st.info("💡 Chỉ số điện/nước sẽ để trống. Khách thuê sẽ tự nhập chỉ số khi nhận hóa đơn.")

        active_contracts = get_active_contracts()
        if not active_contracts:
            st.warning("⚠️ Không có hợp đồng đang hiệu lực!")
        else:
            with st.form("add_invoice_form", clear_on_submit=True):
                # Contract selection
                contract_options = {
                    f"Phòng {c['room_number']} — {c['tenant_name']}": c for c in active_contracts
                }
                selected_key = st.selectbox("Chọn hợp đồng *", list(contract_options.keys()))
                selected_contract = contract_options[selected_key]

                col1, col2 = st.columns(2)
                with col1:
                    now = datetime.now()
                    month = st.number_input("Tháng", min_value=1, max_value=12, value=now.month)
                    year = st.number_input("Năm", min_value=2020, max_value=2030, value=now.year)
                    room_price = st.number_input(
                        "Tiền phòng (VNĐ)",
                        min_value=0,
                        value=int(selected_contract["room_price"]),
                        step=100000
                    )

                with col2:
                    electric_price = st.number_input("Giá điện (VNĐ/kWh)", min_value=0, value=3500, step=100)
                    water_price = st.number_input("Giá nước (VNĐ/m³)", min_value=0, value=15000, step=1000)

                st.markdown("---")
                other_fees = st.number_input("Phí khác (VNĐ)", min_value=0, value=0, step=10000)
                other_fees_note = st.text_input("Ghi chú phí khác", placeholder="VD: Phí internet, rác, giữ xe...")

                # Preview (only room + other fees since meter not set yet)
                st.markdown("---")
                st.markdown("**💵 Tổng tạm tính (chưa bao gồm điện nước):**")
                pcol1, pcol2 = st.columns(2)
                with pcol1:
                    st.metric("Tiền phòng", format_currency(room_price))
                with pcol2:
                    st.metric("Phí khác", format_currency(other_fees))

                submitted = st.form_submit_button("💾 Tạo hóa đơn", use_container_width=True)
                if submitted:
                    # Create with zero meter readings — tenant will fill in later
                    success, msg = create_invoice(
                        selected_contract["id"], month, year,
                        0, 0, 0, 0,
                        electric_price, water_price, room_price,
                        other_fees, other_fees_note
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        # Filters
        col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1])
        now = datetime.now()
        with col_f1:
            filter_month = st.selectbox(
                "Tháng", [None] + list(range(1, 13)),
                format_func=lambda x: "Tất cả" if x is None else f"Tháng {x}",
                index=0,
                key="inv_month"
            )
        with col_f2:
            filter_year = st.selectbox(
                "Năm", [None] + list(range(2020, 2031)),
                format_func=lambda x: "Tất cả" if x is None else str(x),
                index=0,
                key="inv_year"
            )
        with col_f3:
            filter_status = st.selectbox(
                "Trạng thái",
                ["Tất cả", "Chưa thanh toán", "Đã thanh toán"],
                key="inv_status"
            )

        invoices = get_all_invoices(filter_month, filter_year, filter_status)

        if invoices:
            for inv in invoices:
                status_text, status_color = status_badge_invoice(inv["status"])
                meter_filled = inv.get("meter_updated", 0)
                meter_badge = "✅ Đã nhập" if meter_filled else "⏳ Chờ nhập"
                electric_used = inv["electric_new"] - inv["electric_old"]
                water_used = inv["water_new"] - inv["water_old"]

                with st.expander(
                    f"**Phòng {inv['room_number']}** — T{inv['month']}/{inv['year']} — "
                    f"{format_currency(inv['total'])} — {status_text} — Điện/Nước: {meter_badge}"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Phòng:** {inv['room_number']}")
                        st.markdown(f"**Khách thuê:** {inv['tenant_name']}")
                        st.markdown(f"**Kỳ:** Tháng {inv['month']}/{inv['year']}")
                    with col2:
                        st.markdown(f"**Tiền phòng:** {format_currency(inv['room_price'])}")
                        if meter_filled:
                            st.markdown(f"**Tiền điện:** {format_currency(electric_used * inv['electric_price'])} ({electric_used:.0f} kWh × {format_currency(inv['electric_price'])})")
                            st.markdown(f"**Tiền nước:** {format_currency(water_used * inv['water_price'])} ({water_used:.0f} m³ × {format_currency(inv['water_price'])})")
                        else:
                            st.markdown(f"**Tiền điện:** ⏳ *Chờ khách nhập chỉ số*")
                            st.markdown(f"**Tiền nước:** ⏳ *Chờ khách nhập chỉ số*")
                    with col3:
                        if inv["other_fees"] > 0:
                            st.markdown(f"**Phí khác:** {format_currency(inv['other_fees'])}")
                            if inv["other_fees_note"]:
                                st.markdown(f"*({inv['other_fees_note']})*")
                        st.markdown(f"### 🧾 {format_currency(inv['total'])}")
                        st.markdown(f"**Trạng thái:** {status_text}")
                        if not meter_filled:
                            st.markdown("⚠️ *Tổng chưa chính xác — chờ chỉ số*")
                        if inv["paid_at"]:
                            st.markdown(f"**Ngày TT:** {inv['paid_at']}")

                    # ─── Admin Actions ────────────────────────────
                    st.markdown("---")
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if inv["status"] == "unpaid" and meter_filled:
                            if st.button("✅ Xác nhận thanh toán", key=f"pay_{inv['id']}"):
                                success, msg = pay_invoice(inv["id"])
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        elif inv["status"] == "unpaid" and not meter_filled:
                            st.warning("⏳ Chưa thể thanh toán — chờ nhập chỉ số điện nước.")
                    with col_act2:
                        if st.button("🗑️ Xóa hóa đơn", key=f"del_{inv['id']}", type="primary"):
                            success, msg = delete_invoice(inv["id"])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    if inv["status"] == "unpaid":

                        # ─── Admin Full Edit Form ─────────────────
                        with st.form(f"admin_edit_{inv['id']}"):
                            st.subheader("✏️ Cập nhật hóa đơn")

                            ae_col1, ae_col2 = st.columns(2)
                            with ae_col1:
                                ae_eold = st.number_input(
                                    "Chỉ số điện cũ (kWh)", min_value=0.0,
                                    value=float(inv["electric_old"]), step=1.0,
                                    key=f"ae_eo_{inv['id']}"
                                )
                                ae_enew = st.number_input(
                                    "Chỉ số điện mới (kWh)", min_value=0.0,
                                    value=float(inv["electric_new"]), step=1.0,
                                    key=f"ae_en_{inv['id']}"
                                )
                                ae_eprice = st.number_input(
                                    "Giá điện (VNĐ/kWh)", min_value=0,
                                    value=int(inv["electric_price"]), step=100,
                                    key=f"ae_ep_{inv['id']}"
                                )

                            with ae_col2:
                                ae_wold = st.number_input(
                                    "Chỉ số nước cũ (m³)", min_value=0.0,
                                    value=float(inv["water_old"]), step=1.0,
                                    key=f"ae_wo_{inv['id']}"
                                )
                                ae_wnew = st.number_input(
                                    "Chỉ số nước mới (m³)", min_value=0.0,
                                    value=float(inv["water_new"]), step=1.0,
                                    key=f"ae_wn_{inv['id']}"
                                )
                                ae_wprice = st.number_input(
                                    "Giá nước (VNĐ/m³)", min_value=0,
                                    value=int(inv["water_price"]), step=1000,
                                    key=f"ae_wp_{inv['id']}"
                                )

                            ae_room = st.number_input(
                                "Tiền phòng (VNĐ)", min_value=0,
                                value=int(inv["room_price"]), step=100000,
                                key=f"ae_rp_{inv['id']}"
                            )
                            ae_other = st.number_input(
                                "Phí khác (VNĐ)", min_value=0,
                                value=int(inv["other_fees"]), step=10000,
                                key=f"ae_of_{inv['id']}"
                            )
                            ae_note = st.text_input(
                                "Ghi chú phí khác",
                                value=inv["other_fees_note"] or "",
                                key=f"ae_on_{inv['id']}"
                            )

                            # Preview
                            ae_ecost = max(0, (ae_enew - ae_eold)) * ae_eprice
                            ae_wcost = max(0, (ae_wnew - ae_wold)) * ae_wprice
                            ae_total = ae_room + ae_ecost + ae_wcost + ae_other

                            st.markdown("---")
                            tp1, tp2, tp3, tp4 = st.columns(4)
                            with tp1:
                                st.metric("Tiền phòng", format_currency(ae_room))
                            with tp2:
                                st.metric("Tiền điện", format_currency(ae_ecost))
                            with tp3:
                                st.metric("Tiền nước", format_currency(ae_wcost))
                            with tp4:
                                st.metric("🧾 TỔNG CỘNG", format_currency(ae_total))

                            ae_submit = st.form_submit_button("💾 Lưu cập nhật", use_container_width=True)
                            if ae_submit:
                                success, msg = update_invoice_admin(
                                    inv["id"],
                                    ae_eold, ae_enew, ae_wold, ae_wnew,
                                    ae_eprice, ae_wprice, ae_room,
                                    ae_other, ae_note
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
        else:
            st.info("Chưa có hóa đơn nào. Hãy tạo hóa đơn mới!")
