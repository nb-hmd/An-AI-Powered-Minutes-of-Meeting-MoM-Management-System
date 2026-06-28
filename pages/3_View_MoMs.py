"""
📋 View MoMs Page
Displays all Minutes of Meeting in table format with
pagination, sorting, filtering, detail view, edit, and delete.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from services.auth_service import AuthService
from services.mom_service import MoMService
from models.mom import MoMModel
from models.action_item import ActionItemModel
from models.attendee import AttendeeModel
from models.attachment import AttachmentModel
from utils.formatters import format_datetime, format_status, truncate_text
from utils.constants import MEETING_CATEGORIES, ACTION_STATUSES, ALLOWED_FILE_TYPES
from services.ai_service import AIService
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
<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">📋 Minutes of Meeting</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">View, edit, and manage all your meeting records.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Session State for View Mode
# ============================================================
if "view_mom_id" not in st.session_state:
    st.session_state.view_mom_id = None
if "edit_mom_id" not in st.session_state:
    st.session_state.edit_mom_id = None


# ============================================================
# DETAIL VIEW
# ============================================================
def show_detail_view(mom_id):
    """Display detailed view of a single MoM."""
    mom = MoMService.get_mom_detail(mom_id)
    if not mom:
        st.error("MoM not found.")
        return

    # Back button
    if st.button("⬅️ Back to List"):
        st.session_state.view_mom_id = None
        st.session_state.edit_mom_id = None
        st.rerun()

    # Title & metadata
    st.markdown(f"## {mom['title']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"📅 **Date:** {format_datetime(mom['date_time'])}")
        st.markdown(f"📍 **Venue:** {mom.get('venue', 'N/A')}")
    with col2:
        st.markdown(f"📁 **Category:** {mom.get('category', 'N/A')}")
        st.markdown(f"🏢 **Department:** {mom.get('department', 'N/A')}")
    with col3:
        st.markdown(f"👤 **Created by:** {mom.get('creator_name', 'N/A')}")
        st.markdown(f"🕐 **Created:** {format_datetime(mom.get('created_at'))}")

    st.divider()

    # Content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Content", "👥 Attendees", "🎯 Action Items", "📎 Attachments"])

    with tab1:
        st.markdown("### 📋 Agenda")
        st.markdown(mom.get("agenda") or "_No agenda recorded_")
        st.markdown("### 💬 Discussion")
        st.markdown(mom.get("discussion") or "_No discussion recorded_")
        st.markdown("### ✅ Decisions")
        st.markdown(mom.get("decisions") or "_No decisions recorded_")

    with tab2:
        attendees = mom.get("attendees", [])
        if attendees:
            att_df = pd.DataFrame(attendees)
            att_df = att_df[["name", "role", "email", "department"]]
            st.dataframe(att_df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendees recorded.")

    with tab3:
        actions = mom.get("action_items", [])
        if actions:
            for item in actions:
                ic1, ic2, ic3, ic4 = st.columns([4, 2, 2, 2])
                with ic1:
                    st.markdown(f"**{item['description']}**")
                with ic2:
                    st.markdown(f"👤 {item.get('assigned_to', 'Unassigned')}")
                with ic3:
                    deadline = item.get("deadline")
                    st.markdown(f"📅 {deadline}" if deadline else "📅 No deadline")
                with ic4:
                    new_status = st.selectbox(
                        "Status", ACTION_STATUSES,
                        index=ACTION_STATUSES.index(item["status"]),
                        key=f"status_{item['id']}"
                    )
                    if new_status != item["status"]:
                        ActionItemModel.update_action_item_status(item["id"], new_status)
                        st.rerun()
        else:
            st.info("No action items recorded.")

    with tab4:
        attachments = mom.get("attachments", [])
        if attachments:
            for att in attachments:
                fcol1, fcol2, fcol3 = st.columns([4, 2, 1])
                with fcol1:
                    st.markdown(f"📄 **{att['filename']}** ({att.get('file_type', '').upper()})")
                with fcol2:
                    size_kb = (att.get("file_size", 0) or 0) / 1024
                    st.markdown(f"{size_kb:.1f} KB")
                with fcol3:
                    try:
                        with open(att["file_path"], "rb") as f:
                            st.download_button("⬇️", f.read(), file_name=att["filename"],
                                             key=f"dl_{att['id']}")
                    except FileNotFoundError:
                        st.markdown("_File missing_")

            # Delete attachment
            if AuthService.is_admin():
                st.divider()
                del_att_id = st.selectbox("Select attachment to delete",
                                          options=[a["id"] for a in attachments],
                                          format_func=lambda x: next(
                                              a["filename"] for a in attachments if a["id"] == x))
                if st.button("🗑️ Delete Attachment"):
                    MoMService.delete_attachment(del_att_id, st.session_state.get("user_id"))
                    st.success("Attachment deleted.")
                    st.rerun()
        else:
            st.info("No attachments.")

    st.divider()

    # Action buttons
    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        if st.button("✏️ Edit this MoM", use_container_width=True):
            st.session_state.edit_mom_id = mom_id
            st.session_state.view_mom_id = None
            st.rerun()
    with bcol2:
        if st.button("🗑️ Delete this MoM", use_container_width=True):
            result = MoMService.delete_mom(mom_id, st.session_state.get("user_id"))
            if result["success"]:
                st.success(result["message"])
                st.session_state.view_mom_id = None
                st.rerun()
            else:
                st.error(result["message"])


# ============================================================
# EDIT VIEW
# ============================================================
def show_edit_view(mom_id):
    """Display edit form for a MoM."""
    mom = MoMService.get_mom_detail(mom_id)
    if not mom:
        st.error("MoM not found.")
        return

    if st.button("⬅️ Back to List"):
        st.session_state.edit_mom_id = None
        st.rerun()

    st.markdown(f"## ✏️ Editing: {mom['title']}")

    with st.form("edit_mom_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *", value=mom["title"])
            dt = mom["date_time"]
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            meeting_date = st.date_input("Date", value=dt.date() if dt else date.today())
            venue = st.text_input("Venue", value=mom.get("venue", ""))
        with col2:
            category = st.selectbox("Category", MEETING_CATEGORIES,
                                    index=MEETING_CATEGORIES.index(mom["category"])
                                    if mom.get("category") in MEETING_CATEGORIES else 0)
            meeting_time = st.time_input("Time", value=dt.time() if dt else time(10, 0))
            department = st.text_input("Department", value=mom.get("department", ""))

        agenda = st.text_area("Agenda", value=mom.get("agenda", ""), height=100)
        discussion = st.text_area("Discussion", value=mom.get("discussion", ""), height=150)
        decisions = st.text_area("Decisions", value=mom.get("decisions", ""), height=100)

        # Attendees
        st.markdown("### 👥 Attendees")
        existing_att = mom.get("attendees", [])
        att_count = max(len(existing_att), 1)
        attendees_data = []
        for i in range(att_count):
            ea = existing_att[i] if i < len(existing_att) else {}
            ac1, ac2, ac3, ac4 = st.columns(4)
            with ac1:
                a_name = st.text_input("Name", value=ea.get("name", ""), key=f"ea_name_{i}")
            with ac2:
                a_role = st.text_input("Role", value=ea.get("role", ""), key=f"ea_role_{i}")
            with ac3:
                a_email = st.text_input("Email", value=ea.get("email", ""), key=f"ea_email_{i}")
            with ac4:
                a_dept = st.text_input("Dept", value=ea.get("department", ""), key=f"ea_dept_{i}")
            attendees_data.append({"name": a_name, "role": a_role, "email": a_email, "department": a_dept})

        # Action Items
        st.markdown("### 🎯 Action Items")
        existing_ai = mom.get("action_items", [])
        ai_count = max(len(existing_ai), 1)
        action_items_data = []
        for i in range(ai_count):
            ei = existing_ai[i] if i < len(existing_ai) else {}
            ic1, ic2, ic3, ic4 = st.columns([3, 2, 2, 1])
            with ic1:
                ai_desc = st.text_input("Description", value=ei.get("description", ""), key=f"eai_desc_{i}")
            with ic2:
                ai_assigned = st.text_input("Assigned To", value=ei.get("assigned_to", ""), key=f"eai_assigned_{i}")
            with ic3:
                ai_deadline = st.date_input("Deadline", value=ei.get("deadline"), key=f"eai_deadline_{i}")
            with ic4:
                ai_status = st.selectbox("Status", ACTION_STATUSES,
                                          index=ACTION_STATUSES.index(ei["status"]) if ei.get("status") in ACTION_STATUSES else 0,
                                          key=f"eai_status_{i}")
            action_items_data.append({
                "description": ai_desc, "assigned_to": ai_assigned,
                "deadline": ai_deadline, "status": ai_status
            })

        # New attachments
        st.markdown("### 📎 Add New Attachments")
        new_files = st.file_uploader("Upload", type=ALLOWED_FILE_TYPES,
                                     accept_multiple_files=True, key="edit_files")

        # Submit buttons
        edit_btn1, edit_btn2 = st.columns(2)
        with edit_btn1:
            quality_check = st.form_submit_button("🔍 AI Quality Check", use_container_width=True)
        with edit_btn2:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

        # F17: Quality Check on edit
        if quality_check:
            valid_ai_check = [a for a in action_items_data if a["description"].strip()]
            with st.spinner("🔍 Running AI quality check..."):
                qc_result = AIService.quality_check(
                    agenda=agenda.strip(),
                    discussion=discussion.strip(),
                    decisions=decisions.strip(),
                    action_items=valid_ai_check,
                    user_id=st.session_state.get("user_id"),
                )
            if qc_result["success"]:
                score = qc_result["score"]
                issues = qc_result["issues"]
                score_color = "green" if score >= 80 else ("orange" if score >= 50 else "red")
                st.markdown(f"### Quality Score: :{score_color}[**{score}/100**]")
                if issues:
                    for issue in issues:
                        sev = issue['severity']
                        icon = "⚠️" if sev == "warning" else ("❌" if sev == "error" else "ℹ️")
                        st.markdown(f"{icon} **{issue['field']}**: {issue['message']}")
                    st.info("💡 You can dismiss these and save anyway.")
                else:
                    st.success("🎉 No issues found! MoM looks great.")
            else:
                st.error(f"Quality check failed: {qc_result['message']}")

        if submitted:
            # Run full validation (is_new=False skips past-date check for edits)
            from utils.validators import validate_mom_form
            validation_errors = validate_mom_form(
                title=title,
                meeting_date=meeting_date,
                agenda=agenda,
                action_items=action_items_data,
                uploaded_files=new_files if new_files else None,
                is_new=False,
            )

            if validation_errors:
                st.error(f"❌ **{len(validation_errors)} validation error(s) found.** Please fix before saving:")
                for err in validation_errors:
                    st.markdown(
                        f'<div style="padding:0.4rem 0.8rem; margin-bottom:0.3rem; '
                        f'border-left:3px solid #e53e3e; background:#fed7d7; '
                        f'border-radius:0 8px 8px 0; font-size:0.9rem;">'
                        f'❌ <strong>{err["field"]}</strong>: {err["message"]}</div>',
                        unsafe_allow_html=True
                    )
            else:
                meeting_datetime = datetime.combine(meeting_date, meeting_time)
                valid_att = [a for a in attendees_data if a["name"].strip()]
                valid_ai = [a for a in action_items_data if a["description"].strip()]

                result = MoMService.update_mom(
                    mom_id=mom_id,
                    user_id=st.session_state.get("user_id"),
                    title=title.strip(), date_time=meeting_datetime,
                    venue=venue.strip(), agenda=agenda.strip(),
                    discussion=discussion.strip(), decisions=decisions.strip(),
                    category=category, department=department.strip(),
                    attendees=valid_att, action_items=valid_ai,
                    uploaded_files=new_files if new_files else None,
                )
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.session_state.edit_mom_id = None
                    st.session_state.view_mom_id = mom_id
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")


# ============================================================
# LIST VIEW (Main)
# ============================================================
def show_list_view():
    """Display paginated list of all MoMs."""
    # Filters
    with st.expander("🔧 Filters & Sorting", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sort_by = st.selectbox("Sort by", ["date_time", "title", "created_at"])
        with fc2:
            sort_order = st.selectbox("Order", ["DESC", "ASC"])
        with fc3:
            per_page = st.selectbox("Per page", [5, 10, 20, 50], index=1)

    # Pagination
    total = MoMModel.get_total_count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    moms = MoMModel.get_all_moms(
        page=st.session_state.current_page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Stats bar
    st.markdown(f"**Total Meetings:** {total} | **Page:** {st.session_state.current_page}/{total_pages}")

    if not moms:
        st.info("📭 No meetings found. Create your first MoM!")
        return

    # Display as cards
    for mom in moms:
        with st.container():
            mc1, mc2, mc3 = st.columns([5, 3, 2])
            with mc1:
                st.markdown(f"### {mom['title']}")
                st.markdown(f"📅 {format_datetime(mom['date_time'])} | 📍 {mom.get('venue', 'N/A')}")
            with mc2:
                st.markdown(f"📁 {mom.get('category', 'N/A')} | 🏢 {mom.get('department', 'N/A')}")
                st.markdown(f"👤 {mom.get('creator_name', 'N/A')}")
            with mc3:
                if st.button("👁️ View", key=f"view_{mom['id']}"):
                    st.session_state.view_mom_id = mom["id"]
                    st.rerun()
                if st.button("✏️ Edit", key=f"edit_{mom['id']}"):
                    st.session_state.edit_mom_id = mom["id"]
                    st.rerun()
            st.divider()

    # Pagination controls
    pc1, pc2, pc3 = st.columns([1, 2, 1])
    with pc1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_page <= 1):
            st.session_state.current_page -= 1
            st.rerun()
    with pc2:
        st.markdown(f"<div style='text-align:center'>Page {st.session_state.current_page} of {total_pages}</div>",
                    unsafe_allow_html=True)
    with pc3:
        if st.button("➡️ Next", disabled=st.session_state.current_page >= total_pages):
            st.session_state.current_page += 1
            st.rerun()


# ============================================================
# Page Router
# ============================================================
if st.session_state.edit_mom_id:
    show_edit_view(st.session_state.edit_mom_id)
elif st.session_state.view_mom_id:
    show_detail_view(st.session_state.view_mom_id)
else:
    show_list_view()
