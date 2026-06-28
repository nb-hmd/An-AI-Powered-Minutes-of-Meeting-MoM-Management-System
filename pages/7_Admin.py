"""
⚙️ Admin Panel
User management, activity logs, system stats, and database backup.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.auth_service import AuthService
from models.user import UserModel
from models.mom import MoMModel
from models.action_item import ActionItemModel
from models.activity_log import ActivityLogModel
from services.export_service import ExportService
from services.mom_service import MoMService
from utils.formatters import format_datetime, format_role
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require admin access
AuthService.require_admin()
apply_theme()
show_sidebar()


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">⚙️ Admin Panel</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">Manage users, view logs, and system settings.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Tabs
# ============================================================
tab_users, tab_logs, tab_stats, tab_backup = st.tabs([
    "👥 Users", "📜 Activity Logs", "📊 System Stats", "💾 Backup"
])


# ---- Users Management ----
with tab_users:
    st.markdown("### 👥 User Management")

    users = UserModel.get_all_users()
    if users:
        user_df = pd.DataFrame([{
            "ID": u["id"],
            "Username": u["username"],
            "Email": u["email"],
            "Full Name": u.get("full_name", ""),
            "Role": format_role(u["role"]),
            "Active": "✅" if u.get("is_active", True) else "❌",
            "Created": format_datetime(u.get("created_at")),
        } for u in users])
        st.dataframe(user_df, use_container_width=True, hide_index=True)

    st.divider()

    # Change user role
    st.markdown("#### 🔄 Change User Role")
    if users:
        user_options = {u["username"]: u["id"] for u in users}
        selected_user = st.selectbox("Select User", list(user_options.keys()))
        new_role = st.selectbox("New Role", ["admin", "viewer"])
        if st.button("🔄 Update Role"):
            UserModel.update_user(user_options[selected_user], role=new_role)
            ActivityLogModel.log_activity(
                user_id=st.session_state.get("user_id"),
                username=st.session_state.get("username", ""),
                action="Role Changed",
                details=f"Changed {selected_user}'s role to {new_role}",
            )
            st.success(f"✅ {selected_user}'s role updated to {new_role}")
            st.rerun()

    st.divider()

    # Create new user
    st.markdown("#### ➕ Create New User")
    with st.form("admin_create_user"):
        nc1, nc2 = st.columns(2)
        with nc1:
            nu_username = st.text_input("Username")
            nu_email = st.text_input("Email")
            nu_role = st.selectbox("Role", ["viewer", "admin"], key="new_user_role")
        with nc2:
            nu_fullname = st.text_input("Full Name")
            nu_password = st.text_input("Password", type="password")

        if st.form_submit_button("➕ Create User", use_container_width=True):
            if nu_username and nu_email and nu_password:
                result = AuthService.register(nu_username, nu_email, nu_password, nu_password, nu_fullname)
                if result["success"]:
                    if nu_role == "admin":
                        user = UserModel.get_user_by_username(nu_username)
                        if user:
                            UserModel.update_user(user["id"], role="admin")
                    st.success(f"✅ User '{nu_username}' created!")
                    st.rerun()
                else:
                    st.error(result["message"])
            else:
                st.error("All fields are required.")

    st.divider()

    # Deactivate user
    st.markdown("#### 🚫 Deactivate User")
    if users:
        deact_user = st.selectbox("Select user to deactivate",
                                   [u["username"] for u in users if u["username"] != "admin"],
                                   key="deactivate_user")
        if st.button("🚫 Deactivate"):
            u = UserModel.get_user_by_username(deact_user)
            if u:
                UserModel.update_user(u["id"], is_active=False)
                st.success(f"User '{deact_user}' deactivated.")
                st.rerun()


# ---- Activity Logs ----
with tab_logs:
    st.markdown("### 📜 Activity Logs")

    # Filters
    fc1, fc2 = st.columns(2)
    with fc1:
        log_limit = st.selectbox("Show last", [25, 50, 100, 200], index=1)
    with fc2:
        log_filter = st.text_input("Filter by action", placeholder="e.g., Login, MoM Created")

    logs = ActivityLogModel.get_recent_logs(log_limit)
    if log_filter:
        logs = [l for l in logs if log_filter.lower() in l.get("action", "").lower()]

    if logs:
        log_df = pd.DataFrame([{
            "Timestamp": format_datetime(l.get("timestamp")),
            "User": l.get("username", ""),
            "Action": l.get("action", ""),
            "Details": l.get("details", ""),
            "IP": l.get("ip_address", ""),
        } for l in logs])
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity logs found.")


# ---- System Stats ----
with tab_stats:
    st.markdown("### 📊 System Statistics")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        total_users = len(UserModel.get_all_users())
        st.metric("Total Users", total_users)
    with sc2:
        total_moms = MoMModel.get_total_count()
        st.metric("Total MoMs", total_moms)
    with sc3:
        total_actions = ActionItemModel.get_pending_count() + ActionItemModel.get_completed_count()
        st.metric("Total Action Items", total_actions)

    sc4, sc5, sc6 = st.columns(3)
    with sc4:
        st.metric("Pending Actions", ActionItemModel.get_pending_count())
    with sc5:
        st.metric("Completed Actions", ActionItemModel.get_completed_count())
    with sc6:
        st.metric("This Month Meetings", MoMModel.get_this_month_count())


# ---- Backup ----
with tab_backup:
    st.markdown("### 💾 Database Backup & Bulk Export")

    st.markdown("Export all MoMs as a ZIP file containing PDFs, DOCX files, and metadata.")

    if st.button("📦 Export All MoMs as ZIP", use_container_width=True):
        with st.spinner("Generating export..."):
            all_moms = MoMModel.get_all_moms(page=1, per_page=9999)
            if all_moms:
                full_moms = []
                for m in all_moms:
                    detail = MoMService.get_mom_detail(m["id"])
                    if detail:
                        full_moms.append(detail)

                zip_buffer = ExportService.generate_bulk_zip(
                    full_moms, user_id=st.session_state.get("user_id")
                )
                st.download_button(
                    "⬇️ Download ZIP", zip_buffer,
                    file_name=f"mom_export_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                    mime="application/zip",
                )
                st.success(f"✅ Generated export with {len(full_moms)} MoMs.")
            else:
                st.info("No MoMs to export.")
