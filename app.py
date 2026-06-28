# Force reload correct API key from .env
import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)  # override=True forces reload

import streamlit as st
from config.database import init_connection_pool
from config.settings import APP_NAME, APP_VERSION
from services.auth_service import AuthService
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Login Page CSS  (sidebar hidden, centered layout)
# ============================================================
def load_login_css():
    """CSS applied only on the login / register page."""
    st.markdown("""
    <style>
        /* Hide the Streamlit sidebar completely on login page */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }

        /* Make the main area take full width and centered */
        .main .block-container {
            max-width: 680px;
            margin: 0 auto;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        /* ── Form submit buttons (Login / Register) ─────────────────── */
        [data-testid="stFormSubmitButton"] > button,
        [data-testid="stFormSubmitButton"] > button:focus {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.6rem 1.5rem !important;
            width: 100% !important;
            transition: opacity 0.2s ease !important;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            opacity: 0.88 !important;
        }

        /* ── Password show/hide toggle button ───────────────────────── */
        button[data-testid="baseButton-secondary"],
        [data-testid="stTextInput"] button {
            background-color: #0f3460 !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 6px !important;
        }
        button[data-testid="baseButton-secondary"]:hover,
        [data-testid="stTextInput"] button:hover {
            background-color: #667eea !important;
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# Database Init (cached)
# ============================================================
@st.cache_resource
def initialize_database():
    return init_connection_pool()


# ============================================================
# Login Page
# ============================================================
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.2rem;">📝 MoM System</h1>
            <p style="color: #718096; font-size: 1.1rem;">Minutes of Meeting Management</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Login", "📋 Register"])

        with tab_login:
            st.markdown("#### Welcome Back!")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("🚀 Login", use_container_width=True)
                if submitted:
                    result = AuthService.login(username, password)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])

            st.markdown("""
            <div style="text-align: center; margin-top: 0.5rem;">
                <small style="color: #a0aec0;">Default: admin / admin123</small>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            st.markdown("#### Create an Account")
            with st.form("register_form", clear_on_submit=True):
                reg_fullname = st.text_input("📛 Full Name", placeholder="Enter your full name")
                reg_username = st.text_input("👤 Username", placeholder="Choose a username")
                reg_email = st.text_input("📧 Email", placeholder="Enter your email")
                reg_password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
                reg_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password")
                reg_submitted = st.form_submit_button("📋 Register", use_container_width=True)
                if reg_submitted:
                    result = AuthService.register(reg_username, reg_email, reg_password, reg_confirm, reg_fullname)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])


# ============================================================
# Main App (Authenticated)
# ============================================================
def show_main_app():
    # Render the shared custom sidebar (same on every page)
    show_sidebar()

    # ---- MAIN CONTENT ----
    full_name = st.session_state.get("full_name", "User")
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>👋 Welcome, {full_name}!</h2>
        <p>Manage your meetings efficiently with the Minutes of Meeting System.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats (live from database)
    st.markdown("### 📊 Quick Overview")
    try:
        from services.analytics_service import AnalyticsService
        stats = AnalyticsService.get_dashboard_stats()
    except Exception:
        stats = {"total_meetings": 0, "this_month": 0, "pending_actions": 0, "completed_actions": 0}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #667eea;">
            <div class="stat-number">{stats['total_meetings']}</div>
            <div class="stat-label">Total Meetings</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #48bb78;">
            <div class="stat-number">{stats['this_month']}</div>
            <div class="stat-label">This Month</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #ed8936;">
            <div class="stat-number">{stats['pending_actions']}</div>
            <div class="stat-label">Pending Actions</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #38a169;">
            <div class="stat-number">{stats['completed_actions']}</div>
            <div class="stat-label">Completed Actions</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Navigation Cards
    st.markdown("### 🚀 Quick Actions")
    qc1, qc2, qc3, qc4, qc5 = st.columns(5)
    with qc1:
        if st.button("➕ Create MoM", use_container_width=True):
            st.switch_page("pages/2_Create_MoM.py")
    with qc2:
        if st.button("📋 View MoMs", use_container_width=True):
            st.switch_page("pages/3_View_MoMs.py")
    with qc3:
        if st.button("🔍 Search", use_container_width=True):
            st.switch_page("pages/4_Search.py")
    with qc4:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with qc5:
        if st.button("🎙️ Live Recording", use_container_width=True):
            st.switch_page("pages/9_Live_Recording.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Getting Started
    st.markdown("### 📖 Getting Started")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("**📝 Create a Meeting**\n\nNavigate to **Create MoM** to record meeting minutes with agenda, attendees, and action items.")
        st.info("**🔍 Search Meetings**\n\nUse **Search** to find meetings by title, date, venue, or assigned person.")
    with col_b:
        st.info("**📋 View Meetings**\n\nGo to **View MoMs** to browse all meetings with sorting, filtering, and export.")
        st.info("**📊 Dashboard**\n\nCheck the **Dashboard** for analytics, charts, and KPI metrics.")

    st.success("**🎙️ Live Meeting Recording** *(New!)*\n\nHead to **Live Recording** to record a meeting in real-time, auto-transcribe it, and let AI fill in the entire MoM for you — including title, agenda, decisions, and action items with assigned persons and deadlines.")

    st.markdown(f"""
    <div class="footer">
        {APP_NAME} v{APP_VERSION} • Built with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# Main Entry Point
# ============================================================
def main():
    # Default dark mode to True before any CSS is applied
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True

    db_ready = initialize_database()

    if not db_ready:
        apply_theme()   # still apply theme so error page looks correct
        st.error("❌ Unable to connect to the database. Please check your configuration.")
        st.info("""
        **Troubleshooting:**
        1. Make sure PostgreSQL is running
        2. Check `.env` for correct database credentials
        3. Ensure `mom_system` database exists:
        
        ```
        psql -U postgres -c "CREATE DATABASE mom_system;"
        psql -U postgres -d mom_system -f database/schema.sql
        ```
        """)
        st.stop()

    if AuthService.is_authenticated():
        apply_theme()    # apply dark/light theme on home page
        show_main_app()
    else:
        apply_theme()      # apply background theme on login page too
        load_login_css()   # then hide sidebar + center layout
        show_login_page()


if __name__ == "__main__":
    main()
