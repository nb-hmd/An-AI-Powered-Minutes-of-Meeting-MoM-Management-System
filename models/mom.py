"""
MoM Model - Database operations for the moms table.
"""

from config.database import get_cursor
from datetime import datetime


class MoMModel:
    """Handles all database operations for the moms table."""

    @staticmethod
    def create_mom(title, date_time, venue, agenda, discussion, decisions,
                   category="", department="", created_by=None):
        """Create a new MoM record."""
        query = """
            INSERT INTO moms (title, date_time, venue, agenda, discussion,
                              decisions, category, department, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, date_time, venue, agenda, discussion,
                      decisions, category, department, created_by, created_at
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (title, date_time, venue, agenda, discussion,
                                    decisions, category, department, created_by))
                return cur.fetchone()
        except Exception as e:
            print(f"Error creating MoM: {e}")
            return None

    @staticmethod
    def get_mom_by_id(mom_id):
        """Fetch a single MoM by ID (not soft-deleted)."""
        query = """
            SELECT m.*, u.username as creator_name
            FROM moms m
            LEFT JOIN users u ON m.created_by = u.id
            WHERE m.id = %s AND m.is_deleted = FALSE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching MoM: {e}")
            return None

    @staticmethod
    def get_all_moms(page=1, per_page=10, sort_by="date_time", sort_order="DESC"):
        """Fetch all MoMs with pagination and sorting."""
        allowed_sort = {"date_time", "title", "created_at", "venue"}
        if sort_by not in allowed_sort:
            sort_by = "date_time"
        sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"

        offset = (page - 1) * per_page
        query = f"""
            SELECT m.*, u.username as creator_name
            FROM moms m
            LEFT JOIN users u ON m.created_by = u.id
            WHERE m.is_deleted = FALSE
            ORDER BY m.{sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (per_page, offset))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching MoMs: {e}")
            return []

    @staticmethod
    def get_total_count():
        """Get total count of non-deleted MoMs."""
        query = "SELECT COUNT(*) as count FROM moms WHERE is_deleted = FALSE"
        try:
            with get_cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result["count"] if result else 0
        except Exception as e:
            print(f"Error counting MoMs: {e}")
            return 0

    @staticmethod
    def update_mom(mom_id, **kwargs):
        """Update MoM fields dynamically."""
        allowed = {"title", "date_time", "venue", "agenda", "discussion",
                    "decisions", "category", "department"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None

        set_clause = ", ".join([f"{k} = %s" for k in fields])
        values = list(fields.values())
        values.append(datetime.now())
        values.append(mom_id)

        query = f"""
            UPDATE moms SET {set_clause}, updated_at = %s
            WHERE id = %s AND is_deleted = FALSE
            RETURNING *
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, values)
                return cur.fetchone()
        except Exception as e:
            print(f"Error updating MoM: {e}")
            return None

    @staticmethod
    def soft_delete(mom_id):
        """Soft-delete a MoM."""
        query = """
            UPDATE moms SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s
            RETURNING id
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (datetime.now(), mom_id))
                return cur.fetchone() is not None
        except Exception as e:
            print(f"Error deleting MoM: {e}")
            return False

    @staticmethod
    def search_moms(title=None, venue=None, date_from=None, date_to=None,
                    assigned_to=None, category=None):
        """Search MoMs with various filters."""
        conditions = ["m.is_deleted = FALSE"]
        params = []

        if title:
            conditions.append("m.title ILIKE %s")
            params.append(f"%{title}%")
        if venue:
            conditions.append("m.venue ILIKE %s")
            params.append(f"%{venue}%")
        if date_from:
            conditions.append("m.date_time >= %s")
            params.append(date_from)
        if date_to:
            conditions.append("m.date_time <= %s")
            params.append(date_to)
        if category:
            conditions.append("m.category = %s")
            params.append(category)
        if assigned_to:
            conditions.append("""
                m.id IN (
                    SELECT mom_id FROM action_items
                    WHERE assigned_to ILIKE %s
                )
            """)
            params.append(f"%{assigned_to}%")

        where = " AND ".join(conditions)
        query = f"""
            SELECT m.*, u.username as creator_name
            FROM moms m
            LEFT JOIN users u ON m.created_by = u.id
            WHERE {where}
            ORDER BY m.date_time DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching MoMs: {e}")
            return []

    @staticmethod
    def get_moms_count_by_month():
        """Get meeting count grouped by month (for charts)."""
        query = """
            SELECT DATE_TRUNC('month', date_time) as month,
                   COUNT(*) as count
            FROM moms WHERE is_deleted = FALSE
            GROUP BY month ORDER BY month
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def get_moms_count_by_category():
        """Get meeting count grouped by category."""
        query = """
            SELECT COALESCE(category, 'Uncategorized') as category,
                   COUNT(*) as count
            FROM moms WHERE is_deleted = FALSE
            GROUP BY category ORDER BY count DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def get_this_month_count():
        """Get count of meetings created this month."""
        query = """
            SELECT COUNT(*) as count FROM moms
            WHERE is_deleted = FALSE
              AND DATE_TRUNC('month', date_time) = DATE_TRUNC('month', CURRENT_DATE)
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result["count"] if result else 0
        except Exception as e:
            print(f"Error: {e}")
            return 0
