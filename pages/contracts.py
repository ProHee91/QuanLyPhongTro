import streamlit as st
import pandas as pd
from backend.contract_service import get_all_contracts, create_contract, cancel_contract, expire_contract
from backend.room_service import get_available_rooms
from backend.tenant_service import get_tenants_without_contract
from utils.helpers import format_currency, status_badge_contract
from datetime import date


def render():
    st.markdown('<p class="main-header">📝 Quản Lý Hợp Đồng</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Tạo và quản lý hợp đồng thuê phòng</p>', unsafe_allow_html=True)

    tab_list, tab_add = st.tabs(["📋 Danh sách hợp đồng", "➕ Tạo hợp đồng mới"])

    with tab_add:
        st.subheader("Tạo hợp đồng mới")

        available_rooms = get_available_rooms()
        available_tenants = get_tenants_without_contract()

        if not available_rooms:
            st.warning("⚠️ Không có phòng trống! Vui lòng thêm phòng trước.")
        elif not available_tenants:
            st.warning("⚠️ Không có khách thuê khả dụng! Vui lòng thêm khách thuê trước.")
        else:
            with st.form("add_contract_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    room_options = {f"{r['room_number']} — {format_currency(r['price'])}/tháng": r["id"] for r in available_rooms}
                    selected_room = st.selectbox("Chọn phòng *", list(room_options.keys()))

                    start_date = st.date_input("Ngày bắt đầu *", value=date.today())
                    end_date = st.date_input("Ngày kết thúc", value=None)

                with col2:
                    tenant_options = {f"{t['name']} — {t['phone']}": t["id"] for t in available_tenants}
                    selected_tenant = st.selectbox("Chọn khách thuê *", list(tenant_options.keys()))

                    deposit = st.number_input("Tiền đặt cọc (VNĐ)", min_value=0, value=0, step=100000)

                submitted = st.form_submit_button("💾 Tạo hợp đồng", use_container_width=True)
                if submitted:
                    room_id = room_options[selected_room]
                    tenant_id = tenant_options[selected_tenant]
                    start_str = start_date.strftime("%Y-%m-%d")
                    end_str = end_date.strftime("%Y-%m-%d") if end_date else ""

                    success, msg = create_contract(room_id, tenant_id, start_str, end_str, deposit)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        col_filter, col_spacer = st.columns([1, 3])
        with col_filter:
            status_filter = st.selectbox(
                "Lọc trạng thái",
                ["Tất cả", "Đang hiệu lực", "Hết hạn", "Đã hủy"],
                key="contract_filter"
            )

        contracts = get_all_contracts(status_filter)

        if contracts:
            for contract in contracts:
                status_text, status_color = status_badge_contract(contract["status"])
                with st.expander(
                    f"**Phòng {contract['room_number']}** — {contract['tenant_name']} — {status_text}"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Phòng:** {contract['room_number']}")
                        st.markdown(f"**Giá phòng:** {format_currency(contract['room_price'])}")
                        st.markdown(f"**Tiền cọc:** {format_currency(contract['deposit'])}")
                    with col2:
                        st.markdown(f"**Khách thuê:** {contract['tenant_name']}")
                        st.markdown(f"**SĐT:** {contract['tenant_phone']}")
                        st.markdown(f"**Trạng thái:** {status_text}")
                    with col3:
                        st.markdown(f"**Ngày bắt đầu:** {contract['start_date']}")
                        st.markdown(f"**Ngày kết thúc:** {contract['end_date'] or '—'}")

                    if contract["status"] == "active":
                        st.markdown("---")
                        col_btn1, col_btn2, col_spacer = st.columns([1, 1, 2])
                        with col_btn1:
                            if st.button("⏰ Kết thúc HĐ", key=f"expire_{contract['id']}"):
                                success, msg = expire_contract(contract["id"])
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        with col_btn2:
                            if st.button("❌ Hủy HĐ", key=f"cancel_{contract['id']}"):
                                success, msg = cancel_contract(contract["id"])
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
        else:
            st.info("Chưa có hợp đồng nào. Hãy tạo hợp đồng mới!")
