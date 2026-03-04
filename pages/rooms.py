import streamlit as st
import pandas as pd
from backend.room_service import get_all_rooms, create_room, update_room, delete_room
from utils.helpers import format_currency, status_badge_room


def render():
    st.markdown('<p class="main-header">🏢 Quản Lý Phòng</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Thêm, sửa, xóa và quản lý trạng thái phòng trọ</p>', unsafe_allow_html=True)

    # Tabs
    tab_list, tab_add = st.tabs(["📋 Danh sách phòng", "➕ Thêm phòng mới"])

    with tab_add:
        st.subheader("Thêm phòng mới")
        with st.form("add_room_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                room_number = st.text_input("Số phòng *", placeholder="VD: P101")
                floor = st.number_input("Tầng", min_value=1, max_value=50, value=1)
                area = st.number_input("Diện tích (m²)", min_value=0.0, value=20.0, step=0.5)
            with col2:
                price = st.number_input("Giá thuê (VNĐ/tháng) *", min_value=0, value=2000000, step=100000)
                status = st.selectbox("Trạng thái", ["Trống", "Bảo trì"])
                description = st.text_area("Mô tả", placeholder="VD: Phòng có ban công, máy lạnh...")

            submitted = st.form_submit_button("💾 Thêm phòng", use_container_width=True)
            if submitted:
                if not room_number:
                    st.error("Vui lòng nhập số phòng!")
                else:
                    status_map = {"Trống": "available", "Bảo trì": "maintenance"}
                    success, msg = create_room(
                        room_number, floor, area, price,
                        status_map.get(status, "available"), description
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        # Filter
        col_filter, col_spacer = st.columns([1, 3])
        with col_filter:
            status_filter = st.selectbox(
                "Lọc trạng thái",
                ["Tất cả", "Trống", "Đang thuê", "Bảo trì"],
                key="room_filter"
            )

        rooms = get_all_rooms(status_filter)

        if rooms:
            # Display as styled cards
            for room in rooms:
                status_text, status_color = status_badge_room(room["status"])
                with st.expander(f"**{room['room_number']}** — {status_text} — {format_currency(room['price'])}/tháng"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Tầng:** {room['floor']}")
                        st.markdown(f"**Diện tích:** {room['area']} m²")
                    with col2:
                        st.markdown(f"**Giá thuê:** {format_currency(room['price'])}")
                        st.markdown(f"**Trạng thái:** {status_text}")
                    with col3:
                        st.markdown(f"**Mô tả:** {room['description'] or '—'}")

                    st.markdown("---")

                    # Edit form
                    with st.form(f"edit_room_{room['id']}"):
                        st.markdown("**✏️ Chỉnh sửa thông tin phòng**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_number = st.text_input("Số phòng", value=room["room_number"], key=f"rn_{room['id']}")
                            new_floor = st.number_input("Tầng", value=room["floor"], min_value=1, key=f"rf_{room['id']}")
                            new_area = st.number_input("Diện tích (m²)", value=float(room["area"]), min_value=0.0, step=0.5, key=f"ra_{room['id']}")
                        with ec2:
                            new_price = st.number_input("Giá thuê", value=int(room["price"]), min_value=0, step=100000, key=f"rp_{room['id']}")
                            status_options = ["available", "occupied", "maintenance"]
                            status_labels = {"available": "Trống", "occupied": "Đang thuê", "maintenance": "Bảo trì"}
                            current_idx = status_options.index(room["status"]) if room["status"] in status_options else 0
                            new_status = st.selectbox(
                                "Trạng thái",
                                status_options,
                                index=current_idx,
                                format_func=lambda x: status_labels.get(x, x),
                                key=f"rs_{room['id']}"
                            )
                            new_desc = st.text_area("Mô tả", value=room["description"] or "", key=f"rd_{room['id']}")

                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            save = st.form_submit_button("💾 Lưu thay đổi", use_container_width=True)
                        with bcol2:
                            remove = st.form_submit_button("🗑️ Xóa phòng", use_container_width=True)

                        if save:
                            success, msg = update_room(
                                room["id"], new_number, new_floor, new_area, new_price, new_status, new_desc
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        if remove:
                            success, msg = delete_room(room["id"])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Chưa có phòng nào. Hãy thêm phòng mới!")
