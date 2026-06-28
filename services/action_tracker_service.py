"""
Action Tracker Service - Business logic for the Action Item Tracker
and Action Item Status Update features.
"""

from datetime import datetime, date, timedelta
from models.action_item import ActionItemModel
from models.activity_log import ActivityLogModel


class ActionTrackerService:
    """Service for Action Item Tracker and Status Update features."""

    @staticmethod
    def get_tracker_stats():
        """Get KPI stats for the action tracker page."""
        return {
            "total": ActionItemModel.get_total_action_items_count(),
            "pending": ActionItemModel.get_pending_count(),
            "in_progress": ActionItemModel.get_in_progress_count(),
            "completed": ActionItemModel.get_completed_count(),
            "overdue": ActionItemModel.get_overdue_count(),
        }

    @staticmethod
    def get_filtered_items(status_filter=None, assigned_filter=None,
                           deadline_filter=None, sort_by="deadline",
                           sort_order="ASC"):
        """
        Get action items with filters applied.
        deadline_filter: 'all', 'overdue', 'this_week', 'this_month'
        """
        deadline_start = None
        deadline_end = None
        today = date.today()

        if deadline_filter == "overdue":
            deadline_end = today - timedelta(days=1)
        elif deadline_filter == "this_week":
            # Start of week (Monday) to end of week (Sunday)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            deadline_start = start_of_week
            deadline_end = end_of_week
        elif deadline_filter == "this_month":
            deadline_start = today.replace(day=1)
            # Last day of current month
            if today.month == 12:
                deadline_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                deadline_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        items = ActionItemModel.get_all_action_items(
            status_filter=status_filter,
            assigned_filter=assigned_filter,
            deadline_start=deadline_start,
            deadline_end=deadline_end,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return items

    @staticmethod
    def get_my_items(full_name):
        """Get action items assigned to the current user."""
        if not full_name:
            return []
        return ActionItemModel.get_action_items_by_person(full_name)

    @staticmethod
    def update_item_status(item_id, new_status, comment="",
                           user_full_name="", user_id=None, is_admin=False):
        """
        Update an action item's status with validation.
        Only the assignee or admin can update.
        Returns dict with success/message.
        """
        # Get the item to validate ownership
        item = ActionItemModel.get_action_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Action item not found."}

        # Check permission: assignee or admin
        assigned_to = (item.get("assigned_to") or "").strip().lower()
        user_name = (user_full_name or "").strip().lower()

        if not is_admin and assigned_to != user_name:
            return {
                "success": False,
                "message": "You can only update tasks assigned to you."
            }

        # Validate status
        valid_statuses = ["pending", "in_progress", "completed"]
        if new_status not in valid_statuses:
            return {"success": False, "message": f"Invalid status: {new_status}"}

        # Perform the update
        result = ActionItemModel.update_action_item_with_comment(
            item_id=item_id,
            new_status=new_status,
            comment=comment,
            changed_by=user_full_name,
        )

        if result:
            # Log to activity log
            ActivityLogModel.log_activity(
                user_id=user_id,
                username=user_full_name,
                action="Action Item Status Updated",
                details=f"Item #{item_id}: {item.get('description', '')[:80]} → {new_status}"
                        + (f" | Comment: {comment[:100]}" if comment else ""),
            )
            return {"success": True, "message": "Status updated successfully!"}

        return {"success": False, "message": "Failed to update status."}

    @staticmethod
    def auto_flag_overdue():
        """Auto-detect and flag overdue items."""
        flagged_ids = ActionItemModel.mark_overdue_items()
        if flagged_ids:
            ActivityLogModel.log_activity(
                user_id=None,
                username="System",
                action="Action Items Flagged Overdue",
                details=f"Flagged {len(flagged_ids)} overdue item(s): IDs {flagged_ids}",
            )
        return flagged_ids

    @staticmethod
    def get_filter_options():
        """Get available filter options for the tracker UI."""
        persons = ActionItemModel.get_distinct_assigned_persons()
        return {
            "persons": persons,
            "deadline_options": [
                ("All Deadlines", "all"),
                ("Overdue", "overdue"),
                ("Due This Week", "this_week"),
                ("Due This Month", "this_month"),
            ],
        }

    @staticmethod
    def get_item_history(item_id):
        """Get the status change history for an action item."""
        return ActionItemModel.get_status_history(item_id)
