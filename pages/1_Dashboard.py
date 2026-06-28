"""
Dashboard Page
Analytics overview with KPI cards, rich themed charts, and recent activity.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from services.auth_service import AuthService
from services.analytics_service import AnalyticsService
from utils.formatters import format_datetime, format_status
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()

# ============================================================
# Theme tokens (dark / light aware)
# ============================================================
_dark      = st.session_state.get("dark_mode", True)
_card_bg   = "#16213e" if _dark else "#ffffff"
_text      = "#e2e8f0" if _dark else "#1a202c"
_subtext   = "#a0aec0" if _dark else "#718096"
_shadow    = "rgba(0,0,0,0.40)" if _dark else "rgba(0,0,0,0.08)"
_grid      = "rgba(255,255,255,0.07)" if _dark else "rgba(0,0,0,0.06)"
_axis_c    = "#a0aec0" if _dark else "#718096"
_leg_bg    = "rgba(22,33,62,0.85)"   if _dark else "rgba(255,255,255,0.85)"
_fill_area = "rgba(102,126,234,0.20)" if _dark else "rgba(102,126,234,0.12)"

# Multi-colour palettes
VIBRANT = ["#667eea","#f6ad55","#68d391","#fc8181","#63b3ed","#b794f4","#f687b3","#4fd1c5"]
RICH    = ["#667eea","#764ba2","#f093fb","#f5576c","#4facfe","#00f2fe","#43e97b","#38f9d7"]
STATUS_COLORS = {
    "pending":     "#f6ad55",
    "in_progress": "#63b3ed",
    "completed":   "#68d391",
    "overdue":     "#fc8181",
}

def base_layout(**kw):
    """Return shared Plotly layout dict, theme-aware.
    NOTE: legend is NOT included here — set it per-chart to avoid keyword conflicts.
    """
    return dict(
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_text, family="Inter, Arial, sans-serif", size=12),
        xaxis=dict(color=_axis_c, gridcolor=_grid, zerolinecolor=_grid,
                   tickfont=dict(color=_axis_c), title_font=dict(color=_axis_c)),
        yaxis=dict(color=_axis_c, gridcolor=_grid, zerolinecolor=_grid,
                   tickfont=dict(color=_axis_c), title_font=dict(color=_axis_c)),
        margin=dict(t=30, b=50, l=50, r=20),
        height=330,
        **kw,
    )

# Reusable default legend style (pass as legend=LEG_DEFAULT or customize per chart)
LEG_DEFAULT = dict(bgcolor=_leg_bg, bordercolor=_grid, borderwidth=1,
                   font=dict(color=_text))

def chart_card(title, description):
    """Render a titled description card above a chart."""
    st.markdown(f"""
    <div style="background:{_card_bg}; border-radius:12px; padding:0.9rem 1.1rem;
                box-shadow:0 3px 12px {_shadow}; margin-bottom:0.6rem;">
        <div style="color:{_text}; font-weight:700; font-size:0.95rem;">{title}</div>
        <div style="color:{_subtext}; font-size:0.78rem; margin-top:0.25rem; line-height:1.5;">
            {description}
        </div>
    </div>""", unsafe_allow_html=True)


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            padding:1.5rem 2rem; border-radius:16px; color:white;
            margin-bottom:1.5rem; box-shadow:0 8px 32px rgba(102,126,234,0.35);">
    <h2 style="margin:0; font-size:1.7rem; font-weight:700;">
        &#128202; Analytics Dashboard
    </h2>
    <p style="margin:0.4rem 0 0; opacity:0.88; font-size:1rem;">
        Real-time overview of all meeting records, action items, and team activity.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Fetch all data up-front
# ============================================================
stats         = AnalyticsService.get_dashboard_stats()
monthly_data  = AnalyticsService.get_meetings_per_month()
category_data = AnalyticsService.get_meetings_by_category()
dept_data     = AnalyticsService.get_meetings_by_department()
status_data   = AnalyticsService.get_action_items_by_status()
assignee_data = AnalyticsService.get_top_assignees(8)
deadlines     = AnalyticsService.get_upcoming_deadlines(10)
activity      = AnalyticsService.get_recent_activity(15)


# ============================================================
# KPI Cards  (5 cards, each with unique accent color)
# ============================================================
st.markdown(f"<h3 style='color:{_text}; margin-bottom:0.8rem;'>"
            "&#128204; Key Metrics</h3>", unsafe_allow_html=True)

kpi_defs = [
    ("Total Meetings",    stats["total_meetings"],    "#667eea", "&#128203;"),
    ("This Month",        stats["this_month"],        "#48bb78", "&#128197;"),
    ("Pending Actions",   stats["pending_actions"],   "#ed8936", "&#9203;"),
    ("Completed Actions", stats["completed_actions"], "#38a169", "&#9989;"),
    ("Overdue Actions",   stats["overdue_actions"],   "#e53e3e", "&#128680;"),
]
cols = st.columns(5)
for col, (label, val, color, icon) in zip(cols, kpi_defs):
    with col:
        st.markdown(f"""
        <div style="background:{_card_bg}; border-radius:14px; padding:1rem 0.6rem;
                    text-align:center; box-shadow:0 4px 18px {_shadow};
                    border-top:4px solid {color};">
            <div style="font-size:1.5rem;">{icon}</div>
            <div style="font-size:1.9rem; font-weight:800; color:{color};
                        line-height:1.1; margin:0.2rem 0;">{val}</div>
            <div style="font-size:0.7rem; color:{_subtext}; text-transform:uppercase;
                        letter-spacing:0.6px;">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# ROW 1 — Meetings Per Month + Category Donut
# ============================================================
st.markdown(f"<h3 style='color:{_text}; margin-bottom:0.4rem;'>"
            "&#128200; Meeting Trends</h3>", unsafe_allow_html=True)

r1a, r1b = st.columns([3, 2])

# --- Monthly bar chart ---
with r1a:
    chart_card(
        "&#128197; Meetings Created Per Month",
        "Shows how many Minutes of Meeting documents were created each month. "
        "Each bar is uniquely colored — rising bars indicate increasing meeting activity."
    )
    if monthly_data:
        df_m = pd.DataFrame(monthly_data)
        df_m["month"] = pd.to_datetime(df_m["month"])
        df_m = df_m.sort_values("month")
        df_m["lbl"] = df_m["month"].dt.strftime("%b %Y")
        n = len(df_m)
        bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]

        fig = go.Figure(go.Bar(
            x=df_m["lbl"], y=df_m["count"],
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=df_m["count"], textposition="outside",
            textfont=dict(color=_text, size=12),
            hovertemplate="<b>%{x}</b><br>Meetings: %{y}<extra></extra>",
        ))
        fig.update_layout(**base_layout(bargap=0.35,
                                        xaxis_title="Month",
                                        yaxis_title="Meetings Created"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No meetings yet. Create your first MoM to see this chart.")

# --- Category donut ---
with r1b:
    chart_card(
        "&#127991; Meetings by Meeting Type",
        "Breakdown of meeting categories (e.g. Project Review, Standup, Planning). "
        "Helps identify which type of meetings your team holds most frequently."
    )
    if category_data:
        df_c = pd.DataFrame(category_data)
        total_c = int(df_c["count"].sum())
        fig = go.Figure(go.Pie(
            labels=df_c["category"], values=df_c["count"],
            hole=0.52,
            marker=dict(colors=RICH, line=dict(color=_card_bg, width=2)),
            textfont=dict(color=_text, size=11),
            hovertemplate="<b>%{label}</b><br>Count: %{value}  |  %{percent}<extra></extra>",
        ))
        fig.update_layout(**base_layout(showlegend=True))
        fig.update_layout(
            legend=dict(orientation="v", x=1.02, y=0.5,
                        bgcolor="rgba(0,0,0,0)", font=dict(color=_text, size=11)),
            annotations=[dict(text=f"<b>{total_c}</b><br>Total",
                              x=0.5, y=0.5,
                              font=dict(size=14, color=_text),
                              showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data yet.")


# ============================================================
# ROW 2 — Action Status Donut + Top Assignees Stacked Bar
# ============================================================
st.markdown(f"<h3 style='color:{_text}; margin-bottom:0.4rem;'>"
            "&#127919; Action Item Insights</h3>", unsafe_allow_html=True)

r2a, r2b = st.columns([2, 3])

# --- Status donut ---
with r2a:
    chart_card(
        "&#128308; Action Items by Status",
        "Donut chart showing how many action items are Pending, In Progress, "
        "Completed, or Overdue across all meetings. Green = done, Red = overdue."
    )
    if status_data:
        df_s = pd.DataFrame(status_data)
        s_colors = [STATUS_COLORS.get(s, "#a0aec0") for s in df_s["status"]]
        s_labels = [s.replace("_", " ").title() for s in df_s["status"]]
        total_s  = int(df_s["count"].sum())

        fig = go.Figure(go.Pie(
            labels=s_labels, values=df_s["count"],
            hole=0.55,
            marker=dict(colors=s_colors, line=dict(color=_card_bg, width=3)),
            textfont=dict(color=_text, size=11),
            hovertemplate="<b>%{label}</b><br>Count: %{value}  |  %{percent}<extra></extra>",
        ))
        fig.update_layout(**base_layout(showlegend=True))
        fig.update_layout(
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.18,
                        bgcolor="rgba(0,0,0,0)", font=dict(color=_text, size=10)),
            annotations=[dict(text=f"<b>{total_s}</b><br>Actions",
                              x=0.5, y=0.5,
                              font=dict(size=14, color=_text),
                              showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No action items recorded yet.")

# --- Top assignees stacked bar ---
with r2b:
    chart_card(
        "&#128100; Top Assignees — Tasks Assigned vs Completed",
        "Stacked bar showing the team members with the most action items. "
        "Green = completed tasks, Orange = still pending or in progress. "
        "Use this to spot workload imbalances across the team."
    )
    if assignee_data:
        df_a = pd.DataFrame(assignee_data)
        df_a["completed"] = df_a["completed"].astype(int)
        df_a["pending"]   = df_a["total"].astype(int) - df_a["completed"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Completed", x=df_a["assigned_to"], y=df_a["completed"],
            marker_color="#68d391",
            hovertemplate="<b>%{x}</b><br>Completed: %{y}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name="Pending / In Progress", x=df_a["assigned_to"], y=df_a["pending"],
            marker_color="#f6ad55",
            hovertemplate="<b>%{x}</b><br>Remaining: %{y}<extra></extra>",
        ))
        fig.update_layout(**base_layout(barmode="stack", bargap=0.30,
                                         xaxis_title="Team Member",
                                         yaxis_title="Action Items"))
        fig.update_layout(
            legend=dict(orientation="h", x=0.5, xanchor="center", y=1.12,
                        bgcolor="rgba(0,0,0,0)", font=dict(color=_text, size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assignee data yet.")


# ============================================================
# ROW 3 — Department Bar + MoM Trend Area
# ============================================================
st.markdown(f"<h3 style='color:{_text}; margin-bottom:0.4rem;'>"
            "&#127970; Department & Trend Analysis</h3>", unsafe_allow_html=True)

r3a, r3b = st.columns(2)

# --- Department bar ---
with r3a:
    chart_card(
        "&#127970; Meetings by Department",
        "Shows which departments hold the most meetings. "
        "Each department bar has a distinct colour for easy comparison."
    )
    if dept_data:
        df_d = pd.DataFrame(dept_data)
        d_colors = [VIBRANT[i % len(VIBRANT)] for i in range(len(df_d))]

        fig = go.Figure(go.Bar(
            x=df_d["department"], y=df_d["count"],
            marker=dict(color=d_colors, line=dict(width=0)),
            text=df_d["count"], textposition="outside",
            textfont=dict(color=_text, size=12),
            hovertemplate="<b>%{x}</b><br>Meetings: %{y}<extra></extra>",
        ))
        fig.update_layout(**base_layout(bargap=0.35,
                                        xaxis_title="Department",
                                        yaxis_title="Meetings"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No department data yet.")

# --- Trend area line ---
with r3b:
    chart_card(
        "&#128201; MoM Creation Trend (Spline Area)",
        "Area chart showing MoM documentation activity over time. "
        "The dotted line marks the monthly average. "
        "A rising trend means your team is becoming more consistent with meeting records."
    )
    if monthly_data:
        df_t = pd.DataFrame(monthly_data)
        df_t["month"] = pd.to_datetime(df_t["month"])
        df_t = df_t.sort_values("month")
        avg  = df_t["count"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_t["month"], y=df_t["count"],
            mode="lines+markers",
            name="MoMs Created",
            line=dict(color="#667eea", width=3, shape="spline"),
            marker=dict(color="#667eea", size=9,
                        line=dict(color="#ffffff", width=2)),
            fill="tozeroy",
            fillcolor=_fill_area,
            hovertemplate="<b>%{x|%b %Y}</b><br>MoMs: %{y}<extra></extra>",
        ))
        fig.add_hline(
            y=avg, line_dash="dot", line_color="#f6ad55",
            annotation_text=f"Avg {avg:.1f}",
            annotation_font_color=_axis_c,
            annotation_font_size=11,
        )
        fig.update_layout(**base_layout(xaxis_title="Month",
                                        yaxis_title="MoMs Created"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data yet.")


# ============================================================
# Upcoming Deadlines
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background:{_card_bg}; border-radius:14px; padding:1rem 1.4rem;
            box-shadow:0 4px 15px {_shadow}; margin-bottom:0.8rem;">
    <div style="color:{_text}; font-weight:700; font-size:1.05rem;">
        &#9200; Upcoming Deadlines
    </div>
    <div style="color:{_subtext}; font-size:0.8rem; margin-top:0.25rem;">
        Action items with approaching or overdue deadlines. Review these to keep
        all tasks on track and avoid missed commitments.
    </div>
</div>""", unsafe_allow_html=True)

if deadlines:
    dl_df = pd.DataFrame([{
        "Meeting":     d.get("mom_title", ""),
        "Action Item": d.get("description", ""),
        "Assigned To": d.get("assigned_to", ""),
        "Deadline":    str(d.get("deadline", "")),
        "Status":      format_status(d.get("status", "pending")),
    } for d in deadlines])
    st.dataframe(dl_df, use_container_width=True, hide_index=True)
else:
    st.success("All action items are on schedule — no upcoming deadlines!")


# ============================================================
# Recent Activity
# ============================================================
st.markdown(f"""
<div style="background:{_card_bg}; border-radius:14px; padding:1rem 1.4rem;
            box-shadow:0 4px 15px {_shadow}; margin-bottom:0.8rem; margin-top:1rem;">
    <div style="color:{_text}; font-weight:700; font-size:1.05rem;">
        &#128220; Recent Activity Log
    </div>
    <div style="color:{_subtext}; font-size:0.8rem; margin-top:0.25rem;">
        A real-time audit trail of user actions — logins, MoM creation, edits, and
        status updates. Useful for tracking changes and ensuring accountability.
    </div>
</div>""", unsafe_allow_html=True)

if activity:
    act_df = pd.DataFrame([{
        "Time":    format_datetime(a.get("timestamp")),
        "User":    a.get("username", ""),
        "Action":  a.get("action", ""),
        "Details": a.get("details", ""),
    } for a in activity])
    st.dataframe(act_df, use_container_width=True, hide_index=True)
else:
    st.info("No activity recorded yet.")
