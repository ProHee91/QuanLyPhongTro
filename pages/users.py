import streamlit as st
from backend.auth_service import get_all_users, create_user, update_user, delete_user
from backend.tenant_service import get_all_tenants


def render():
    """Render user management page (admin only)."""
    st.markdown('<p class="main-header">👤 Quản Lý Tài Khoản</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Tạo và quản lý tài khoản người dùng</p>', unsafe_allow_html=True)

    tab_list, tab_add = st.tabs(["📋 Danh sách tài khoản", "➕ Tạo tài khoản mới"])

    with tab_add:
        st.subheader("Tạo tài khoản mới")
        tenants = get_all_tenants()

        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Tên đăng nhập *", placeholder="VD: nguyenvana")
                password = st.text_input("Mật khẩu *", type="password", placeholder="Tối thiểu 4 ký tự")
                display_name = st.text_input("Tên hiển thị *", placeholder="VD: Nguyễn Văn A")
            with col2:
                role = st.selectbox("Vai trò", ["user", "admin"], format_func=lambda x: "Quản trị viên" if x == "admin" else "Khách thuê")
                tenant_options = {"— Không liên kết —": None}
                tenant_options.update({f"{t['name']} — {t['phone']}": t["id"] for t in tenants})
                selected_tenant = st.selectbox(
                    "Liên kết khách thuê (cho role User)",
                    list(tenant_options.keys())
                )

            submitted = st.form_submit_button("💾 Tạo tài khoản", use_container_width=True)
            if submitted:
                if not username or not password or not display_name:
                    st.error("Vui lòng nhập đầy đủ thông tin!")
                elif len(password) < 4:
                    st.error("Mật khẩu phải có ít nhất 4 ký tự!")
                else:
                    tenant_id = tenant_options[selected_tenant]
                    success, msg = create_user(username, password, display_name, role, tenant_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        users = get_all_users()
        if users:
            for user in users:
                role_badge = "🔑 Admin" if user["role"] == "admin" else "👤 User"
                tenant_info = f" — Liên kết: {user['tenant_name']}" if user.get("tenant_name") else ""
                with st.expander(f"**{user['username']}** — {user['display_name']} — {role_badge}{tenant_info}"):
                    tenants = get_all_tenants()
                    with st.form(f"edit_user_{user['id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Tên đăng nhập", value=user["username"], disabled=True, key=f"uu_{user['id']}")
                            new_display = st.text_input("Tên hiển thị", value=user["display_name"], key=f"ud_{user['id']}")
                            new_password = st.text_input("Mật khẩu mới (để trống nếu không đổi)", type="password", key=f"up_{user['id']}")
                        with col2:
                            role_options = ["admin", "user"]
                            new_role = st.selectbox(
                                "Vai trò",
                                role_options,
                                index=role_options.index(user["role"]),
                                format_func=lambda x: "Quản trị viên" if x == "admin" else "Khách thuê",
                                key=f"ur_{user['id']}"
                            )
                            tenant_opts = {"— Không liên kết —": None}
                            tenant_opts.update({f"{t['name']} — {t['phone']}": t["id"] for t in tenants})
                            current_tenant_key = "— Không liên kết —"
                            for k, v in tenant_opts.items():
                                if v == user["tenant_id"]:
                                    current_tenant_key = k
                                    break
                            new_tenant = st.selectbox(
                                "Liên kết khách thuê",
                                list(tenant_opts.keys()),
                                index=list(tenant_opts.keys()).index(current_tenant_key),
                                key=f"ut_{user['id']}"
                            )

                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            save = st.form_submit_button("💾 Lưu thay đổi", use_container_width=True)
                        with bcol2:
                            remove = st.form_submit_button("🗑️ Xóa tài khoản", use_container_width=True)

                        if save:
                            tid = tenant_opts[new_tenant]
                            pwd = new_password if new_password else None
                            success, msg = update_user(user["id"], new_display, new_role, tid, pwd)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        if remove:
                            if user["id"] == st.session_state.user_id:
                                st.error("Không thể xóa tài khoản đang đăng nhập!")
                            else:
                                success, msg = delete_user(user["id"])
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
        else:
            st.info("Chưa có tài khoản nào.")
