"""
🎯 Action Item Tracker Page
Central tracker showing all action items across all meetings.
Supports filtering by person, deadline, and status.
Allows assignees to self-update their task status with comments.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from services.auth_service import AuthService
from services.action_tracker_service import ActionTrackerService
from models.action_item import ActionItemModel
from utils.formatters import format_datetime, format_status, format_date
from utils.constants import ACTION_STATUSES
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()


# ============================================================
# Custom CSS for this page  (theme-aware)
# ============================================================
_dark = st.session_state.get("dark_mode", True)
_card_bg  = "#16213e" if _dark else "#ffffff"
_text_col = "#e2e8f0" if _dark else "#2d3748"
_sub_col  = "#a0aec0" if _dark else "#718096"
_entry_bg = "#0f3460" if _dark else "#f7fafc"
_entry_border = "rgba(255,255,255,0.08)" if _dark else "#e2e8f0"
_form_bg  = "#16213e" if _dark else "#f7fafc"
_shadow   = "rgba(0,0,0,0.4)" if _dark else "rgba(0,0,0,0.08)"

st.markdown(f"""
<style>
    .tracker-banner {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
    }}
    .tracker-banner h2 {{ margin: 0; font-size: 1.6rem; font-weight: 700; }}
    .tracker-banner p {{ margin: 0.3rem 0 0; opacity: 0.85; font-size: 1rem; }}

    .kpi-card {{
        background: {_card_bg};
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px {_shadow};
        border-left: 4px solid;
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); }}
    .kpi-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {_text_col};
    }}
    .kpi-label {{
        font-size: 0.8rem;
        color: {_sub_col};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .overdue-row {{
        background: rgba(229, 62, 62, 0.08) !important;
        border-left: 3px solid #e53e3e;
    }}

    .status-badge {{
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .status-pending    {{ background: #fefcbf; color: #975a16; }}
    .status-in_progress {{ background: #bee3f8; color: #2a4365; }}
    .status-completed  {{ background: #c6f6d5; color: #276749; }}
    .status-overdue    {{ background: #fed7d7; color: #9b2c2c; }}

    .history-entry {{
        padding: 0.6rem 1rem;
        border-left: 3px solid #667eea;
        margin-bottom: 0.5rem;
        background: {_entry_bg};
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: {_text_col};
    }}

    .update-form-container {{
        background: {_form_bg};
        border: 1px solid {_entry_border};
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# Auto-flag overdue items on page load
# ============================================================
ActionTrackerService.auto_flag_overdue()


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div class="tracker-banner">
    <h2>🎯 Action Item Tracker</h2>
    <p>Central view of all action items across every meeting — filter, track, and update status.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI Cards
# ============================================================
stats = ActionTrackerService.get_tracker_stats()

kc1, kc2, kc3, kc4, kc5 = st.columns(5)

with kc1:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #667eea;">
        <div class="kpi-number">{stats['total']}</div>
        <div class="kpi-label">Total Items</div>
    </div>""", unsafe_allow_html=True)
with kc2:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #ecc94b;">
        <div class="kpi-number">{stats['pending']}</div>
        <div class="kpi-label">Pending</div>
    </div>""", unsafe_allow_html=True)
with kc3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #4299e1;">
        <div class="kpi-number">{stats['in_progress']}</div>
        <div class="kpi-label">In Progress</div>
    </div>""", unsafe_allow_html=True)
with kc4:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #48bb78;">
        <div class="kpi-number">{stats['completed']}</div>
        <div class="kpi-label">Completed</div>
    </div>""", unsafe_allow_html=True)
with kc5:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #e53e3e;">
        <div class="kpi-number">{stats['overdue']}</div>
        <div class="kpi-label">Overdue</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# Filters
# ============================================================
filter_options = ActionTrackerService.get_filter_options()
current_user_name = st.session_state.get("full_name", "")
is_admin = AuthService.is_admin()

with st.expander("🔧 Filters & Sorting", expanded=True):
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        # Person filter with "My Tasks" shortcut
        person_options = ["All Persons", f"📌 My Tasks ({current_user_name})"] + filter_options["persons"]
        person_filter = st.selectbox("👤 Filter by Person", person_options)

    with fc2:
        # Deadline filter
        deadline_labels = [opt[0] for opt in filter_options["deadline_options"]]
        deadline_values = [opt[1] for opt in filter_options["deadline_options"]]
        deadline_choice = st.selectbox("📅 Filter by Deadline", deadline_labels)
        deadline_filter = deadline_values[deadline_labels.index(deadline_choice)]

    with fc3:
        # Status filter
        status_display = {
            "pending": "⏳ Pending",
            "in_progress": "🔄 In Progress",
            "completed": "✅ Completed",
            "overdue": "🔴 Overdue",
        }
        status_options = list(status_display.keys())
        status_labels = list(status_display.values())
        selected_status_labels = st.multiselect(
            "📊 Filter by Status",
            status_labels,
            default=[],
            placeholder="All Statuses"
        )
        # Convert labels back to values
        selected_statuses = [k for k, v in status_display.items() if v in selected_status_labels]

    with fc4:
        sort_col = st.selectbox("🔃 Sort by", ["deadline", "status", "assigned_to", "created_at"])
        sort_dir = st.radio("Order", ["ASC", "DESC"], horizontal=True)


# ============================================================
# Build filters and fetch items
# ============================================================
assigned_val = None
if person_filter.startswith("📌 My Tasks"):
    assigned_val = current_user_name
elif person_filter != "All Persons":
    assigned_val = person_filter

status_val = selected_statuses if selected_statuses else None

items = ActionTrackerService.get_filtered_items(
    status_filter=status_val,
    assigned_filter=assigned_val,
    deadline_filter=deadline_filter,
    sort_by=sort_col,
    sort_order=sort_dir,
)


# ============================================================
# Results summary
# ============================================================
st.markdown(f"**Showing {len(items)} action item(s)**")

if not items:
    st.info("📭 No action items match your filters. Try adjusting the filters above.")
    st.stop()


# ============================================================
# Action Items Table
# ============================================================
# Session state for update form
if "update_item_id" not in st.session_state:
    st.session_state.update_item_id = None
if "show_history_id" not in st.session_state:
    st.session_state.show_history_id = None

for idx, item in enumerate(items):
    item_id = item["id"]
    is_overdue = item.get("status") == "overdue"
    deadline = item.get("deadline")
    assigned = item.get("assigned_to", "Unassigned") or "Unassigned"
    status = item.get("status", "pending")
    status_class = f"status-{status}"

    # Determine if current user can update this item
    can_update = is_admin or (current_user_name.strip().lower() == assigned.strip().lower())

    # Card container
    container_style = "border-left: 3px solid #e53e3e; background: rgba(229,62,62,0.04);" if is_overdue else ""

    st.markdown(f"""
    <div style="padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.3rem; {container_style}">
    </div>
    """, unsafe_allow_html=True)

    mc1, mc2, mc3, mc4, mc5 = st.columns([4, 2, 2, 2, 2])

    with mc1:
        st.markdown(f"**{item.get('description', 'No description')}**")
        st.caption(f"📋 {item.get('mom_title', 'Unknown Meeting')}")
        if item.get("status_comment"):
            st.caption(f"💬 _{item['status_comment']}_")

    with mc2:
        st.markdown(f"👤 **{assigned}**")

    with mc3:
        if deadline:
            deadline_str = format_date(deadline) if hasattr(deadline, 'strftime') else str(deadline)
            if is_overdue:
                st.markdown(f"📅 :red[**{deadline_str}**]")
            else:
                st.markdown(f"📅 {deadline_str}")
        else:
            st.markdown("📅 _No deadline_")

    with mc4:
        st.markdown(f'<span class="status-badge {status_class}">{format_status(status)}</span>',
                    unsafe_allow_html=True)

    with mc5:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if can_update:
                if st.button("✏️", key=f"upd_{item_id}", help="Update status"):
                    if st.session_state.update_item_id == item_id:
                        st.session_state.update_item_id = None
                    else:
                        st.session_state.update_item_id = item_id
                        st.session_state.show_history_id = None
                    st.rerun()
        with btn_col2:
            if st.button("📜", key=f"hist_{item_id}", help="View history"):
                if st.session_state.show_history_id == item_id:
                    st.session_state.show_history_id = None
                else:
                    st.session_state.show_history_id = item_id
                    st.session_state.update_item_id = None
                st.rerun()

    # ---- Inline Status Update Form (F14) ----
    if st.session_state.update_item_id == item_id:
        st.markdown('<div class="update-form-container">', unsafe_allow_html=True)
        st.markdown(f"#### ✏️ Update Status — _{item.get('description', '')[:60]}_")

        with st.form(f"status_form_{item_id}", clear_on_submit=True):
            uf1, uf2 = st.columns([1, 2])
            with uf1:
                # Only allow updating to standard statuses (not overdue directly)
                update_statuses = ["pending", "in_progress", "completed"]
                update_labels = ["⏳ Pending", "🔄 In Progress", "✅ Done"]
                current_idx = update_statuses.index(status) if status in update_statuses else 0
                new_status_label = st.selectbox(
                    "New Status",
                    update_labels,
                    index=current_idx,
                    key=f"ns_{item_id}"
                )
                new_status = update_statuses[update_labels.index(new_status_label)]

            with uf2:
                comment = st.text_area(
                    "Comment (optional)",
                    placeholder="Add a short note about this update...",
                    height=80,
                    key=f"comment_{item_id}"
                )

            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                submitted = st.form_submit_button("💾 Save Update", use_container_width=True)
            with sub_col2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            if submitted:
                result = ActionTrackerService.update_item_status(
                    item_id=item_id,
                    new_status=new_status,
                    comment=comment.strip(),
                    user_full_name=current_user_name,
                    user_id=st.session_state.get("user_id"),
                    is_admin=is_admin,
                )
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.session_state.update_item_id = None
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")

            if cancelled:
                st.session_state.update_item_id = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Status History View ----
    if st.session_state.show_history_id == item_id:
        history = ActionTrackerService.get_item_history(item_id)
        if history:
            st.markdown(f"#### 📜 Status History — _{item.get('description', '')[:60]}_")
            for entry in history:
                changed_at = format_datetime(entry.get("changed_at"))
                old_s = format_status(entry.get("old_status", "—"))
                new_s = format_status(entry.get("new_status", "—"))
                by = entry.get("changed_by", "Unknown")
                comment = entry.get("comment", "")

                st.markdown(f"""
                <div class="history-entry">
                    <strong>{changed_at}</strong> — by <em>{by}</em><br>
                    {old_s} → {new_s}
                    {f'<br>💬 <em>{comment}</em>' if comment else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No status change history recorded yet.")

    st.divider()


# ============================================================
# Footer
# ============================================================
st.markdown("""
<div style="text-align: center; color: #a0aec0; font-size: 0.8rem;
            padding: 1rem 0; border-top: 1px solid #e2e8f0; margin-top: 1rem;">
    🎯 Action Item Tracker • Items are automatically flagged as overdue when past deadline
</div>
""", unsafe_allow_html=True)
