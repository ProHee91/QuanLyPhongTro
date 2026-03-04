import streamlit as st
from backend.auth_service import authenticate


def render_login():
    """Render the login page. Returns True if logged in."""
    # Center the login form
    st.markdown("""
    <style>
        .login-container {
            max-width: 420px;
            margin: 60px auto;
            padding: 40px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }
        .login-header {
            text-align: center;
            font-size: 42px;
            margin-bottom: 8px;
        }
        .login-title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #a78bfa 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }
        .login-subtitle {
            text-align: center;
            color: #8888aa;
            font-size: 14px;
            margin-bottom: 32px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-header">🏠</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Quản Lý Phòng Trọ</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Đăng nhập để tiếp tục</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Tên đăng nhập", placeholder="Nhập tên đăng nhập")
            password = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            submitted = st.form_submit_button("🔐 Đăng nhập", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ thông tin!")
                else:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.user_role = user["role"]
                        st.session_state.user_id = user["id"]
                        st.success(f"Chào mừng, {user['display_name']}!")
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")

        st.markdown("---")
