-- ============================================================
-- Migration 002: Live Meeting Recordings Table
-- Run: psql -U postgres -d mom_system -f database/migrations/002_live_recording.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS meeting_recordings (
    id              SERIAL PRIMARY KEY,
    mom_id          INTEGER REFERENCES moms(id) ON DELETE SET NULL,
    transcript_text TEXT,
    ai_outcome      TEXT,
    recording_duration_seconds INTEGER DEFAULT 0,
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meeting_recordings_mom_id   ON meeting_recordings(mom_id);
CREATE INDEX IF NOT EXISTS idx_meeting_recordings_created_by ON meeting_recordings(created_by);
CREATE INDEX IF NOT EXISTS idx_meeting_recordings_created_at ON meeting_recordings(created_at);
