"""
🎙️ Live Meeting Recording Page
Records a live meeting via browser microphone, transcribes with OpenAI Whisper,
then summarizes the full transcript into a complete MoM using gpt-4o-mini.
The form is auto-filled with title, agenda, discussion, decisions, action items,
and overall outcome — ready to review, edit, and save.
"""

import streamlit as st
from datetime import datetime, date, time as dtime
from services.auth_service import AuthService
from services.ai_service import AIService
from services.speech_service import SpeechService
from services.mom_service import MoMService
from utils.constants import MEETING_CATEGORIES
from utils.theme import apply_theme
from utils.sidebar import show_sidebar

# Require authentication
AuthService.require_auth()
apply_theme()
show_sidebar()


# ============================================================
# Custom CSS — Premium UI  (theme-aware)
# ============================================================
_dark = st.session_state.get("dark_mode", True)
_step_bg      = "linear-gradient(145deg, #16213e, #0f3460)" if _dark else "linear-gradient(145deg, #ffffff, #f8f9ff)"
_step_border  = "rgba(102,126,234,0.25)"
_step_shadow  = "rgba(0,0,0,0.4)" if _dark else "rgba(0,0,0,0.08)"
_step_title   = "#e2e8f0" if _dark else "#2d3748"
_action_bg    = "#16213e" if _dark else "#ffffff"
_action_bdr   = "rgba(255,255,255,0.08)" if _dark else "#e2e8f0"
_action_task  = "#e2e8f0" if _dark else "#2d3748"
_action_meta  = "#a0aec0" if _dark else "#718096"
_save_sec_h3  = "#e2e8f0" if _dark else "#4a5568"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Recording hero banner */
    .rec-hero {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102,126,234,0.35);
        position: relative;
        overflow: hidden;
    }}
    .rec-hero::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(102,126,234,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .rec-hero h1 {{ margin: 0; font-size: 2rem; font-weight: 700; font-family: 'Inter', sans-serif; }}
    .rec-hero p  {{ margin: 0.5rem 0 0; opacity: 0.8; font-size: 1rem; }}

    /* Step cards */
    .step-card {{
        background: {_step_bg};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px {_step_shadow};
        border: 1px solid {_step_border};
        margin-bottom: 1.5rem;
    }}
    .step-number {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 1rem;
        margin-right: 0.8rem;
    }}
    .step-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {_step_title};
        display: inline;
        vertical-align: middle;
    }}

    /* Transcript box — intentionally terminal-dark in all modes */
    .transcript-box {{
        background: #0d1117;
        color: #58a6ff;
        border-radius: 12px;
        padding: 1.2rem;
        font-family: 'Courier New', monospace;
        font-size: 0.88rem;
        line-height: 1.7;
        max-height: 280px;
        overflow-y: auto;
        border: 1px solid #30363d;
        margin-top: 0.8rem;
    }}

    /* AI summary card */
    .ai-result-card {{
        background: linear-gradient(135deg, #f0fff4, #e6fffa);
        border: 1px solid #68d391;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.15);
    }}
    .ai-result-card h4 {{ color: #276749; margin: 0 0 0.8rem; }}

    /* Outcome badge */
    .outcome-badge {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }}

    /* Action item row */
    .ai-action-row {{
        background: {_action_bg};
        border: 1px solid {_action_bdr};
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }}
    .ai-action-row .task {{ font-weight: 600; color: {_action_task}; }}
    .ai-action-row .meta {{ color: {_action_meta}; font-size: 0.82rem; margin-top: 0.2rem; }}

    /* Status pill */
    .status-pill {{
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        background: #c6f6d5;
        color: #276749;
    }}

    /* Save form */
    .save-section {{
        background: linear-gradient(145deg, #667eea10, #764ba210);
        border: 2px dashed #667eea40;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }}
    .save-section h3 {{ color: {_save_sec_h3}; margin-top: 0; }}

    /* Pulse animation for recording indicator */
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.6); }}
        70%  {{ box-shadow: 0 0 0 12px rgba(229, 62, 62, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }}
    }}
    .recording-dot {{
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #e53e3e;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 6px;
        vertical-align: middle;
    }}

    /* Divider */
    .fancy-divider {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# Hero Banner
# ============================================================
st.markdown("""
<div class="rec-hero">
    <h1>🎙️ Live Meeting Recording</h1>
    <p>Record your meeting → Auto-transcribe with Whisper → Summarize with AI → Save as MoM</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Session State Init
# ============================================================
for key, default in {
    "rec_transcript": "",
    "rec_title": "",
    "rec_agenda": "",
    "rec_discussion": "",
    "rec_decisions": "",
    "rec_action_items": [],
    "rec_outcome": "",
    "rec_summarized": False,
    "rec_transcribed": False,
    "rec_attendees_count": 1,
    "rec_action_items_count": 1,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# STEP 1 — Record Audio
# ============================================================
st.markdown("""
<div class="step-card">
    <span class="step-number">1</span>
    <span class="step-title">Record Your Meeting</span>
</div>
""", unsafe_allow_html=True)

st.info(
    "🎙️ Click the **microphone button** below to start recording directly from your browser. "
    "When the meeting is done, stop recording. The audio will be ready for transcription."
)

audio_value = st.audio_input(
    "🔴 Click to start recording your meeting",
    key="live_audio_recorder"
)

if audio_value:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin:0.5rem 0 1rem;">
        <span class="recording-dot"></span>
        <span style="color:#e53e3e; font-weight:600;">Recording captured! Ready to transcribe.</span>
    </div>
    """, unsafe_allow_html=True)
    st.audio(audio_value)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ============================================================
# STEP 2 — Transcribe with Whisper
# ============================================================
st.markdown("""
<div class="step-card">
    <span class="step-number">2</span>
    <span class="step-title">Transcribe with OpenAI Whisper</span>
</div>
""", unsafe_allow_html=True)

if not audio_value:
    st.warning("⬆️ Please record your meeting first (Step 1).")
else:
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.caption("Whisper AI will convert your recorded audio into accurate text in seconds.")
    with col_t2:
        transcribe_btn = st.button(
            "🎙️ Transcribe Now",
            key="btn_transcribe_live",
            use_container_width=True,
            type="primary"
        )

    if transcribe_btn:
        with st.spinner("🎙️ Transcribing your recording with OpenAI Whisper..."):
            result = SpeechService.transcribe_audio(
                audio_value,
                user_id=st.session_state.get("user_id")
            )

        if result["success"]:
            st.session_state.rec_transcript = result["text"]
            st.session_state.rec_transcribed = True
            st.session_state.rec_summarized = False  # Reset summary on new transcription
            st.success("✅ Transcription complete!")
            st.rerun()
        else:
            st.error(f"❌ Transcription failed: {result['message']}")

# Show transcript if available
if st.session_state.rec_transcribed and st.session_state.rec_transcript:
    word_count = len(st.session_state.rec_transcript.split())
    st.markdown(f"**📄 Transcript** — {word_count} words")
    st.markdown(
        f'<div class="transcript-box">{st.session_state.rec_transcript}</div>',
        unsafe_allow_html=True
    )
    # Allow manual editing
    with st.expander("✏️ Edit transcript (optional)", expanded=False):
        edited_transcript = st.text_area(
            "You can correct any transcription errors before summarizing:",
            value=st.session_state.rec_transcript,
            height=200,
            key="transcript_editor"
        )
        if st.button("💾 Apply Edits", key="apply_transcript_edits"):
            st.session_state.rec_transcript = edited_transcript
            st.session_state.rec_summarized = False
            st.success("✅ Transcript updated.")
            st.rerun()

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ============================================================
# STEP 3 — Summarize with AI
# ============================================================
st.markdown("""
<div class="step-card">
    <span class="step-number">3</span>
    <span class="step-title">Summarize Meeting with AI (gpt-4o-mini)</span>
</div>
""", unsafe_allow_html=True)

if not st.session_state.rec_transcribed or not st.session_state.rec_transcript:
    st.warning("⬆️ Please transcribe your recording first (Step 2).")
else:
    st.info(
        "🤖 The AI will analyze your full transcript and extract: **Meeting Title**, **Agenda**, "
        "**Discussion Points**, **Key Decisions**, **Action Items** (with assigned persons & deadlines), "
        "and **Overall Meeting Outcome**."
    )

    summarize_btn = st.button(
        "🤖 Summarize Meeting",
        key="btn_summarize_live",
        use_container_width=True,
        type="primary"
    )

    if summarize_btn:
        with st.spinner("🤖 AI is analyzing your meeting transcript... This may take a moment."):
            result = AIService.summarize_live_recording(
                transcript=st.session_state.rec_transcript,
                user_id=st.session_state.get("user_id")
            )

        if result["success"]:
            # Store everything in session state
            st.session_state.rec_title = result["title"]
            st.session_state.rec_agenda = result["agenda"]
            st.session_state.rec_discussion = result["discussion"]
            st.session_state.rec_decisions = result["decisions"]
            st.session_state.rec_action_items = result["action_items"]
            st.session_state.rec_outcome = result["outcome"]
            st.session_state.rec_summarized = True
            st.session_state.rec_action_items_count = max(
                len(result["action_items"]), 1
            )
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"❌ {result['message']}")

    # Show AI summary results
    if st.session_state.rec_summarized:
        st.markdown("### 🧠 AI Summary Results")

        # Meeting Title
        st.markdown(f"""
        <div class="ai-result-card">
            <h4>📌 Suggested Meeting Title</h4>
            <div style="font-size:1.2rem; font-weight:700; color:#2d3748;">
                {st.session_state.rec_title or "—"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Agenda + Discussion side by side
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**📋 Agenda Topics**")
            st.markdown(st.session_state.rec_agenda or "_None extracted_")
        with col_b:
            st.markdown("**✅ Decisions Made**")
            st.markdown(st.session_state.rec_decisions or "_None extracted_")

        st.markdown("**💬 Discussion Summary**")
        st.info(st.session_state.rec_discussion or "_No discussion extracted_")

        # Action Items
        if st.session_state.rec_action_items:
            st.markdown(f"**🎯 Action Items ({len(st.session_state.rec_action_items)} extracted)**")
            for item in st.session_state.rec_action_items:
                desc = item.get("description", "")
                assigned = item.get("assigned_to", "TBD")
                deadline = item.get("deadline", "TBD")
                st.markdown(f"""
                <div class="ai-action-row">
                    <div class="task">🎯 {desc}</div>
                    <div class="meta">👤 {assigned} &nbsp;•&nbsp; 📅 {deadline}</div>
                </div>
                """, unsafe_allow_html=True)

        # Outcome
        if st.session_state.rec_outcome:
            st.markdown(f"""
            <div class="outcome-badge">
                <strong>🏁 Meeting Outcome:</strong><br>
                {st.session_state.rec_outcome}
            </div>
            """, unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ============================================================
# STEP 4 — Review, Edit & Save MoM
# ============================================================
st.markdown("""
<div class="step-card">
    <span class="step-number">4</span>
    <span class="step-title">Review, Edit & Save Minutes of Meeting</span>
</div>
""", unsafe_allow_html=True)

if not st.session_state.rec_summarized:
    st.warning("⬆️ Please summarize your meeting first (Step 3) to auto-fill the form below.")
    show_empty_form = st.checkbox("Or fill the form manually without AI", value=False)
    if not show_empty_form:
        st.stop()
else:
    st.success("✅ **Form pre-filled from AI summary.** Review each field carefully, make any corrections, then save.")


# ---- Helper callbacks ----
def add_rec_attendee():
    st.session_state.rec_attendees_count += 1

def remove_rec_attendee():
    if st.session_state.rec_attendees_count > 1:
        st.session_state.rec_attendees_count -= 1

def add_rec_action():
    st.session_state.rec_action_items_count += 1

def remove_rec_action():
    if st.session_state.rec_action_items_count > 1:
        st.session_state.rec_action_items_count -= 1


# ---- MoM Form ----
st.markdown('<div class="save-section">', unsafe_allow_html=True)
st.markdown("### 📋 Meeting Details")

with st.form("live_recording_mom_form", clear_on_submit=False):

    # --- Basic Info ---
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "📌 Meeting Title *",
            value=st.session_state.rec_title,
            placeholder="Auto-filled from AI summary"
        )
        meeting_date = st.date_input("📅 Meeting Date *", value=date.today())
        venue = st.text_input("📍 Venue / Location", placeholder="e.g., Conference Room / Zoom")
    with col2:
        category = st.selectbox("📁 Category", MEETING_CATEGORIES)
        meeting_time = st.time_input("⏰ Meeting Time", value=dtime(10, 0))
        department = st.text_input("🏢 Department", placeholder="e.g., Engineering")

    st.divider()

    # --- Content (AI pre-filled) ---
    st.markdown("### 📝 Meeting Content")
    agenda = st.text_area(
        "📋 Agenda",
        value=st.session_state.rec_agenda,
        height=120,
        placeholder="Topics discussed during the meeting..."
    )
    discussion = st.text_area(
        "💬 Discussion Points",
        value=st.session_state.rec_discussion,
        height=200,
        placeholder="Summary of all key discussion points..."
    )
    decisions = st.text_area(
        "✅ Decisions Taken",
        value=st.session_state.rec_decisions,
        height=120,
        placeholder="Decisions made during the meeting..."
    )

    # --- Outcome (extra field from Live Recording AI) ---
    if st.session_state.rec_outcome:
        outcome_text = st.text_area(
            "🏁 Meeting Outcome / Result",
            value=st.session_state.rec_outcome,
            height=100,
            help="Overall result of the meeting — auto-generated by AI from your recording."
        )
    else:
        outcome_text = ""

    st.divider()

    # --- Attendees ---
    st.markdown("### 👥 Attendees")
    attendees_data = []
    for i in range(st.session_state.rec_attendees_count):
        st.markdown(f"**Attendee {i + 1}**")
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            a_name = st.text_input("Name", key=f"rec_att_name_{i}", placeholder="Full name")
        with ac2:
            a_role = st.text_input("Role / Title", key=f"rec_att_role_{i}", placeholder="e.g., Developer")
        with ac3:
            a_email = st.text_input("Email", key=f"rec_att_email_{i}", placeholder="email@company.com")
        with ac4:
            a_dept = st.text_input("Department", key=f"rec_att_dept_{i}", placeholder="e.g., Engineering")
        attendees_data.append({"name": a_name, "role": a_role, "email": a_email, "department": a_dept})

    st.divider()

    # --- Action Items (AI pre-filled) ---
    st.markdown("### 🎯 Action Items")
    ai_items = st.session_state.rec_action_items or []
    action_items_data = []

    for i in range(st.session_state.rec_action_items_count):
        st.markdown(f"**Action Item {i + 1}**")

        # Pre-fill from AI
        ai_item = ai_items[i] if i < len(ai_items) else {}
        ai_desc_val = ai_item.get("description", "")
        ai_assigned_val = ai_item.get("assigned_to", "")
        if ai_assigned_val == "TBD":
            ai_assigned_val = ""

        # Parse deadline from AI if it's a real date
        ai_deadline_val = None
        raw_deadline = ai_item.get("deadline", "TBD")
        if raw_deadline and raw_deadline != "TBD":
            try:
                from dateutil import parser as dateutil_parser
                ai_deadline_val = dateutil_parser.parse(raw_deadline, fuzzy=True).date()
            except Exception:
                ai_deadline_val = None

        ic1, ic2, ic3 = st.columns([3, 2, 2])
        with ic1:
            ai_desc = st.text_input(
                "Task Description",
                key=f"rec_ai_desc_{i}",
                value=ai_desc_val,
                placeholder="What needs to be done?"
            )
        with ic2:
            ai_person = st.text_input(
                "Assigned To",
                key=f"rec_ai_person_{i}",
                value=ai_assigned_val,
                placeholder="Person responsible"
            )
        with ic3:
            ai_deadline = st.date_input(
                "Deadline",
                key=f"rec_ai_deadline_{i}",
                value=ai_deadline_val
            )
        action_items_data.append({
            "description": ai_desc,
            "assigned_to": ai_person,
            "deadline": ai_deadline,
            "status": "pending"
        })

    st.divider()

    # --- Transcript attachment note ---
    if st.session_state.rec_transcript:
        st.info(
            f"📄 **Full transcript** ({len(st.session_state.rec_transcript.split())} words) "
            "will be saved alongside this MoM record for reference."
        )

    # --- Submit ---
    save_btn = st.form_submit_button("💾 Save Minutes of Meeting", use_container_width=True, type="primary")

    if save_btn:
        # Validate
        if not title or not title.strip():
            st.error("❌ Meeting Title is required.")
        else:
            meeting_datetime = datetime.combine(meeting_date, meeting_time)

            # Merge outcome into decisions if present
            final_decisions = decisions.strip()
            if outcome_text and outcome_text.strip():
                if final_decisions:
                    final_decisions += f"\n\n**Meeting Outcome:**\n{outcome_text.strip()}"
                else:
                    final_decisions = f"**Meeting Outcome:**\n{outcome_text.strip()}"

            # Merge transcript into discussion for record-keeping
            final_discussion = discussion.strip()
            if st.session_state.rec_transcript:
                final_discussion += (
                    f"\n\n---\n**Full Meeting Transcript (auto-generated):**\n"
                    f"{st.session_state.rec_transcript}"
                )

            valid_attendees = [a for a in attendees_data if a["name"].strip()]
            valid_actions = [a for a in action_items_data if a["description"].strip()]

            with st.spinner("💾 Saving your Minutes of Meeting..."):
                result = MoMService.create_mom(
                    title=title.strip(),
                    date_time=meeting_datetime,
                    venue=venue.strip(),
                    agenda=agenda.strip(),
                    discussion=final_discussion,
                    decisions=final_decisions,
                    category=category,
                    department=department.strip(),
                    created_by=st.session_state.get("user_id"),
                    attendees=valid_attendees,
                    action_items=valid_actions,
                    uploaded_files=None,
                )

            if result["success"]:
                st.success(f"✅ Meeting saved successfully! MoM ID: **{result['mom_id']}**")
                st.balloons()

                # Try to save recording metadata
                try:
                    from config.database import get_connection
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO meeting_recordings
                                (mom_id, transcript_text, ai_outcome, created_by)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            result["mom_id"],
                            st.session_state.rec_transcript,
                            st.session_state.rec_outcome,
                            st.session_state.get("user_id")
                        ))
                        conn.commit()
                        cursor.close()
                        conn.close()
                except Exception:
                    pass  # Recording metadata save is optional

                # Clear session state
                for k in ["rec_transcript", "rec_title", "rec_agenda", "rec_discussion",
                          "rec_decisions", "rec_action_items", "rec_outcome",
                          "rec_summarized", "rec_transcribed"]:
                    if k == "rec_action_items":
                        st.session_state[k] = []
                    elif k in ("rec_summarized", "rec_transcribed"):
                        st.session_state[k] = False
                    else:
                        st.session_state[k] = ""
                st.session_state.rec_attendees_count = 1
                st.session_state.rec_action_items_count = 1

                st.info("💡 View your saved MoM in **View MoMs** or track action items in **Action Tracker**.")
            else:
                st.error(f"❌ Failed to save: {result['message']}")

st.markdown("</div>", unsafe_allow_html=True)


# ---- Attendee / Action Item controls (outside form) ----
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
with btn_col1:
    st.button("➕ Add Attendee", on_click=add_rec_attendee, key="rec_add_att")
with btn_col2:
    st.button("➖ Remove Attendee", on_click=remove_rec_attendee, key="rec_rem_att")
with btn_col3:
    st.button("➕ Add Action Item", on_click=add_rec_action, key="rec_add_act")
with btn_col4:
    st.button("➖ Remove Action Item", on_click=remove_rec_action, key="rec_rem_act")


# ============================================================
# Footer
# ============================================================
st.markdown("""
<div style="text-align: center; color: #a0aec0; font-size: 0.82rem;
            padding: 2rem 0 1rem; border-top: 1px solid #e2e8f0; margin-top: 2rem;">
    🎙️ Live Meeting Recording • Powered by OpenAI Whisper + gpt-4o-mini
</div>
""", unsafe_allow_html=True)
