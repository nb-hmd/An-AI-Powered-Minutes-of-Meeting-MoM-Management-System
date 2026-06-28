"""
🔍 Search Page
Search meetings by title, date range, venue, or assigned person.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services.auth_service import AuthService
from models.mom import MoMModel
from utils.formatters import format_datetime, truncate_text
from utils.constants import MEETING_CATEGORIES
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
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">🔍 Search Meetings</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">Find meetings by title, date, venue, or assigned person.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Search Filters
# ============================================================
with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        search_title = st.text_input("📌 Search by Title", placeholder="Enter meeting title...")
        search_venue = st.text_input("📍 Search by Venue", placeholder="Enter venue...")
        search_assigned = st.text_input("👤 Search by Assigned Person", placeholder="Person name...")
    with col2:
        search_category = st.selectbox("📁 Category", ["All"] + MEETING_CATEGORIES)
        search_date_from = st.date_input("📅 From Date", value=date.today() - timedelta(days=90))
        search_date_to = st.date_input("📅 To Date", value=date.today())

    scol1, scol2 = st.columns(2)
    with scol1:
        search_btn = st.form_submit_button("🔍 Search", use_container_width=True)
    with scol2:
        clear_btn = st.form_submit_button("🗑️ Clear Filters", use_container_width=True)


# ============================================================
# Perform Search
# ============================================================
if search_btn:
    results = MoMModel.search_moms(
        title=search_title.strip() if search_title.strip() else None,
        venue=search_venue.strip() if search_venue.strip() else None,
        date_from=search_date_from,
        date_to=search_date_to,
        assigned_to=search_assigned.strip() if search_assigned.strip() else None,
        category=search_category if search_category != "All" else None,
    )

    st.markdown(f"### 📊 Found **{len(results)}** result(s)")
    st.divider()

    if results:
        for mom in results:
            with st.container():
                mc1, mc2, mc3 = st.columns([5, 3, 2])
                with mc1:
                    st.markdown(f"### {mom['title']}")
                    st.markdown(f"📅 {format_datetime(mom['date_time'])} | 📍 {mom.get('venue', 'N/A')}")
                with mc2:
                    st.markdown(f"📁 {mom.get('category', 'N/A')}")
                    if mom.get("discussion"):
                        st.markdown(f"💬 {truncate_text(mom['discussion'], 80)}")
                with mc3:
                    if st.button("👁️ View", key=f"search_view_{mom['id']}"):
                        st.session_state.view_mom_id = mom["id"]
                        st.switch_page("pages/3_View_MoMs.py")
                st.divider()

        # Also show as table
        with st.expander("📊 View as Table"):
            df = pd.DataFrame([{
                "Title": m["title"],
                "Date": format_datetime(m["date_time"]),
                "Venue": m.get("venue", ""),
                "Category": m.get("category", ""),
                "Department": m.get("department", ""),
                "Created By": m.get("creator_name", ""),
            } for m in results])
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No meetings found matching your criteria.")

elif clear_btn:
    st.rerun()
else:
    st.info("💡 Use the filters above and click **Search** to find meetings.")
