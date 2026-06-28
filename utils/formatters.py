"""
Data formatting utilities for the MoM system.
"""

from datetime import datetime, date


def format_datetime(dt) -> str:
    """Format a datetime object for display."""
    if isinstance(dt, datetime):
        return dt.strftime("%B %d, %Y at %I:%M %p")
    elif isinstance(dt, date):
        return dt.strftime("%B %d, %Y")
    elif isinstance(dt, str):
        try:
            dt_obj = datetime.fromisoformat(dt)
            return dt_obj.strftime("%B %d, %Y at %I:%M %p")
        except ValueError:
            return dt
    return str(dt)


def format_date(dt) -> str:
    """Format a date object for display."""
    if isinstance(dt, (datetime, date)):
        return dt.strftime("%B %d, %Y")
    return str(dt)


def format_status(status: str) -> str:
    """Format a status string with emoji."""
    status_map = {
        "pending": "⏳ Pending",
        "in_progress": "🔄 In Progress",
        "completed": "✅ Completed",
        "overdue": "🔴 Overdue",
    }
    return status_map.get(status, status)


def format_role(role: str) -> str:
    """Format a user role string with emoji."""
    role_map = {
        "admin": "👑 Admin",
        "viewer": "👁️ Viewer",
    }
    return role_map.get(role, role)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
