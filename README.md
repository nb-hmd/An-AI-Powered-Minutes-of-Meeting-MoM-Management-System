# 📝 AI-Powered Minutes of Meeting (MoM) Management System

> **A production-ready, intelligent meeting documentation platform** that transforms how teams record, manage, and act on meeting outcomes — powered by OpenAI GPT-4o-mini, Whisper speech-to-text, and a real-time analytics dashboard.

---

## 🎬 Watch the Demo

> **See the full system in action before reading anything else!**

<div align="center">
  <a href="https://drive.google.com/file/d/16080Dm2XhPgwbSMklzvZNQ0f_kWmBkYF/view?usp=drivesdk" target="_blank">
    <img src="https://drive.google.com/thumbnail?id=16080Dm2XhPgwbSMklzvZNQ0f_kWmBkYF&sz=w1280"
         alt="▶️ Watch Demo Video — AI-Powered Minutes of Meeting System"
         width="780"
         style="border-radius:12px; box-shadow:0 8px 32px rgba(0,0,0,0.3);"/>
  </a>
  <br/><br/>
  <a href="https://drive.google.com/file/d/16080Dm2XhPgwbSMklzvZNQ0f_kWmBkYF/view?usp=drivesdk" target="_blank">
    <img src="https://img.shields.io/badge/▶%20Watch%20Full%20Demo-2%20min%207%20sec-red?style=for-the-badge&logo=google-drive&logoColor=white" alt="Watch Demo"/>
  </a>
</div>

> 🎥 **Click the thumbnail or button above** to watch the 2-minute demo on Google Drive.

---

## 🌟 What Is This Project?

The **AI-Powered Minutes of Meeting (MoM) Management System** is a comprehensive, web application designed to eliminate the pain of manual meeting documentation. Whether you are a project manager, team lead, or executive, this system gives you a single platform to:

- **Record meetings live** directly from your browser microphone
- **Auto-transcribe audio** using OpenAI Whisper with high accuracy
- **Auto-generate complete MoMs** using GPT-4o-mini — title, agenda, discussion points, decisions, and action items extracted intelligently from the raw transcript
- **Manage, search, and export** all meeting records in PDF or DOCX format
- **Track action items** with deadlines, assignees, and completion status
- **Visualize meeting trends** through an interactive analytics dashboard

This system is built with **Streamlit** (Python web framework), **PostgreSQL** (relational database), and the **OpenAI API**, providing a clean, responsive UI that supports both **Dark Mode** and **Light Mode** across all pages.

---

## ✨ Key Features at a Glance

| Category                      | Features                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------- |
| 🤖**AI Automation**     | Live transcription, MoM generation, summarization, grammar fix, quality scoring |
| 📋**MoM Management**    | Create, read, update, delete, archive meetings                                  |
| 👥**People Management** | Attendees with roles, departments                                               |
| ✅**Action Tracking**   | Deadlines, assignees, status updates, overdue alerts                            |
| 📊**Analytics**         | 5 interactive charts, 5 KPI cards, trend analysis                               |
| 🔍**Search & Filter**   | Full-text search, date range, department, status filters                        |
| 📄**Export**            | PDF and DOCX generation with formatted layout                                   |
| 📝**Templates**         | Reusable meeting templates by category                                          |
| 🔐**Security**          | bcrypt password hashing, role-based access control                              |
| 🎨**Themes**            | System-wide Dark Mode / Light Mode toggle                                       |
| 📎**Attachments**       | Upload PDF, DOCX, JPG, PNG, PPTX per meeting                                    |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER / USER                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │  HTTP
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                   STREAMLIT APPLICATION                        │
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ app.py   │  │ Pages    │  │ Utils     │  │ Config        │  │
│  │ (Entry)  │  │ (9 pages)│  │ theme     │  │ settings.py   │  │
│  │ Auth     │  │          │  │ sidebar   │  │ database.py   │  │
│  │ Login    │  │ Dashboard│  │ formatters│  │               │  │
│  │ Register │  │ Create   │  │ validators│  │               │  │
│  └────┬─────┘  │ View     │  └───────────┘  └───────────────┘  │
│       │        │ Search   │                                    │
│       │        │ Templates│  ┌──────────────────────────────┐  │
│       │        │ Profile  │  │        SERVICES LAYER        │  │
│       │        │ Admin    │  │                              │  │
│       │        │ Tracker  │  │  AuthService    AIService    │  │
│       │        │ Live Rec.│  │  MoMService     SpeechSvc    │  │
│       │        └──────────┘  │  AnalyticsSvc   ExportSvc    │  │
│       │                      │  ActionTrackerSvc            │  │
│       │                      └───────────────┬──────────────┘  │
└───────┼──────────────────────────────────────┼─────────────────┘
        │                                      │
        ▼                                      ▼
┌───────────────┐                  ┌───────────────────────────┐
│  PostgreSQL   │                  │     EXTERNAL APIS         │
│  Database     │                  │                           │
│               │                  │  ┌─────────────────────┐  │
│  moms         │                  │  │ OpenAI GPT-4o-mini  │  │
│  attendees    │                  │  │ (Summarization,     │  │
│  action_items │                  │  │  MoM Generation,    │  │
│  users        │                  │  │  Grammar Fix,       │  │
│  templates    │                  │  │  Quality Scoring)   │  │
│  attachments  │                  │  └─────────────────────┘  │
│  activity_log │                  │  ┌─────────────────────┐  │
│               │                  │  │ OpenAI Whisper API  │  │
└───────────────┘                  │  │ (Speech-to-Text     │  │
                                   │  │  Transcription)     │  │
                                   │  └─────────────────────┘  │
                                   └───────────────────────────┘
```

### Project Workflow

```
User Opens App
      │
      ▼
 Authenticated? ──No──► Login / Register Page
      │
     Yes
      │
      ▼
  Home Page (Quick Overview + Quick Actions)
      │
      ├──► 📊 Dashboard ──────► View KPI Cards + 5 Plotly Charts
      │
      ├──► ➕ Create MoM ──────► Manual Form Entry
      │         └──────────────► OR AI Tools (Upload notes/audio → AI fills form)
      │
      ├──► 📋 View MoMs ────────► Browse, Filter, Sort, Expand, Export, Edit, Delete
      │
      ├──► 🔍 Search ───────────► Full-text search across all meeting fields
      │
      ├──► 📝 Templates ────────► Manage reusable meeting templates
      │
      ├──► 🎯 Action Tracker ───► Track all action items across all meetings
      │
      ├──► 🎙️ Live Recording ───► Record → Transcribe → AI Generate MoM → Save
      │         Step 1: Record via browser mic
      │         Step 2: Transcribe with Whisper
      │         Step 3: AI generates complete MoM
      │         Step 4: Review, edit, and save
      │
      ├──► 👤 Profile ──────────► Update personal info & change password
      │
      └──► ⚙️ Admin Panel ──────► Manage users, roles, system activity logs
```

---

## 📱 Application Pages — Detailed Description

### 🏠 Home Page (`app.py`)

The landing page after login. It serves as the central hub of the system.

- **Welcome Banner** — Personalized greeting with the user's full name
- **Quick Overview Cards** — 4 live KPI cards: Total Meetings, This Month, Pending Actions, Completed Actions (data pulled directly from the database)
- **Quick Action Buttons** — One-click navigation to Create MoM, View MoMs, Search, Dashboard, and Live Recording
- **Getting Started Guide** — Step-by-step cards for new users explaining how to use each major feature
- **Live Feature Highlight** — Prominent callout for the AI Live Recording feature

---

### 📊 Dashboard (`pages/1_Dashboard.py`)

A full analytics page giving a bird's-eye view of all meeting activity.

**5 KPI Metric Cards:**

| Card              | Description                                |
| ----------------- | ------------------------------------------ |
| Total Meetings    | All MoMs ever recorded in the system       |
| This Month        | MoMs created in the current calendar month |
| Pending Actions   | Action items not yet completed             |
| Completed Actions | Successfully completed action items        |
| Overdue Actions   | Action items past their deadline           |

**5 Interactive Plotly Charts:**

| Chart                  | Type            | What It Shows                                                |
| ---------------------- | --------------- | ------------------------------------------------------------ |
| Meetings Per Month     | Multi-color Bar | Monthly MoM creation trend with unique color per bar         |
| Meetings by Category   | Donut           | Breakdown of meeting types (Review, Standup, Planning, etc.) |
| Action Items by Status | Donut           | Pending / In Progress / Completed / Overdue split            |
| Top Assignees          | Stacked Bar     | Team members' assigned vs completed action items             |
| MoM Creation Trend     | Spline Area     | Monthly trend with dotted average reference line             |

- All charts are **fully theme-aware** — colors, text, and backgrounds adapt to Dark/Light mode
- Each chart has a **guide description card** explaining what it shows and how to read it
- Data is **always live** from the database

**Tables:**

- **Upcoming Deadlines** — Action items with approaching due dates
- **Recent Activity Log** — Real-time audit trail of all user actions

---

### ➕ Create MoM (`pages/2_Create_MoM.py`)

The primary form for creating a new Minutes of Meeting document. Supports both manual entry and AI-assisted creation.

**Manual Fields:**

- Meeting Title, Date, Time, Venue, Department
- Meeting Category (dropdown)
- Attendees (dynamic rows — add/remove name, role, email, department)
- Agenda, Discussion Points, Decisions Made
- Action Items (dynamic rows — task, assigned to, deadline, priority)
- Overall Outcome, Follow-up Date
- File Attachments (PDF, DOCX, JPG, PNG, PPTX)

**AI Tools Panel** (right side):

| Tool                    | What It Does                                                               |
| ----------------------- | -------------------------------------------------------------------------- |
| 📤 Summarize from Notes | Paste raw notes → AI extracts agenda, discussion, decisions, action items |
| 🎵 Transcribe Audio     | Upload MP3/WAV → Whisper transcribes → GPT fills the form                |
| ✨ Fix Grammar          | AI corrects grammar in all text fields simultaneously                      |
| 📊 Quality Check        | AI scores the MoM (0–100) and lists missing or weak sections              |

- The quality report card shows a **color-coded score** (green/orange/red) with specific issue warnings
- All AI-filled fields can be manually edited before saving

---

### 📋 View MoMs (`pages/3_View_MoMs.py`)

Browse and manage all recorded Minutes of Meeting documents.

**Filtering & Sorting:**

- Filter by date range, department, meeting category, status
- Sort by date (newest/oldest), title (A-Z)
- Pagination (10 records per page)

**For Each MoM Card:**

- Title, date, venue, department, category badge
- Attendee count, action item count
- **Expand** to read full details (agenda, discussion, decisions, action items, attachments)
- **Edit** — opens the full edit form pre-populated with existing data
- **Export to PDF** — generates a formatted PDF report
- **Export to DOCX** — generates a formatted Word document
- **Delete** — soft-delete with confirmation

---

### 🔍 Search (`pages/4_Search.py`)

Powerful full-text search across all meeting records.

- Search by meeting title, description, venue, assigned person, department
- Results displayed as expandable cards with highlighted matching fields
- Instant results with meeting date, category, and action item summary

---

### 📝 Templates (`pages/5_Templates.py`)

Create and reuse standardized meeting structures.

- **View all templates** organized by category
- **Create new templates** — define reusable agenda and discussion structure
- **Apply a template** — pre-fills the Create MoM form with the template content
- **Edit and delete** existing templates
- Templates are stored in the database and available to all users

---

### 🎯 Action Tracker (`pages/8_Action_Tracker.py`)

A dedicated page to track all action items across every meeting in the system.

**Dashboard Strip:**

- Total Actions, Pending, In Progress, Completed, Overdue (live KPI cards)

**Features:**

- Filter by status (All / Pending / In Progress / Completed / Overdue), assignee, or date range
- Update action item status directly from the tracker without opening the full MoM
- Color-coded priority badges (High / Medium / Low)
- Deadline highlighting — overdue items shown in red
- Expandable rows showing which meeting the action item belongs to

---

### 🎙️ Live Recording (`pages/9_Live_Recording.py`)

The flagship AI feature — record a meeting live and get a complete MoM generated automatically.

**4-Step Workflow:**

**Step 1 — Record Your Meeting**

- Browser-native microphone capture using JavaScript Web Audio API
- Real-time recording timer display
- Start/Stop controls with visual feedback
- Audio is captured entirely in the browser — no external software needed

**Step 2 — Transcribe with OpenAI Whisper**

- Recorded audio is sent to OpenAI Whisper API
- Accurate speech-to-text transcription even with background noise
- Full transcript displayed in a terminal-style viewer
- Transcript can be manually edited before AI processing

**Step 3 — AI Generate Complete MoM**

- The full transcript is sent to GPT-4o-mini
- AI intelligently extracts:
  - Meeting title and category
  - Agenda items from the conversation
  - Full discussion summary
  - Key decisions made
  - Action items with assigned persons and deadlines
  - Overall outcome
- All extracted fields are shown in a structured review card

**Step 4 — Review, Edit & Save**

- All AI-generated content is placed into an editable form
- User can correct any AI extraction errors
- Add additional manual details (venue, department, follow-up date)
- One-click save creates the complete MoM in the database

---

### 👤 Profile (`pages/6_Profile.py`)

Personal account management page.

- View account details (username, email, full name, role, join date)
- Update full name and email
- Change password (requires current password confirmation)
- View personal activity history

---

### ⚙️ Admin Panel (`pages/7_Admin.py`)

Exclusive to users with the `admin` role.

- **User Management** — view all registered users, change roles, activate/deactivate accounts
- **System Activity Logs** — full audit trail of every action taken across the system
- **Database Statistics** — total records per table (users, MoMs, action items, templates)
- Create new users directly from the admin panel

---

## 🏗️ Technology Stack

| Layer                    | Technology         | Version | Purpose                       |
| ------------------------ | ------------------ | ------- | ----------------------------- |
| **Frontend**       | Streamlit          | 1.45.0  | Web UI framework              |
| **Database**       | PostgreSQL         | 14+     | Relational data storage       |
| **DB Driver**      | psycopg2-binary    | 2.9.10  | PostgreSQL connection         |
| **ORM**            | SQLAlchemy         | 2.0.36  | Query building                |
| **Authentication** | bcrypt             | 4.2.1   | Password hashing              |
| **Charts**         | Plotly             | 6.0.0   | Interactive visualizations    |
| **Data**           | pandas             | 2.2.3   | Data manipulation             |
| **AI — LLM**      | OpenAI GPT-4o-mini | ≥1.0.0 | Summarization, extraction     |
| **AI — STT**      | OpenAI Whisper API | ≥1.0.0 | Speech-to-text                |
| **PDF Export**     | ReportLab          | 4.4.0   | PDF generation                |
| **DOCX Export**    | python-docx        | 1.1.2   | Word document generation      |
| **Image**          | Pillow             | 11.1.0  | Image processing              |
| **Env**            | python-dotenv      | 1.0.1   | Environment variable loading  |
| **Date Parsing**   | python-dateutil    | ≥2.9.0 | AI-extracted deadline parsing |

---

## 📁 Project Structure

```
mom-system/
│
├── app.py                          # Entry point — login, register, home page
├── requirements.txt                # All Python dependencies
├── .env                            # Environment variables (DB, API keys)
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
├── config/
│   ├── database.py                 # PostgreSQL connection pool setup
│   └── settings.py                 # App name, version, constants
│
├── database/
│   └── schema.sql                  # Full PostgreSQL schema with indexes
│
├── models/                         # Database layer (raw SQL queries)
│   ├── mom.py                      # MoM CRUD operations
│   ├── action_item.py              # Action item CRUD + analytics queries
│   ├── attendee.py                 # Attendee management
│   ├── user.py                     # User account operations
│   ├── attachment.py               # File attachment handling
│   └── activity_log.py             # Audit log operations
│
├── services/                       # Business logic layer
│   ├── auth_service.py             # Login, register, session, RBAC
│   ├── ai_service.py               # OpenAI GPT calls — summarize, extract, fix
│   ├── speech_service.py           # Whisper API — audio transcription
│   ├── mom_service.py              # MoM creation, update, delete orchestration
│   ├── analytics_service.py        # Dashboard chart data queries
│   ├── action_tracker_service.py   # Action item filtering and status updates
│   └── export_service.py           # PDF and DOCX generation
│
├── pages/                          # Streamlit multipage app pages
│   ├── 1_Dashboard.py              # Analytics dashboard with 5 charts
│   ├── 2_Create_MoM.py             # Create MoM form + AI tools panel
│   ├── 3_View_MoMs.py              # Browse, filter, export, edit, delete MoMs
│   ├── 4_Search.py                 # Full-text search across meetings
│   ├── 5_Templates.py              # Meeting template management
│   ├── 6_Profile.py                # User profile and password change
│   ├── 7_Admin.py                  # Admin-only user management and logs
│   ├── 8_Action_Tracker.py         # Cross-meeting action item tracker
│   └── 9_Live_Recording.py         # AI live recording → transcription → MoM
│
├── utils/                          # Shared utilities
│   ├── theme.py                    # Dark/Light mode CSS injection
│   ├── sidebar.py                  # Shared sidebar component
│   ├── formatters.py               # Date, status, and text formatters
│   ├── validators.py               # Form validation logic
│   ├── file_handler.py             # File upload/download helpers
│   └── constants.py                # Meeting categories, priorities, etc.
│
├── templates/                      # Jinja2 / document templates
├── exports/                        # Auto-generated PDF/DOCX files
├── uploads/                        # User-uploaded attachments
└── Demo Video/
    └── Project-Demo-Video.mp4      # Full system walkthrough
```

---

## 📦 Installation & Setup

### Prerequisites

- **Python** 3.10 or higher
- **PostgreSQL** 14 or higher
- **OpenAI API Key** (for AI features — get one at [platform.openai.com](https://platform.openai.com))

### Step-by-Step Setup

**1. Clone the repository**

```bash
git clone https://github.com/nb-hmd/An-AI-Powered-Minutes-of-Meeting-MoM-Management-System.git
cd An-AI-Powered-Minutes-of-Meeting-MoM-Management-System
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

**3. Install all dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```env
# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mom_system
DB_USER=postgres
DB_PASSWORD=your_password

# OpenAI API (required for AI features)
OPENAI_API_KEY=your-openai-api-key
```

**5. Initialize the PostgreSQL database**

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE mom_system;"

# Run the schema (creates all tables, indexes, default admin account)
psql -U postgres -d mom_system -f database/schema.sql
```

**6. Run the application**

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 👥 Default Admin Account

After running the schema, a default admin account is available:

| Field    | Value        |
| -------- | ------------ |
| Username | `admin`    |
| Password | `admin123` |
| Role     | `admin`    |

> ⚠️ **Security**: Change the default admin password immediately after first login via the **Profile** page.

---

## 🤖 AI Features Configuration

All AI features require a valid **OpenAI API key** in your `.env` file.

| Feature                        | Model Used  | API Call             |
| ------------------------------ | ----------- | -------------------- |
| MoM Generation from Transcript | GPT-4o-mini | Chat Completions     |
| Summarize from Notes           | GPT-4o-mini | Chat Completions     |
| Grammar Fix                    | GPT-4o-mini | Chat Completions     |
| Quality Check & Scoring        | GPT-4o-mini | Chat Completions     |
| Speech-to-Text Transcription   | Whisper-1   | Audio Transcriptions |

> If the OpenAI API key is not set, the AI tools panel will display a friendly error message. All non-AI features of the system continue to work normally.

---

## 🎨 Theme Support

The system ships with a full **Dark Mode / Light Mode** toggle accessible from the sidebar on every page.

- **Dark Mode** (default): Deep navy color scheme (`#1a1a2e`, `#16213e`, `#0f3460`)
- **Light Mode**: Clean white and light grey scheme (`#f7f9fc`, `#ffffff`)
- All pages, charts, forms, tables, and the sidebar update instantly when the theme is switched
- Theme preference is stored in the session and persists across page navigation

---

## 🔐 Security Features

- **Password Hashing** — All passwords stored using bcrypt (salt rounds: 12)
- **Role-Based Access Control** — Admin and Viewer roles with page-level restrictions
- **Session Management** — Streamlit session_state-based authentication
- **Input Validation** — All form fields validated on both client and server side
- **Soft Delete** — Records are never permanently deleted (flagged `is_deleted = TRUE`)
- **Audit Trail** — Every create, update, delete, login, and logout is logged

---

## 📄 License

This project is developed for educational and internal use purposes.

---

## 👨‍💻 Author

Built with ❤️ using **Streamlit**, **PostgreSQL**, and **OpenAI API**.

> For questions, feedback, or contributions, please open an issue or submit a pull request.
