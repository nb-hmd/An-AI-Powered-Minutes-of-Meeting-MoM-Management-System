"""
Analytics Service - Dashboard metrics and chart data.
"""

from models.mom import MoMModel
from models.action_item import ActionItemModel
from models.activity_log import ActivityLogModel
from config.database import get_cursor


class AnalyticsService:
    """Service for computing dashboard analytics."""

    @staticmethod
    def get_dashboard_stats():
        """Get key stats for the dashboard KPI cards."""
        return {
            "total_meetings": MoMModel.get_total_count(),
            "this_month": MoMModel.get_this_month_count(),
            "pending_actions": ActionItemModel.get_pending_count(),
            "completed_actions": ActionItemModel.get_completed_count(),
            "overdue_actions": ActionItemModel.get_overdue_count(),
        }

    @staticmethod
    def get_meetings_per_month():
        """Get meetings count per month for bar/line chart."""
        return MoMModel.get_moms_count_by_month()

    @staticmethod
    def get_meetings_by_category():
        """Get meetings count by category for pie chart."""
        return MoMModel.get_moms_count_by_category()

    @staticmethod
    def get_upcoming_deadlines(limit=10):
        """Get upcoming action item deadlines."""
        return ActionItemModel.get_upcoming_deadlines(limit)

    @staticmethod
    def get_meetings_by_department():
        """Get meetings count by department."""
        query = """
            SELECT COALESCE(department, 'Unassigned') as department,
                   COUNT(*) as count
            FROM moms WHERE is_deleted = FALSE
            GROUP BY department ORDER BY count DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception:
            return []

    @staticmethod
    def get_action_items_by_status():
        """Get action items count grouped by status (for donut chart)."""
        query = """
            SELECT status, COUNT(*) as count
            FROM action_items
            GROUP BY status ORDER BY count DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception:
            return []

    @staticmethod
    def get_top_assignees(limit=8):
        """Get top assignees by number of action items assigned (horizontal bar)."""
        query = """
            SELECT assigned_to,
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM action_items
            WHERE assigned_to IS NOT NULL AND assigned_to != ''
            GROUP BY assigned_to
            ORDER BY total DESC
            LIMIT %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
        except Exception:
            return []

    @staticmethod
    def get_recent_activity(limit=20):
        """Get recent activity logs."""
        return ActivityLogModel.get_recent_logs(limit)
