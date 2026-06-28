-- ============================================================
-- Migration: Action Item Tracker & Status Update
-- Adds overdue status, status comment, and status history table
-- ============================================================

-- 1. Extend the status CHECK constraint to include 'overdue'
ALTER TABLE action_items DROP CONSTRAINT IF EXISTS action_items_status_check;
ALTER TABLE action_items ADD CONSTRAINT action_items_status_check
    CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue'));

-- 2. Add status_comment column for assignee notes
ALTER TABLE action_items ADD COLUMN IF NOT EXISTS status_comment TEXT DEFAULT '';

-- 3. Create status history table to track every status change
CREATE TABLE IF NOT EXISTS action_item_status_history (
    id              SERIAL PRIMARY KEY,
    action_item_id  INTEGER NOT NULL REFERENCES action_items(id) ON DELETE CASCADE,
    old_status      VARCHAR(20),
    new_status      VARCHAR(20) NOT NULL,
    comment         TEXT DEFAULT '',
    changed_by      VARCHAR(100),
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Indexes for performance
CREATE INDEX IF NOT EXISTS idx_aish_action_item_id ON action_item_status_history(action_item_id);
CREATE INDEX IF NOT EXISTS idx_aish_changed_at ON action_item_status_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_action_items_deadline ON action_items(deadline);
