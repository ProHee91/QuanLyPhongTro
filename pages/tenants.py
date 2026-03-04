import streamlit as st
import pandas as pd
from backend.tenant_service import get_all_tenants, create_tenant, update_tenant, delete_tenant
from datetime import date


def render():
    st.markdown('<p class="main-header">👥 Quản Lý Khách Thuê</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Quản lý thông tin khách thuê phòng trọ</p>', unsafe_allow_html=True)

    tab_list, tab_add = st.tabs(["📋 Danh sách khách thuê", "➕ Thêm khách mới"])

    with tab_add:
        st.subheader("Thêm khách thuê mới")
        with st.form("add_tenant_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Họ và tên *", placeholder="VD: Nguyễn Văn A")
                phone = st.text_input("Số điện thoại *", placeholder="VD: 0901234567")
                email = st.text_input("Email", placeholder="VD: email@example.com")
                id_card = st.text_input("CCCD/CMND", placeholder="VD: 012345678901")
            with col2:
                gender = st.selectbox("Giới tính", ["", "Nam", "Nữ"])
                dob = st.date_input("Ngày sinh", value=None, min_value=date(1950, 1, 1), max_value=date.today())
                address = st.text_area("Địa chỉ thường trú", placeholder="VD: 123 Đường ABC, Quận XYZ, TP.HCM")

            submitted = st.form_submit_button("💾 Thêm khách thuê", use_container_width=True)
            if submitted:
                if not name or not phone:
                    st.error("Vui lòng nhập họ tên và số điện thoại!")
                else:
                    dob_str = dob.strftime("%Y-%m-%d") if dob else ""
                    success, msg = create_tenant(name, phone, email, id_card, gender, dob_str, address)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        # Search
        search = st.text_input("🔍 Tìm kiếm theo tên hoặc SĐT", placeholder="Nhập tên hoặc số điện thoại...", key="tenant_search")

        tenants = get_all_tenants(search if search else None)

        if tenants:
            # Summary table
            df = pd.DataFrame(tenants)
            display_df = df[["name", "phone", "email", "id_card", "gender"]].copy()
            display_df.columns = ["Họ tên", "SĐT", "Email", "CCCD", "Giới tính"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Chi tiết & Chỉnh sửa")

            for tenant in tenants:
                with st.expander(f"**{tenant['name']}** — {tenant['phone']}"):
                    with st.form(f"edit_tenant_{tenant['id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Họ tên", value=tenant["name"], key=f"tn_{tenant['id']}")
                            new_phone = st.text_input("SĐT", value=tenant["phone"], key=f"tp_{tenant['id']}")
                            new_email = st.text_input("Email", value=tenant["email"] or "", key=f"te_{tenant['id']}")
                            new_id_card = st.text_input("CCCD", value=tenant["id_card"] or "", key=f"ti_{tenant['id']}")
                        with col2:
                            gender_options = ["", "Nam", "Nữ"]
                            current_gender = tenant["gender"] if tenant["gender"] in gender_options else ""
                            new_gender = st.selectbox(
                                "Giới tính",
                                gender_options,
                                index=gender_options.index(current_gender),
                                key=f"tg_{tenant['id']}"
                            )
                            dob_val = None
                            if tenant["date_of_birth"]:
                                try:
                                    dob_val = date.fromisoformat(tenant["date_of_birth"])
                                except ValueError:
                                    dob_val = None
                            new_dob = st.date_input(
                                "Ngày sinh", value=dob_val,
                                min_value=date(1950, 1, 1), max_value=date.today(),
                                key=f"td_{tenant['id']}"
                            )
                            new_address = st.text_area("Địa chỉ", value=tenant["address"] or "", key=f"ta_{tenant['id']}")

                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            save = st.form_submit_button("💾 Lưu thay đổi", use_container_width=True)
                        with bcol2:
                            remove = st.form_submit_button("🗑️ Xóa khách", use_container_width=True)

                        if save:
                            dob_str = new_dob.strftime("%Y-%m-%d") if new_dob else ""
                            success, msg = update_tenant(
                                tenant["id"], new_name, new_phone, new_email,
                                new_id_card, new_gender, dob_str, new_address
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        if remove:
                            success, msg = delete_tenant(tenant["id"])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Chưa có khách thuê nào. Hãy thêm khách mới!")
