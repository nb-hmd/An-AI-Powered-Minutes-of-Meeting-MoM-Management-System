"""
Theme Utility - Apply dark/light mode CSS across all pages.

Strategy:
 - DARK  mode: Override Streamlit's light base theme aggressively with !important
 - LIGHT mode: Also use !important to reset any residual dark overrides and ensure
   every element is visible on a light background
Both modes are treated equally — no relying on Streamlit's base to "do the work".
"""

import streamlit as st


def apply_theme():
    """
    Inject comprehensive theme CSS.
    Call this at the top of every page right after AuthService.require_auth().
    Defaults to dark mode if not yet set in session state.
    """
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True

    dark = st.session_state.get("dark_mode", True)

    # ── colour tokens ─────────────────────────────────────────────────────────
    if dark:
        BG          = "#1a1a2e"
        BG2         = "#16213e"
        BG3         = "#0f3460"
        TEXT        = "#e2e8f0"
        SUBTEXT     = "#a0aec0"
        BORDER      = "rgba(255,255,255,0.10)"
        SHADOW      = "rgba(0,0,0,0.45)"
        INPUT_BG    = "#0f3460"
        SELECT_BG   = "#0f3460"
        BTN_BG      = "#16213e"
        TABLE_HEAD  = "#16213e"
        TABLE_EVEN  = "#1a1a2e"
        TABLE_HOVER = "#0f3460"
        CODE_BG     = "#0d1b2a"
        ALERT_BG    = "#16213e"
        EXPANDER_BG = "#16213e"
        S_BG1       = "#1a1a2e"   # sidebar gradient start
        S_BG2       = "#16213e"   # sidebar gradient end
        S_TEXT      = "#e2e8f0"
        S_HOVER     = "#0f3460"
    else:
        BG          = "#f7f9fc"
        BG2         = "#eef1f7"
        BG3         = "#e2e8f0"
        TEXT        = "#1a202c"
        SUBTEXT     = "#4a5568"
        BORDER      = "rgba(0,0,0,0.10)"
        SHADOW      = "rgba(0,0,0,0.07)"
        INPUT_BG    = "#ffffff"
        SELECT_BG   = "#ffffff"
        BTN_BG      = "#eef1f7"
        TABLE_HEAD  = "#eef1f7"
        TABLE_EVEN  = "#f7f9fc"
        TABLE_HOVER = "#dde5f7"
        CODE_BG     = "#f0f4f8"
        ALERT_BG    = "#eef1f7"
        EXPANDER_BG = "#ffffff"
        S_BG1       = "#ffffff"   # sidebar gradient start
        S_BG2       = "#eef1f7"   # sidebar gradient end
        S_TEXT      = "#1a202c"
        S_HOVER     = "#dde5f7"

    st.markdown(f"""
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       0. ALWAYS hide Streamlit's auto-generated page nav (prevents duplicate sidebar)
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"] {{
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    /* Collapse the top padding Streamlit adds for the nav area */
    div[data-testid="stSidebarUserContent"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.5rem !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       1. FULL APP BACKGROUND
    ═══════════════════════════════════════════════════════════════════════ */
    html, body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main,
    .main {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}
    .main .block-container,
    [data-testid="block-container"] {{
        background-color: {BG} !important;
        color: {TEXT} !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }}
    /* Top toolbar / header bar */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background-color: {BG} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       2. ALL TEXT — headings, paragraphs, labels
    ═══════════════════════════════════════════════════════════════════════ */
    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT} !important;
    }}
    p, li, td, th, caption,
    [data-testid="stText"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    .stMarkdown a {{
        color: {TEXT} !important;
    }}
    /* Streamlit widget labels */
    label,
    [data-testid="stWidgetLabel"] > div,
    [data-testid="stWidgetLabel"] label,
    [data-testid="InputInstructions"] {{
        color: {TEXT} !important;
    }}
    /* Generic small text / captions */
    small, .caption, [data-testid="stCaptionContainer"] {{
        color: {SUBTEXT} !important;
    }}
    /* Dividers */
    hr {{
        border-color: {BORDER} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       3. SIDEBAR — complete dark↔light switch
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {S_BG1} 0%, {S_BG2} 100%) !important;
        border-right: 1px solid {BORDER} !important;
    }}
    /* Every single child element inside sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {{
        color: {S_TEXT} !important;
    }}
    /* Sidebar nav links (page_link) */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"],
    [data-testid="stSidebar"] .st-emotion-cache-1rtdyuf,
    [data-testid="stSidebar"] a[href] {{
        color: {S_TEXT} !important;
        border-radius: 8px;
    }}
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
        background-color: {S_HOVER} !important;
    }}
    /* Sidebar toggle (dark mode switch) */
    [data-testid="stSidebar"] [data-testid="stToggle"] p,
    [data-testid="stSidebar"] [data-testid="stToggle"] span,
    [data-testid="stSidebar"] [data-testid="stToggle"] label {{
        color: {S_TEXT} !important;
    }}
    /* Sidebar buttons (Logout) */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: {S_HOVER} !important;
        color: {S_TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #667eea !important;
        color: #ffffff !important;
        border-color: #667eea !important;
    }}
    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {{
        border-color: {BORDER} !important;
    }}
    /* Sidebar user info box (inline HTML) */
    [data-testid="stSidebar"] .stMarkdown *,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
        color: {S_TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       4. INPUT FIELDS
    ═══════════════════════════════════════════════════════════════════════ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {{
        background-color: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: {SUBTEXT} !important;
        opacity: 1 !important;
    }}
    /* Selectbox */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div {{
        background-color: {SELECT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
    }}
    /* MultiSelect */
    .stMultiSelect [data-baseweb="select"] > div {{
        background-color: {SELECT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
    }}
    /* Dropdown menu / popover */
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] ul,
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li {{
        background-color: {BG2} !important;
        color: {TEXT} !important;
    }}
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover {{
        background-color: {BG3} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       5. FORM CONTAINERS
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stForm"] {{
        background-color: {BG2} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: {TEXT} !important;
    }}
    [data-testid="stForm"] * {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       6. TABS
    ═══════════════════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {BG2} !important;
        border-radius: 10px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {SUBTEXT} !important;
        background-color: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: #667eea !important;
        border-bottom: 2px solid #667eea !important;
        background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] label,
    .stTabs [data-baseweb="tab-panel"] h1,
    .stTabs [data-baseweb="tab-panel"] h2,
    .stTabs [data-baseweb="tab-panel"] h3 {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       7. METRICS
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="metric-container"] {{
        background-color: {BG2} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }}
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricValue"] div,
    [data-testid="metric-container"] p,
    [data-testid="metric-container"] span {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       8. EXPANDERS
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stExpander"] {{
        background-color: {EXPANDER_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {{
        color: {TEXT} !important;
        background-color: {EXPANDER_BG} !important;
    }}
    [data-testid="stExpander"] > div:last-child,
    [data-testid="stExpander"] > div:last-child p,
    [data-testid="stExpander"] > div:last-child span,
    [data-testid="stExpander"] > div:last-child label {{
        color: {TEXT} !important;
        background-color: {EXPANDER_BG} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       9. ALERTS (info, warning, success, error)
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div,
    [data-testid="stNotificationContentText"] {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       10. DATAFRAMES / TABLES
    ═══════════════════════════════════════════════════════════════════════ */
    .stDataFrame,
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div {{
        background-color: {BG2} !important;
        color: {TEXT} !important;
    }}
    .stDataFrame th {{
        background-color: {TABLE_HEAD} !important;
        color: {TEXT} !important;
    }}
    .stDataFrame tr:nth-child(even) {{
        background-color: {TABLE_EVEN} !important;
    }}
    .stDataFrame tr:hover {{
        background-color: {TABLE_HOVER} !important;
    }}
    .stDataFrame td {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       11. BUTTONS (main area only, NOT sidebar)
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stMain"] .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background-color: {BTN_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
    }}
    [data-testid="stMain"] .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background-color: #667eea !important;
        color: #ffffff !important;
        border-color: #667eea !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       12. CHECKBOXES, RADIOS, TOGGLES
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] span,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] span {{
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       13. FILE UPLOADER
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span {{
        color: {TEXT} !important;
    }}
    [data-testid="stFileUploader"] > div {{
        background-color: {BG2} !important;
        border: 2px dashed {BORDER} !important;
        border-radius: 12px !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       14. CODE BLOCKS
    ═══════════════════════════════════════════════════════════════════════ */
    code, pre, [data-testid="stCode"] {{
        background-color: {CODE_BG} !important;
        color: {TEXT} !important;
        border-radius: 6px;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       15. CUSTOM HTML COMPONENTS — stat-card, kpi-card, etc.
    ═══════════════════════════════════════════════════════════════════════ */
    .stat-card {{
        background: {BG2} !important;
        border-radius: 12px;
        padding: 1.3rem;
        box-shadow: 0 4px 15px {SHADOW};
        text-align: center;
        border-left: 4px solid;
        transition: transform 0.2s ease;
    }}
    .stat-card:hover {{ transform: translateY(-2px); }}
    .stat-card .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {TEXT} !important;
    }}
    .stat-card .stat-label {{
        font-size: 0.8rem;
        color: {SUBTEXT} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    /* quality-report box in Create MoM */
    .quality-report {{
        background: {BG2} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       16. FOOTER
    ═══════════════════════════════════════════════════════════════════════ */
    .footer {{
        text-align: center;
        color: {SUBTEXT} !important;
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
        border-top: 1px solid {BORDER};
        margin-top: 3rem;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       17. PRINT
    ═══════════════════════════════════════════════════════════════════════ */
    @media print {{
        [data-testid="stSidebar"] {{ display: none !important; }}
        .stButton {{ display: none !important; }}
        header {{ display: none !important; }}
        .main .block-container {{ padding: 0 !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)
