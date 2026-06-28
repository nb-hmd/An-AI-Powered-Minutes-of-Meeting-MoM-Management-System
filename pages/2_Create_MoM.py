"""
➕ Create MoM Page
Comprehensive form to create new Minutes of Meeting with:
- Speech-to-Text (audio upload → transcription → AI extraction)
- AI Summary Generator (grammar cleanup, summarize, format rough notes)
- AI Quality Checker (pre-save review)
- Attendees, action items, and file attachments
"""

import streamlit as st
from datetime import datetime, date, time
from services.auth_service import AuthService
from services.mom_service import MoMService
from services.ai_service import AIService
from services.speech_service import SpeechService
from utils.constants import MEETING_CATEGORIES, ALLOWED_FILE_TYPES
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()


# ============================================================
# Custom CSS  (theme-aware)
# ============================================================
_d = st.session_state.get("dark_mode", True)
_qr_bg  = "#16213e" if _d else "#f7fafc"
_qr_bdr = "rgba(255,255,255,0.08)" if _d else "#e2e8f0"
_qr_txt = "#e2e8f0" if _d else "#2d3748"

st.markdown(f"""
<style>
    .ai-tools-card {{
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(161, 140, 209, 0.3);
    }}
    .ai-tools-card h4 {{ margin: 0 0 0.3rem; }}
    .ai-tools-card p  {{ margin: 0; opacity: 0.9; font-size: 0.85rem; }}

    .quality-report {{
        background: {_qr_bg} !important;
        border: 1px solid {_qr_bdr} !important;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: {_qr_txt} !important;
    }}
    .quality-report * {{ color: {_qr_txt} !important; }}
    .quality-score {{
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
    }}
    .quality-score.good   {{ color: #38a169 !important; }}
    .quality-score.medium {{ color: #ed8936 !important; }}
    .quality-score.poor   {{ color: #e53e3e !important; }}

    .issue-item {{
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: {_qr_txt} !important;
    }}
    .issue-warning {{ background: #fefcbf; border-left: 3px solid #ecc94b; color: #7b4f00 !important; }}
    .issue-error   {{ background: #fed7d7; border-left: 3px solid #e53e3e; color: #7b1f1f !important; }}
    .issue-info    {{ background: #bee3f8; border-left: 3px solid #4299e1; color: #1a3a5c !important; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# Page Header
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <h2 style="margin:0;">➕ Create New Minutes of Meeting</h2>
    <p style="margin:0.3rem 0 0; opacity:0.85;">Fill in the details below or use AI tools to auto-generate from audio/notes.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Initialize Session State
# ============================================================
if "attendees_count" not in st.session_state:
    st.session_state.attendees_count = 1
if "action_items_count" not in st.session_state:
    st.session_state.action_items_count = 1
# AI-populated fields
if "ai_agenda" not in st.session_state:
    st.session_state.ai_agenda = ""
if "ai_discussion" not in st.session_state:
    st.session_state.ai_discussion = ""
if "ai_decisions" not in st.session_state:
    st.session_state.ai_decisions = ""
if "ai_action_items" not in st.session_state:
    st.session_state.ai_action_items = []
if "quality_report" not in st.session_state:
    st.session_state.quality_report = None
if "ai_transcript" not in st.session_state:
    st.session_state.ai_transcript = ""


def add_attendee():
    st.session_state.attendees_count += 1

def remove_attendee():
    if st.session_state.attendees_count > 1:
        st.session_state.attendees_count -= 1

def add_action_item():
    st.session_state.action_items_count += 1

def remove_action_item():
    if st.session_state.action_items_count > 1:
        st.session_state.action_items_count -= 1


# ============================================================
# F15 & F16 — AI Tools Section (OUTSIDE FORM)
# ============================================================
st.markdown("""
<div class="ai-tools-card">
    <h4>🤖 AI-Powered Tools</h4>
    <p>Upload audio for transcription, clean up rough notes, or generate a summary — all powered by OpenAI.</p>
</div>
""", unsafe_allow_html=True)

ai_tab1, ai_tab2, ai_tab3 = st.tabs([
    "🎙️ Speech-to-Text",
    "✨ AI Summary & Cleanup",
    "📝 Format Rough Notes"
])

# ---- F15: Speech-to-Text ----
with ai_tab1:
    st.markdown("#### 🎙️ Upload Audio → Auto-Generate MoM Draft")
    st.caption("Supported formats: **MP3, WAV, M4A** — Audio is transcribed via OpenAI Whisper, then AI extracts agenda, discussion, decisions, and action items.")

    audio_file = st.file_uploader(
        "Upload audio file",
        type=["mp3", "wav", "m4a"],
        key="audio_upload",
        help="Max file size depends on your OpenAI plan."
    )

    if audio_file:
        st.audio(audio_file, format=f"audio/{audio_file.name.rsplit('.', 1)[-1]}")
        if st.button("🚀 Transcribe & Extract", key="btn_transcribe", use_container_width=True):
            with st.spinner("🎙️ Transcribing audio and extracting meeting content..."):
                audio_file.seek(0)
                result = SpeechService.transcribe_and_extract(
                    audio_file,
                    user_id=st.session_state.get("user_id")
                )

            if result["success"]:
                st.success(f"✅ {result['message']}")

                # Store results in session state
                st.session_state.ai_transcript = result.get("transcript", "")
                st.session_state.ai_discussion = result.get("discussion", "")
                st.session_state.ai_decisions = result.get("decisions", "")
                st.session_state.ai_agenda = result.get("agenda", "")
                st.session_state.ai_action_items = result.get("action_items", [])

                # Update action items count
                if result.get("action_items"):
                    st.session_state.action_items_count = max(
                        len(result["action_items"]),
                        st.session_state.action_items_count
                    )

                st.rerun()
            else:
                st.error(f"❌ {result['message']}")

    # Show transcript if available
    if st.session_state.ai_transcript:
        with st.expander("📄 Raw Transcript", expanded=False):
            st.text_area("Transcript", st.session_state.ai_transcript, height=150,
                        disabled=True, key="show_transcript")

# ---- F16: AI Summary & Grammar Cleanup ----
with ai_tab2:
    st.markdown("#### ✨ AI Summary Generator & Grammar Cleanup")
    st.caption("Paste rough meeting notes below. AI will clean grammar, generate a summary, extract decisions, and suggest action items.")

    rough_text = st.text_area(
        "Paste rough notes or discussion text",
        height=200,
        placeholder="Paste your rough meeting notes here...\n\nThe AI will:\n• Clean grammar & spelling\n• Generate a concise summary\n• Extract key decisions\n• Suggest action items",
        key="rough_notes_input"
    )

    rc1, rc2 = st.columns(2)
    with rc1:
        if st.button("🧹 Clean Grammar Only", key="btn_clean", use_container_width=True):
            if rough_text and rough_text.strip():
                with st.spinner("🧹 Cleaning grammar..."):
                    result = AIService.clean_grammar(
                        rough_text,
                        user_id=st.session_state.get("user_id")
                    )
                if result["success"]:
                    st.success("✅ Grammar cleaned!")
                    st.session_state.ai_discussion = result["cleaned_text"]
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.warning("Please paste some text first.")

    with rc2:
        if st.button("🤖 Full AI Summary", key="btn_summarize", use_container_width=True):
            if rough_text and rough_text.strip():
                with st.spinner("🤖 Generating AI summary..."):
                    result = AIService.summarize_text(
                        rough_text,
                        user_id=st.session_state.get("user_id")
                    )
                if result["success"]:
                    st.success("✅ Summary generated!")
                    st.session_state.ai_discussion = result["summary"]
                    st.session_state.ai_decisions = result["decisions"]
                    st.session_state.ai_action_items = result.get("action_items", [])

                    if result.get("action_items"):
                        st.session_state.action_items_count = max(
                            len(result["action_items"]),
                            st.session_state.action_items_count
                        )
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.warning("Please paste some text first.")

# ---- F16: Format Rough Notes into MoM ----
with ai_tab3:
    st.markdown("#### 📝 Convert Rough Notes → Structured MoM")
    st.caption("Paste handwritten notes, voice notes text, or any rough content. AI will organize it into proper Agenda, Discussion, Decisions, and Action Items sections.")

    raw_notes = st.text_area(
        "Paste raw/rough notes",
        height=200,
        placeholder="Paste ANY rough notes here — handwritten, voice memos, bullet points...\n\nThe AI will structure them into a proper MoM format.",
        key="raw_notes_input"
    )

    if st.button("📝 Format into MoM Structure", key="btn_format", use_container_width=True):
        if raw_notes and raw_notes.strip():
            with st.spinner("📝 Formatting notes into MoM structure..."):
                result = AIService.format_rough_notes_to_mom(
                    raw_notes,
                    user_id=st.session_state.get("user_id")
                )
            if result["success"]:
                st.success(f"✅ {result['message']}")
                st.session_state.ai_agenda = result["agenda"]
                st.session_state.ai_discussion = result["discussion"]
                st.session_state.ai_decisions = result["decisions"]
                st.session_state.ai_action_items = result.get("action_items", [])

                if result.get("action_items"):
                    st.session_state.action_items_count = max(
                        len(result["action_items"]),
                        st.session_state.action_items_count
                    )
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")
        else:
            st.warning("Please paste some notes first.")

# Show AI pre-fill status
if any([st.session_state.ai_agenda, st.session_state.ai_discussion,
        st.session_state.ai_decisions, st.session_state.ai_action_items]):
    st.info("✅ **AI content loaded!** The form below has been pre-filled. Review and edit before saving.")

st.divider()


# ============================================================
# Meeting Details Form
# ============================================================
with st.form("create_mom_form"):

    # --- Basic Info ---
    st.markdown("### 📋 Meeting Details")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("📌 Meeting Title *", placeholder="e.g., Sprint Planning Meeting")
        meeting_date = st.date_input("📅 Meeting Date *", value=date.today())
        venue = st.text_input("📍 Venue", placeholder="e.g., Conference Room A / Zoom")
    with col2:
        category = st.selectbox("📁 Category", MEETING_CATEGORIES)
        meeting_time = st.time_input("⏰ Meeting Time", value=time(10, 0))
        department = st.text_input("🏢 Department", placeholder="e.g., Engineering")

    st.divider()

    # --- Agenda, Discussion, Decisions (pre-filled by AI if available) ---
    st.markdown("### 📝 Meeting Content")
    agenda = st.text_area(
        "📋 Agenda",
        value=st.session_state.ai_agenda,
        height=100,
        placeholder="1. Item one\n2. Item two\n3. Item three"
    )
    discussion = st.text_area(
        "💬 Discussion Points",
        value=st.session_state.ai_discussion,
        height=150,
        placeholder="Summarize key discussion points..."
    )
    decisions = st.text_area(
        "✅ Decisions Taken",
        value=st.session_state.ai_decisions,
        height=100,
        placeholder="List the decisions made during the meeting..."
    )

    st.divider()

    # --- Attendees ---
    st.markdown("### 👥 Attendees")
    attendees_data = []
    for i in range(st.session_state.attendees_count):
        st.markdown(f"**Attendee {i + 1}**")
        acol1, acol2, acol3, acol4 = st.columns(4)
        with acol1:
            a_name = st.text_input("Name", key=f"att_name_{i}", placeholder="Full name")
        with acol2:
            a_role = st.text_input("Role", key=f"att_role_{i}", placeholder="e.g., Developer")
        with acol3:
            a_email = st.text_input("Email", key=f"att_email_{i}", placeholder="email@example.com")
        with acol4:
            a_dept = st.text_input("Department", key=f"att_dept_{i}", placeholder="e.g., Engineering")
        attendees_data.append({"name": a_name, "role": a_role, "email": a_email, "department": a_dept})

    st.divider()

    # --- Action Items (pre-filled by AI if available) ---
    st.markdown("### 🎯 Action Items")

    # Parse AI action items for pre-filling
    ai_items = st.session_state.ai_action_items or []

    action_items_data = []
    for i in range(st.session_state.action_items_count):
        st.markdown(f"**Action Item {i + 1}**")

        # Pre-fill from AI if available
        ai_prefill = ""
        ai_assigned = ""
        if i < len(ai_items):
            ai_raw = ai_items[i]
            if "→" in ai_raw or "Assigned to:" in ai_raw:
                # Try to parse "Task → Assigned to: Person | Deadline: Date"
                parts = ai_raw.split("→")
                ai_prefill = parts[0].strip()
                if len(parts) > 1:
                    assign_part = parts[1]
                    if "Assigned to:" in assign_part:
                        ai_assigned = assign_part.split("Assigned to:")[1].split("|")[0].strip()
            else:
                ai_prefill = ai_raw

        icol1, icol2, icol3 = st.columns([3, 2, 2])
        with icol1:
            ai_desc = st.text_input("Description", key=f"ai_desc_{i}",
                                    value=ai_prefill,
                                    placeholder="What needs to be done?")
        with icol2:
            ai_assigned_input = st.text_input("Assigned To", key=f"ai_assigned_{i}",
                                              value=ai_assigned,
                                              placeholder="Person name")
        with icol3:
            ai_deadline = st.date_input("Deadline", key=f"ai_deadline_{i}", value=None)
        action_items_data.append({
            "description": ai_desc, "assigned_to": ai_assigned_input,
            "deadline": ai_deadline, "status": "pending"
        })

    st.divider()

    # --- Attachments ---
    st.markdown("### 📎 Attachments")
    uploaded_files = st.file_uploader(
        "Upload files (PDF, JPG, PNG, DOCX, PPTX — max 10MB each)",
        type=ALLOWED_FILE_TYPES,
        accept_multiple_files=True,
    )

    st.divider()

    # --- Submit Buttons ---
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        quality_check = st.form_submit_button("🔍 AI Quality Check ", use_container_width=True)
    with btn_col2:
        submitted = st.form_submit_button("💾 Save Minutes of Meeting", use_container_width=True)

    # ---- F17: AI Quality Checker ----
    if quality_check:
        valid_actions_for_check = [a for a in action_items_data if a["description"].strip()]
        with st.spinner("🔍 Running AI quality check..."):
            qc_result = AIService.quality_check(
                agenda=agenda.strip(),
                discussion=discussion.strip(),
                decisions=decisions.strip(),
                action_items=valid_actions_for_check,
                user_id=st.session_state.get("user_id"),
            )

        if qc_result["success"]:
            score = qc_result["score"]
            issues = qc_result["issues"]

            # Score display
            score_class = "good" if score >= 80 else ("medium" if score >= 50 else "poor")
            st.markdown(f"""
            <div class="quality-report">
                <div class="quality-score {score_class}">{score}/100</div>
                <p style="text-align:center; color:#718096; margin:0;">Quality Score</p>
            </div>
            """, unsafe_allow_html=True)

            if issues:
                st.markdown(f"**{len(issues)} issue(s) found:**")
                for issue in issues:
                    sev = issue["severity"]
                    icon = "⚠️" if sev == "warning" else ("❌" if sev == "error" else "ℹ️")
                    css_class = f"issue-{sev}"
                    st.markdown(f"""
                    <div class="issue-item {css_class}">
                        {icon} <strong>{issue['field']}</strong>: {issue['message']}
                    </div>
                    """, unsafe_allow_html=True)
                st.info("💡 You can dismiss these warnings and save anyway by clicking **Save Minutes of Meeting**.")
            else:
                st.success("🎉 No issues found! Your MoM looks great.")
        else:
            st.error(f"❌ Quality check failed: {qc_result['message']}")

    # ---- Save MoM ----
    if submitted:
        # Run full validation
        from utils.validators import validate_mom_form
        validation_errors = validate_mom_form(
            title=title,
            meeting_date=meeting_date,
            agenda=agenda,
            action_items=action_items_data,
            uploaded_files=uploaded_files if uploaded_files else None,
            is_new=True,
        )

        if validation_errors:
            st.error(f"❌ **{len(validation_errors)} validation error(s) found.** Please fix them before saving:")
            for err in validation_errors:
                st.markdown(
                    f'<div style="padding:0.4rem 0.8rem; margin-bottom:0.3rem; '
                    f'border-left:3px solid #e53e3e; background:#fed7d7; '
                    f'border-radius:0 8px 8px 0; font-size:0.9rem;">'
                    f'❌ <strong>{err["field"]}</strong>: {err["message"]}</div>',
                    unsafe_allow_html=True
                )
        else:
            # Combine date + time
            meeting_datetime = datetime.combine(meeting_date, meeting_time)

            # Filter out empty attendees / action items
            valid_attendees = [a for a in attendees_data if a["name"].strip()]
            valid_actions = [a for a in action_items_data if a["description"].strip()]

            result = MoMService.create_mom(
                title=title.strip(),
                date_time=meeting_datetime,
                venue=venue.strip(),
                agenda=agenda.strip(),
                discussion=discussion.strip(),
                decisions=decisions.strip(),
                category=category,
                department=department.strip(),
                created_by=st.session_state.get("user_id"),
                attendees=valid_attendees,
                action_items=valid_actions,
                uploaded_files=uploaded_files if uploaded_files else None,
            )

            if result["success"]:
                st.success(f"✅ {result['message']} (ID: {result['mom_id']})")
                st.balloons()
                # Clear AI session state
                for key in ["ai_agenda", "ai_discussion", "ai_decisions",
                            "ai_action_items", "ai_transcript", "quality_report"]:
                    st.session_state[key] = "" if key != "ai_action_items" else []
            else:
                st.error(f"❌ {result['message']}")


# ============================================================
# Dynamic Add/Remove Buttons (outside form)
# ============================================================
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    st.button("➕ Add Attendee", on_click=add_attendee)
with col_btn2:
    st.button("➖ Remove Attendee", on_click=remove_attendee)
with col_btn3:
    st.button("➕ Add Action Item", on_click=add_action_item)
with col_btn4:
    st.button("➖ Remove Action Item", on_click=remove_action_item)
