"""
Shared Sidebar Component
Renders the custom sidebar on every authenticated page.
Import and call show_sidebar() at the top of each page file.
"""

import streamlit as st
from config.settings import APP_VERSION
from services.auth_service import AuthService


def show_sidebar():
    """
    Render the full custom sidebar (navigation, user info, theme toggle, logout).
    Call this after apply_theme() and AuthService.require_auth() on every page.
    """
    # ── Collapse the hidden stSidebarNav empty space at the top ──────────
    st.markdown("""
    <style>
    /* Remove the empty top gap left by the hidden auto-nav */
    [data-testid="stSidebarNav"] { display: none !important; height: 0 !important; }
    [data-testid="stSidebarNavItems"] { display: none !important; height: 0 !important; }
    [data-testid="stSidebarNavSeparator"] { display: none !important; height: 0 !important; }
    div[data-testid="stSidebarUserContent"] { padding-top: 0 !important; margin-top: 0 !important; }
    section[data-testid="stSidebar"] > div { padding-top: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # ── Logo / App title ──────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding:0.6rem 0 0.4rem;">
            <div style="font-size:2rem;">📝</div>
            <div style="font-size:1.15rem; font-weight:700; margin-top:0.15rem;">
                MoM System
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<div style='text-align:center; font-size:0.72rem; opacity:0.55;"
            f"margin-bottom:0.6rem;'>v{APP_VERSION}</div>",
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Logged-in user info ───────────────────────────────────────────
        current_user = st.session_state.get("full_name", "User")
        current_role = st.session_state.get("user_role", "viewer")
        role_icon = "👑" if current_role == "admin" else "👁️"

        st.markdown(f"""
        <div style="padding:0.65rem 0.8rem; background:rgba(102,126,234,0.12);
                    border-radius:10px; margin-bottom:0.7rem;
                    border:1px solid rgba(102,126,234,0.2);">
            <div style="font-size:0.88rem; font-weight:600;">👤 {current_user}</div>
            <div style="font-size:0.75rem; opacity:0.7; margin-top:0.12rem;">
                {role_icon} {current_role.capitalize()}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Navigation links (actual Unicode emoji in labels) ─────────────
        st.markdown("### 🧭 Navigation")

        st.page_link("app.py",                   label="🏠 Home")
        st.page_link("pages/1_Dashboard.py",      label="📊 Dashboard")
        st.page_link("pages/2_Create_MoM.py",     label="➕ Create MoM")
        st.page_link("pages/3_View_MoMs.py",      label="📋 View MoMs")
        st.page_link("pages/4_Search.py",         label="🔍 Search")
        st.page_link("pages/5_Templates.py",      label="📝 Templates")
        st.page_link("pages/8_Action_Tracker.py", label="🎯 Action Tracker")
        st.page_link("pages/9_Live_Recording.py", label="🎙️ Live Recording")
        st.page_link("pages/6_Profile.py",        label="👤 Profile")

        if AuthService.is_admin():
            st.page_link("pages/7_Admin.py",      label="⚙️ Admin Panel")

        st.divider()

        # ── Theme toggle ──────────────────────────────────────────────────
        st.markdown("### 🎨 Theme")
        dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.get("dark_mode", True),
            key="sidebar_dark_toggle",
        )
        if dark_mode != st.session_state.get("dark_mode", True):
            st.session_state.dark_mode = dark_mode
            st.rerun()

        st.divider()

        # ── Logout ────────────────────────────────────────────────────────
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            AuthService.logout()
            st.rerun()
