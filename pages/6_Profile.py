"""
👤 User Profile Page
Display user info, change password, upload profile picture, activity history.
"""

import streamlit as st
import pandas as pd
from services.auth_service import AuthService
from models.user import UserModel
from models.activity_log import ActivityLogModel
from utils.formatters import format_datetime, format_role
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">👤 User Profile</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">Manage your account settings.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Get Current User Data
# ============================================================
user_id = st.session_state.get("user_id")
user = UserModel.get_user_by_id(user_id)

if not user:
    st.error("User data not found.")
    st.stop()


# ============================================================
# Profile Tabs
# ============================================================
tab_info, tab_password, tab_picture, tab_activity = st.tabs([
    "📋 Info", "🔑 Change Password", "🖼️ Profile Picture", "📜 Activity"
])


# ---- User Info ----
with tab_info:
    st.markdown("### 📋 Your Information")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Username:** {user['username']}")
        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Full Name:** {user.get('full_name', 'N/A')}")
    with col2:
        st.markdown(f"**Role:** {format_role(user['role'])}")
        st.markdown(f"**Account Created:** {format_datetime(user.get('created_at'))}")
        st.markdown(f"**Last Updated:** {format_datetime(user.get('updated_at'))}")

    st.divider()

    # Update profile
    st.markdown("### ✏️ Update Profile")
    with st.form("update_profile"):
        new_fullname = st.text_input("Full Name", value=user.get("full_name", ""))
        new_email = st.text_input("Email", value=user.get("email", ""))

        if st.form_submit_button("💾 Save Changes", use_container_width=True):
            updates = {}
            if new_fullname.strip() != user.get("full_name", ""):
                updates["full_name"] = new_fullname.strip()
            if new_email.strip() != user.get("email", ""):
                updates["email"] = new_email.strip()

            if updates:
                result = UserModel.update_user(user_id, **updates)
                if result:
                    if "full_name" in updates:
                        st.session_state["full_name"] = updates["full_name"]
                    st.success("✅ Profile updated!")
                    st.rerun()
                else:
                    st.error("Failed to update profile.")
            else:
                st.info("No changes detected.")


# ---- Change Password ----
with tab_password:
    st.markdown("### 🔑 Change Password")
    with st.form("change_password"):
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("🔑 Change Password", use_container_width=True):
            if not current_pw or not new_pw or not confirm_pw:
                st.error("All fields are required.")
            elif new_pw != confirm_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                # Verify current password
                full_user = UserModel.get_user_by_username(user["username"])
                if AuthService.verify_password(current_pw, full_user["password_hash"]):
                    new_hash = AuthService.hash_password(new_pw)
                    success = UserModel.update_password(user_id, new_hash)
                    if success:
                        ActivityLogModel.log_activity(
                            user_id=user_id,
                            username=user["username"],
                            action="Password Changed",
                            details="User changed their password.",
                        )
                        st.success("✅ Password changed successfully!")
                    else:
                        st.error("Failed to change password.")
                else:
                    st.error("Current password is incorrect.")


# ---- Profile Picture ----
with tab_picture:
    st.markdown("### 🖼️ Profile Picture")

    current_pic = user.get("profile_picture")
    if current_pic:
        try:
            st.image(current_pic, width=150)
        except Exception:
            st.info("No profile picture set.")
    else:
        st.info("No profile picture set.")

    uploaded_pic = st.file_uploader("Upload new picture", type=["jpg", "jpeg", "png"])
    if uploaded_pic:
        from utils.file_handler import save_file
        file_info = save_file(uploaded_pic, subfolder=f"profiles/{user_id}")
        UserModel.update_user(user_id, profile_picture=file_info["file_path"])
        st.success("✅ Profile picture uploaded!")
        st.rerun()


# ---- Activity History ----
with tab_activity:
    st.markdown("### 📜 Your Activity History")

    logs = ActivityLogModel.get_logs_by_user(user_id, limit=50)
    if logs:
        log_df = pd.DataFrame([{
            "Time": format_datetime(l.get("timestamp")),
            "Action": l.get("action", ""),
            "Details": l.get("details", ""),
        } for l in logs])
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")
