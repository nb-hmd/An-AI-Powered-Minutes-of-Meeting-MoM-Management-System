-- ============================================================
-- Minutes of Meeting (MoM) System - Database Schema
-- PostgreSQL
-- ============================================================

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            VARCHAR(20) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'viewer')),
    profile_picture VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. MOMS TABLE (Minutes of Meeting)
-- ============================================================
CREATE TABLE IF NOT EXISTS moms (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    date_time       TIMESTAMP NOT NULL,
    venue           VARCHAR(255),
    agenda          TEXT,
    discussion      TEXT,
    decisions       TEXT,
    category        VARCHAR(50),
    department      VARCHAR(100),
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted      BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- 3. ATTENDEES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS attendees (
    id              SERIAL PRIMARY KEY,
    mom_id          INTEGER NOT NULL REFERENCES moms(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    role            VARCHAR(50),
    email           VARCHAR(100),
    department      VARCHAR(100)
);

-- ============================================================
-- 4. ACTION ITEMS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS action_items (
    id              SERIAL PRIMARY KEY,
    mom_id          INTEGER NOT NULL REFERENCES moms(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    assigned_to     VARCHAR(100),
    deadline        DATE,
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    status_comment  TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. ATTACHMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS attachments (
    id              SERIAL PRIMARY KEY,
    mom_id          INTEGER NOT NULL REFERENCES moms(id) ON DELETE CASCADE,
    filename        VARCHAR(255) NOT NULL,
    file_path       VARCHAR(500) NOT NULL,
    file_type       VARCHAR(20),
    file_size       BIGINT,
    uploaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. ACTIVITY LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username        VARCHAR(50),
    action          VARCHAR(100) NOT NULL,
    details         TEXT,
    ip_address      VARCHAR(45),
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. TEMPLATES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS templates (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50),
    content         JSONB NOT NULL DEFAULT '{}',
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. ACTION ITEM STATUS HISTORY TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS action_item_status_history (
    id              SERIAL PRIMARY KEY,
    action_item_id  INTEGER NOT NULL REFERENCES action_items(id) ON DELETE CASCADE,
    old_status      VARCHAR(20),
    new_status      VARCHAR(20) NOT NULL,
    comment         TEXT DEFAULT '',
    changed_by      VARCHAR(100),
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_moms_created_by ON moms(created_by);
CREATE INDEX IF NOT EXISTS idx_moms_date_time ON moms(date_time);
CREATE INDEX IF NOT EXISTS idx_moms_is_deleted ON moms(is_deleted);
CREATE INDEX IF NOT EXISTS idx_moms_title ON moms(title);
CREATE INDEX IF NOT EXISTS idx_attendees_mom_id ON attendees(mom_id);
CREATE INDEX IF NOT EXISTS idx_action_items_mom_id ON action_items(mom_id);
CREATE INDEX IF NOT EXISTS idx_action_items_status ON action_items(status);
CREATE INDEX IF NOT EXISTS idx_action_items_assigned ON action_items(assigned_to);
CREATE INDEX IF NOT EXISTS idx_action_items_deadline ON action_items(deadline);
CREATE INDEX IF NOT EXISTS idx_attachments_mom_id ON attachments(mom_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_aish_action_item_id ON action_item_status_history(action_item_id);
CREATE INDEX IF NOT EXISTS idx_aish_changed_at ON action_item_status_history(changed_at);

-- ============================================================
-- DEFAULT ADMIN USER
-- Password: admin123 (bcrypt hashed)
-- ============================================================
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES (
    'admin',
    'admin@momsystem.com',
    '$2b$12$r/jAza2XV7DYZlY/YexpauDy42gn.pvZUtQBtJV4KCZpZ50nrAlWy',
    'System Administrator',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- DEFAULT TEMPLATES
-- ============================================================
INSERT INTO templates (name, category, content) VALUES
(
    'Project Meeting',
    'project',
    '{
        "agenda": "1. Project Status Update\n2. Milestones Review\n3. Blockers & Issues\n4. Next Steps",
        "discussion": "",
        "decisions": "",
        "default_roles": ["Project Manager", "Developer", "Designer", "QA Engineer"]
    }'::jsonb
),
(
    'Client Meeting',
    'client',
    '{
        "agenda": "1. Welcome & Introductions\n2. Project Progress Demo\n3. Client Feedback\n4. Timeline Discussion\n5. Action Items",
        "discussion": "",
        "decisions": "",
        "default_roles": ["Account Manager", "Project Lead", "Client Representative"]
    }'::jsonb
),
(
    'Review Meeting',
    'review',
    '{
        "agenda": "1. Sprint Review\n2. Completed Tasks\n3. Pending Items\n4. Performance Metrics\n5. Improvements",
        "discussion": "",
        "decisions": "",
        "default_roles": ["Team Lead", "Team Member", "Stakeholder"]
    }'::jsonb
)
ON CONFLICT DO NOTHING;
