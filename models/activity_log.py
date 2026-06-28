"""
Activity Log Model - Database operations for activity_logs table.
"""

from config.database import get_cursor


class ActivityLogModel:
    """Handles all database operations for the activity_logs table."""

    @staticmethod
    def log_activity(user_id, username, action, details="", ip_address=""):
        """Log a user activity."""
        query = """
            INSERT INTO activity_logs (user_id, username, action, details, ip_address)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (user_id, username, action, details, ip_address))
                result = cur.fetchone()
                return result["id"] if result else None
        except Exception as e:
            print(f"Error logging activity: {e}")
            return None

    @staticmethod
    def get_recent_logs(limit=50):
        """Get the most recent activity logs."""
        query = """
            SELECT id, user_id, username, action, details, ip_address, timestamp
            FROM activity_logs
            ORDER BY timestamp DESC
            LIMIT %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching activity logs: {e}")
            return []

    @staticmethod
    def get_logs_by_user(user_id, limit=50):
        """Get activity logs for a specific user."""
        query = """
            SELECT id, user_id, username, action, details, ip_address, timestamp
            FROM activity_logs
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (user_id, limit))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching user activity logs: {e}")
            return []
