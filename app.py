import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="Quản Lý Phòng Trọ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for premium dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e8e8ff !important;
    }

    /* Navigation buttons in sidebar */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        padding: 12px 20px;
        border: none;
        border-radius: 12px;
        background: transparent;
        color: #b8b8d0;
        font-size: 15px;
        font-weight: 500;
        transition: all 0.3s ease;
        margin-bottom: 4px;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        transform: translateX(4px);
    }

    /* KPI metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
    }

    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 15, 35, 0.5);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 500;
        color: #8888aa;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    }

    /* Form styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    /* Submit buttons */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 32px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
    }

    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        background: rgba(99, 102, 241, 0.05);
        font-weight: 500;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(99, 102, 241, 0.15);
    }

    /* Success/Error alerts */
    .stSuccess {
        border-radius: 12px;
        border-left: 4px solid #10b981;
    }

    .stError {
        border-radius: 12px;
        border-left: 4px solid #ef4444;
    }

    /* Header styling */
    .main-header {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a78bfa 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .sub-header {
        color: #8888aa;
        font-size: 16px;
        margin-bottom: 32px;
        font-weight: 400;
    }

    /* Card container */
    .card {
        background: rgba(15, 15, 35, 0.6);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(99, 102, 241, 0.1);
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(99, 102, 241, 0.1);
        margin: 24px 0;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ══════════════════════════════════════════════
       MOBILE & TABLET RESPONSIVE
       ══════════════════════════════════════════════ */

    /* Viewport & base mobile fixes */
    .main .block-container {
        max-width: 100% !important;
    }

    /* Touch-friendly inputs (always) */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea textarea {
        font-size: 16px !important;  /* Prevents iOS zoom on focus */
        min-height: 44px !important; /* Apple touch target guideline */
    }

    /* Touch-friendly buttons (always) */
    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 48px !important;
        font-size: 15px !important;
    }

    /* ─── Tablet (max-width: 1024px) ─── */
    @media (max-width: 1024px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        div[data-testid="stMetric"] {
            padding: 14px !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 24px !important;
        }

        .main-header {
            font-size: 28px;
        }

        .sub-header {
            font-size: 14px;
            margin-bottom: 20px;
        }
    }

    /* ─── Mobile (max-width: 768px) ─── */
    @media (max-width: 768px) {
        /* Reduce padding */
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
        }

        /* Stack columns vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Smaller headers */
        .main-header {
            font-size: 24px !important;
        }

        .sub-header {
            font-size: 13px;
            margin-bottom: 16px;
        }

        /* Compact metrics */
        div[data-testid="stMetric"] {
            padding: 12px !important;
            border-radius: 12px;
        }

        div[data-testid="stMetric"] label {
            font-size: 11px !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }

        /* Tabs responsive */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            padding: 4px;
            border-radius: 12px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 14px;
            font-size: 13px;
            white-space: nowrap;
        }

        /* Expander full width */
        .streamlit-expanderHeader {
            font-size: 13px !important;
            padding: 10px !important;
        }

        /* Bigger touch targets for buttons */
        .stButton > button {
            min-height: 48px !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
            border-radius: 10px !important;
        }

        .stFormSubmitButton > button {
            min-height: 52px !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            border-radius: 12px !important;
        }

        /* Form inputs larger for touch */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            padding: 12px !important;
            border-radius: 10px !important;
        }

        /* Sidebar overlay on mobile */
        section[data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 280px !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            padding: 14px 16px;
            font-size: 14px;
        }

        /* Card spacing */
        .card {
            padding: 16px;
            border-radius: 12px;
        }

        hr {
            margin: 16px 0;
        }
    }

    /* ─── Small phones (max-width: 480px) ─── */
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.3rem !important;
            padding-right: 0.3rem !important;
        }

        .main-header {
            font-size: 20px !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 18px !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px;
            font-size: 12px;
        }
    }
</style>

<!-- Mobile viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)


# ─── Authentication Gate ─────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    from pages.login import render_login
    render_login()
    st.stop()

# ─── User is logged in ──────────────────────────────────────
user = st.session_state.user
user_role = st.session_state.user_role

# Sidebar Navigation
with st.sidebar:
    st.markdown('<p class="main-header" style="font-size: 24px;">🏠 Phòng Trọ</p>', unsafe_allow_html=True)

    # User info badge
    role_label = "🔑 Admin" if user_role == "admin" else "👤 Khách thuê"
    st.markdown(
        f'<p style="color: #a5b4fc; font-size: 13px; margin-bottom: 4px;">Xin chào, <b>{user["display_name"]}</b></p>'
        f'<p style="color: #666; font-size: 11px; margin-bottom: 20px;">{role_label}</p>',
        unsafe_allow_html=True
    )
    st.divider()

    # ─── Build navigation based on role ──────────────────────
    if user_role == "admin":
        pages = {
            "📊 Tổng quan": "dashboard",
            "🏢 Quản lý phòng": "rooms",
            "👥 Quản lý khách thuê": "tenants",
            "📝 Quản lý hợp đồng": "contracts",
            "💰 Hóa đơn & Thanh toán": "invoices",
            "👤 Quản lý tài khoản": "users",
        }
        default_page = "dashboard"
    else:
        # User role: only see their own invoices + change password
        pages = {
            "💰 Hóa đơn của tôi": "my_invoices",
            "🔑 Đổi mật khẩu": "change_password",
        }
        default_page = "my_invoices"

    if "current_page" not in st.session_state:
        st.session_state.current_page = default_page

    # Reset page if user role changed or page not in allowed pages
    if st.session_state.current_page not in pages.values():
        st.session_state.current_page = default_page

    for label, page_key in pages.items():
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()

    st.divider()

    # Logout button
    if st.button("🚪 Đăng xuất", key="logout_btn", use_container_width=True):
        for key in ["logged_in", "user", "user_role", "user_id", "current_page"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown(
        '<p style="color: #555; font-size: 12px; text-align: center;">v2.0 • Quản Lý Phòng Trọ</p>',
        unsafe_allow_html=True
    )

# ─── Page Routing ────────────────────────────────────────────
page = st.session_state.current_page

if user_role == "admin":
    if page == "dashboard":
        from pages.dashboard import render
        render()
    elif page == "rooms":
        from pages.rooms import render
        render()
    elif page == "tenants":
        from pages.tenants import render
        render()
    elif page == "contracts":
        from pages.contracts import render
        render()
    elif page == "invoices":
        from pages.invoices import render
        render()
    elif page == "users":
        from pages.users import render
        render()
else:
    # User pages
    if page == "my_invoices":
        from pages.my_invoices import render
        render()
    elif page == "change_password":
        from pages.my_invoices import render_change_password
        render_change_password()
