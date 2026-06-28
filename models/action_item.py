"""
Action Item Model - Database operations for the action_items table.
"""

from config.database import get_cursor
from datetime import datetime


class ActionItemModel:
    """Handles all database operations for the action_items table."""

    @staticmethod
    def add_action_item(mom_id, description, assigned_to="", deadline=None, status="pending"):
        """Add an action item to a MoM."""
        query = """
            INSERT INTO action_items (mom_id, description, assigned_to, deadline, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, mom_id, description, assigned_to, deadline, status
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id, description, assigned_to, deadline, status))
                return cur.fetchone()
        except Exception as e:
            print(f"Error adding action item: {e}")
            return None

    @staticmethod
    def add_multiple_action_items(mom_id, items_list):
        """Add multiple action items at once. items_list = list of dicts."""
        results = []
        for item in items_list:
            result = ActionItemModel.add_action_item(
                mom_id=mom_id,
                description=item.get("description", ""),
                assigned_to=item.get("assigned_to", ""),
                deadline=item.get("deadline"),
                status=item.get("status", "pending"),
            )
            if result:
                results.append(result)
        return results

    @staticmethod
    def get_action_items_by_mom(mom_id):
        """Fetch all action items for a specific MoM."""
        query = """
            SELECT id, mom_id, description, assigned_to, deadline, status,
                   created_at, updated_at
            FROM action_items WHERE mom_id = %s ORDER BY id
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching action items: {e}")
            return []

    @staticmethod
    def update_action_item_status(item_id, status):
        """Update the status of an action item."""
        query = """
            UPDATE action_items SET status = %s, updated_at = %s
            WHERE id = %s RETURNING *
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (status, datetime.now(), item_id))
                return cur.fetchone()
        except Exception as e:
            print(f"Error updating action item: {e}")
            return None

    @staticmethod
    def delete_action_items_by_mom(mom_id):
        """Delete all action items for a MoM (used before re-adding on edit)."""
        query = "DELETE FROM action_items WHERE mom_id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return True
        except Exception as e:
            print(f"Error deleting action items: {e}")
            return False

    @staticmethod
    def delete_action_item(item_id):
        """Delete a single action item."""
        query = "DELETE FROM action_items WHERE id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (item_id,))
                return True
        except Exception as e:
            print(f"Error deleting action item: {e}")
            return False

    @staticmethod
    def get_pending_count():
        """Get total count of pending action items."""
        query = "SELECT COUNT(*) as count FROM action_items WHERE status = 'pending'"
        try:
            with get_cursor() as cur:
                cur.execute(query)
                r = cur.fetchone()
                return r["count"] if r else 0
        except Exception:
            return 0

    @staticmethod
    def get_completed_count():
        """Get total count of completed action items."""
        query = "SELECT COUNT(*) as count FROM action_items WHERE status = 'completed'"
        try:
            with get_cursor() as cur:
                cur.execute(query)
                r = cur.fetchone()
                return r["count"] if r else 0
        except Exception:
            return 0

    @staticmethod
    def get_upcoming_deadlines(limit=10):
        """Get upcoming action item deadlines."""
        query = """
            SELECT ai.*, m.title as mom_title
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.status != 'completed'
              AND ai.deadline IS NOT NULL
              AND ai.deadline >= CURRENT_DATE
              AND m.is_deleted = FALSE
            ORDER BY ai.deadline ASC
            LIMIT %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
        except Exception:
            return []

    # ==============================================================
    # F12 & F14 — Action Item Tracker & Status Update Methods
    # ==============================================================

    @staticmethod
    def get_all_action_items(status_filter=None, assigned_filter=None,
                             deadline_start=None, deadline_end=None,
                             sort_by="deadline", sort_order="ASC"):
        """Fetch ALL action items across all meetings with filters.
        Excludes items belonging to soft-deleted MoMs.
        """
        conditions = ["m.is_deleted = FALSE"]
        params = []

        if status_filter and isinstance(status_filter, list) and len(status_filter) > 0:
            placeholders = ", ".join(["%s"] * len(status_filter))
            conditions.append(f"ai.status IN ({placeholders})")
            params.extend(status_filter)

        if assigned_filter:
            conditions.append("ai.assigned_to ILIKE %s")
            params.append(f"%{assigned_filter}%")

        if deadline_start:
            conditions.append("ai.deadline >= %s")
            params.append(deadline_start)

        if deadline_end:
            conditions.append("ai.deadline <= %s")
            params.append(deadline_end)

        where = " AND ".join(conditions)

        allowed_sort = {"deadline", "status", "assigned_to", "created_at", "updated_at"}
        if sort_by not in allowed_sort:
            sort_by = "deadline"
        sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"

        query = f"""
            SELECT ai.*, m.title as mom_title
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE {where}
            ORDER BY
                CASE WHEN ai.deadline IS NULL THEN 1 ELSE 0 END,
                ai.{sort_by} {sort_order}
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching all action items: {e}")
            return []

    @staticmethod
    def get_action_items_by_person(assigned_to):
        """Fetch action items assigned to a specific person (exact match)."""
        query = """
            SELECT ai.*, m.title as mom_title
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.assigned_to ILIKE %s
              AND m.is_deleted = FALSE
            ORDER BY
                CASE WHEN ai.deadline IS NULL THEN 1 ELSE 0 END,
                ai.deadline ASC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (assigned_to,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching items by person: {e}")
            return []

    @staticmethod
    def get_overdue_items():
        """Get items that are past deadline and not completed."""
        query = """
            SELECT ai.*, m.title as mom_title
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.deadline < CURRENT_DATE
              AND ai.status NOT IN ('completed', 'overdue')
              AND m.is_deleted = FALSE
            ORDER BY ai.deadline ASC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching overdue items: {e}")
            return []

    @staticmethod
    def mark_overdue_items():
        """Bulk-update: set status='overdue' for items past deadline
        that are still pending or in_progress."""
        query = """
            UPDATE action_items
            SET status = 'overdue', updated_at = CURRENT_TIMESTAMP
            WHERE deadline < CURRENT_DATE
              AND status IN ('pending', 'in_progress')
              AND mom_id IN (SELECT id FROM moms WHERE is_deleted = FALSE)
            RETURNING id
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [r["id"] for r in results] if results else []
        except Exception as e:
            print(f"Error marking overdue items: {e}")
            return []

    @staticmethod
    def update_action_item_with_comment(item_id, new_status, comment="", changed_by=""):
        """Update status with comment and record in status history table."""
        # First, get current status for history
        get_query = "SELECT status FROM action_items WHERE id = %s"
        update_query = """
            UPDATE action_items
            SET status = %s, status_comment = %s, updated_at = %s
            WHERE id = %s
            RETURNING *
        """
        history_query = """
            INSERT INTO action_item_status_history
                (action_item_id, old_status, new_status, comment, changed_by)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with get_cursor() as cur:
                # Get current status
                cur.execute(get_query, (item_id,))
                current = cur.fetchone()
                old_status = current["status"] if current else "unknown"

                # Update the action item
                cur.execute(update_query, (new_status, comment, datetime.now(), item_id))
                result = cur.fetchone()

                # Insert history record
                cur.execute(history_query, (item_id, old_status, new_status, comment, changed_by))

                return result
        except Exception as e:
            print(f"Error updating action item with comment: {e}")
            return None

    @staticmethod
    def get_action_item_by_id(item_id):
        """Fetch a single action item with its MoM title."""
        query = """
            SELECT ai.*, m.title as mom_title
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.id = %s AND m.is_deleted = FALSE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (item_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching action item by ID: {e}")
            return None

    @staticmethod
    def get_status_history(item_id):
        """Fetch all status change history for an action item."""
        query = """
            SELECT * FROM action_item_status_history
            WHERE action_item_id = %s
            ORDER BY changed_at DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (item_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching status history: {e}")
            return []

    @staticmethod
    def get_distinct_assigned_persons():
        """Get unique assigned_to values for filter dropdowns."""
        query = """
            SELECT DISTINCT ai.assigned_to
            FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.assigned_to IS NOT NULL
              AND ai.assigned_to != ''
              AND m.is_deleted = FALSE
            ORDER BY ai.assigned_to
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [r["assigned_to"] for r in results] if results else []
        except Exception as e:
            print(f"Error fetching assigned persons: {e}")
            return []

    @staticmethod
    def get_overdue_count():
        """Get total count of overdue action items."""
        query = """
            SELECT COUNT(*) as count FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.status = 'overdue'
              AND m.is_deleted = FALSE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                r = cur.fetchone()
                return r["count"] if r else 0
        except Exception:
            return 0

    @staticmethod
    def get_in_progress_count():
        """Get total count of in-progress action items."""
        query = """
            SELECT COUNT(*) as count FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE ai.status = 'in_progress'
              AND m.is_deleted = FALSE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                r = cur.fetchone()
                return r["count"] if r else 0
        except Exception:
            return 0

    @staticmethod
    def get_total_action_items_count():
        """Get total count of all action items."""
        query = """
            SELECT COUNT(*) as count FROM action_items ai
            JOIN moms m ON ai.mom_id = m.id
            WHERE m.is_deleted = FALSE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                r = cur.fetchone()
                return r["count"] if r else 0
        except Exception:
            return 0

