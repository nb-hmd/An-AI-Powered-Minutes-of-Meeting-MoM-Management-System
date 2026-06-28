"""
📝 Templates Page
Manage meeting templates — view, use, create, edit, delete.
"""

import streamlit as st
import json
from services.auth_service import AuthService
from config.database import get_cursor
from models.activity_log import ActivityLogModel
from utils.constants import MEETING_CATEGORIES
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()


# ============================================================
# Template DB Operations
# ============================================================
class TemplateModel:
    @staticmethod
    def get_all_templates():
        query = "SELECT * FROM templates ORDER BY created_at DESC"
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception:
            return []

    @staticmethod
    def get_template_by_id(template_id):
        query = "SELECT * FROM templates WHERE id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (template_id,))
                return cur.fetchone()
        except Exception:
            return None

    @staticmethod
    def create_template(name, category, content, created_by=None):
        query = """
            INSERT INTO templates (name, category, content, created_by)
            VALUES (%s, %s, %s::jsonb, %s) RETURNING *
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (name, category, json.dumps(content), created_by))
                return cur.fetchone()
        except Exception as e:
            print(f"Error creating template: {e}")
            return None

    @staticmethod
    def update_template(template_id, name, category, content):
        query = """
            UPDATE templates SET name=%s, category=%s, content=%s::jsonb, updated_at=CURRENT_TIMESTAMP
            WHERE id=%s RETURNING *
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (name, category, json.dumps(content), template_id))
                return cur.fetchone()
        except Exception:
            return None

    @staticmethod
    def delete_template(template_id):
        query = "DELETE FROM templates WHERE id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (template_id,))
                return True
        except Exception:
            return False


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">📝 Meeting Templates</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">Use templates to quickly create meetings.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Tab Layout
# ============================================================
tab_view, tab_create = st.tabs(["📋 Available Templates", "➕ Create Template"])


# ---- View Templates ----
with tab_view:
    templates = TemplateModel.get_all_templates()
    if not templates:
        st.info("No templates available. Create one to get started!")
    else:
        for tmpl in templates:
            content = tmpl["content"] if isinstance(tmpl["content"], dict) else json.loads(tmpl["content"])
            with st.expander(f"📄 {tmpl['name']} — {tmpl.get('category', 'General')}", expanded=False):
                st.markdown(f"**Category:** {tmpl.get('category', 'N/A')}")

                if content.get("agenda"):
                    st.markdown(f"**Agenda:**\n{content['agenda']}")
                if content.get("default_roles"):
                    st.markdown(f"**Default Roles:** {', '.join(content['default_roles'])}")

                bcol1, bcol2, bcol3 = st.columns(3)
                with bcol1:
                    if st.button("📋 Use Template", key=f"use_{tmpl['id']}"):
                        st.session_state["template_data"] = content
                        st.session_state["template_name"] = tmpl["name"]
                        ActivityLogModel.log_activity(
                            user_id=st.session_state.get("user_id"),
                            username=st.session_state.get("username", ""),
                            action="Template Used",
                            details=f"Used template: {tmpl['name']}",
                        )
                        st.success(f"✅ Template '{tmpl['name']}' loaded! Go to **Create MoM** page.")

                if AuthService.is_admin():
                    with bcol2:
                        if st.button("✏️ Edit", key=f"edit_tmpl_{tmpl['id']}"):
                            st.session_state["editing_template_id"] = tmpl["id"]
                            st.rerun()
                    with bcol3:
                        if st.button("🗑️ Delete", key=f"del_tmpl_{tmpl['id']}"):
                            TemplateModel.delete_template(tmpl["id"])
                            st.success("Template deleted.")
                            st.rerun()

    # Edit template inline
    if AuthService.is_admin() and st.session_state.get("editing_template_id"):
        tid = st.session_state["editing_template_id"]
        tmpl = TemplateModel.get_template_by_id(tid)
        if tmpl:
            st.markdown("---")
            st.markdown(f"### ✏️ Editing: {tmpl['name']}")
            content = tmpl["content"] if isinstance(tmpl["content"], dict) else json.loads(tmpl["content"])
            with st.form("edit_template_form"):
                e_name = st.text_input("Template Name", value=tmpl["name"])
                e_cat = st.selectbox("Category", MEETING_CATEGORIES,
                                     index=MEETING_CATEGORIES.index(tmpl["category"])
                                     if tmpl.get("category") in MEETING_CATEGORIES else 0)
                e_agenda = st.text_area("Default Agenda", value=content.get("agenda", ""))
                e_roles = st.text_input("Default Roles (comma separated)",
                                        value=", ".join(content.get("default_roles", [])))
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    new_content = {
                        "agenda": e_agenda,
                        "discussion": content.get("discussion", ""),
                        "decisions": content.get("decisions", ""),
                        "default_roles": [r.strip() for r in e_roles.split(",") if r.strip()],
                    }
                    TemplateModel.update_template(tid, e_name, e_cat, new_content)
                    st.session_state.pop("editing_template_id", None)
                    st.success("✅ Template updated!")
                    st.rerun()


# ---- Create Template (Admin only) ----
with tab_create:
    if not AuthService.is_admin():
        st.warning("Only admins can create templates.")
    else:
        with st.form("create_template_form"):
            t_name = st.text_input("Template Name *", placeholder="e.g., Sprint Review Meeting")
            t_cat = st.selectbox("Category", MEETING_CATEGORIES)
            t_agenda = st.text_area("Default Agenda", height=100,
                                    placeholder="1. Item one\n2. Item two")
            t_roles = st.text_input("Default Roles (comma separated)",
                                    placeholder="e.g., Team Lead, Developer, QA")

            if st.form_submit_button("💾 Create Template", use_container_width=True):
                if not t_name.strip():
                    st.error("Template name is required.")
                else:
                    content = {
                        "agenda": t_agenda.strip(),
                        "discussion": "",
                        "decisions": "",
                        "default_roles": [r.strip() for r in t_roles.split(",") if r.strip()],
                    }
                    result = TemplateModel.create_template(
                        name=t_name.strip(), category=t_cat,
                        content=content,
                        created_by=st.session_state.get("user_id"),
                    )
                    if result:
                        st.success(f"✅ Template '{t_name}' created!")
                        st.rerun()
                    else:
                        st.error("Failed to create template.")
