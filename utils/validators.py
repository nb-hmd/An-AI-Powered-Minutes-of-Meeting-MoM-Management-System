"""
Input validators for the MoM system.
"""

import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> tuple:
    """
    Validate username.
    Returns (is_valid, error_message).
    """
    if not username:
        return False, "Username is required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 50:
        return False, "Username must be at most 50 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""


def validate_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if len(password) > 128:
        return False, "Password must be at most 128 characters."
    return True, ""


def validate_required_field(value: str, field_name: str) -> tuple:
    """
    Validate that a required field is not empty.
    Returns (is_valid, error_message).
    """
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, ""


# ============================================
# MoM Form Validation
# ============================================

def validate_mom_form(title, meeting_date, agenda, action_items,
                      uploaded_files=None, is_new=True):
    """
    Validate the Create/Edit MoM form fields.
    Returns a list of error dicts: [{'field': str, 'message': str}]
    An empty list means no errors.

    Args:
        title: Meeting title string
        meeting_date: date object for the meeting
        agenda: Agenda text
        action_items: List of action item dicts with 'description', 'assigned_to', 'deadline'
        uploaded_files: List of uploaded file objects (optional)
        is_new: True for Create, False for Edit (disables past-date check)
    """
    from datetime import date as date_type
    errors = []

    # 1. Required field: Title
    if not title or not title.strip():
        errors.append({
            "field": "Meeting Title",
            "message": "Meeting title is required."
        })

    # 2. Required field: Date + past-date check (only for new MoMs)
    if not meeting_date:
        errors.append({
            "field": "Meeting Date",
            "message": "Meeting date is required."
        })
    elif is_new and isinstance(meeting_date, date_type) and meeting_date < date_type.today():
        errors.append({
            "field": "Meeting Date",
            "message": "Meeting date cannot be set to a past date when creating a new MoM."
        })

    # 3. Required field: Agenda (at least one item)
    if not agenda or not agenda.strip():
        errors.append({
            "field": "Agenda",
            "message": "At least one agenda item is required before saving."
        })

    # 4. Action item validation
    action_errors = validate_action_items(action_items)
    errors.extend(action_errors)

    # 5. File validation (server-side)
    if uploaded_files:
        file_errors = validate_uploaded_files(uploaded_files)
        errors.extend(file_errors)

    return errors


def validate_action_items(action_items):
    """
    Validate action items: every item with a description must have
    an assigned person and a deadline.
    Returns list of error dicts.
    """
    errors = []
    if not action_items:
        return errors

    for i, item in enumerate(action_items):
        desc = item.get("description", "").strip()
        if not desc:
            continue  # Skip empty rows (user didn't fill anything)

        assigned = item.get("assigned_to", "").strip()
        deadline = item.get("deadline")
        item_num = i + 1

        if not assigned:
            errors.append({
                "field": f"Action Item {item_num}",
                "message": f'"{desc[:60]}" — an assigned person is required for every action item.'
            })

        if not deadline:
            errors.append({
                "field": f"Action Item {item_num}",
                "message": f'"{desc[:60]}" — a deadline is required for every action item.'
            })

    return errors


def validate_uploaded_files(uploaded_files):
    """
    Server-side validation of uploaded files for type and size.
    Returns list of error dicts.
    """
    ALLOWED_TYPES = {"pdf", "jpg", "jpeg", "png", "docx", "pptx"}
    MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    errors = []
    if not uploaded_files:
        return errors

    for f in uploaded_files:
        filename = getattr(f, "name", "unknown")

        # Type check
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_TYPES:
            errors.append({
                "field": "Attachments",
                "message": f'"{filename}" — file type .{ext} is not allowed. '
                           f'Allowed: {", ".join(sorted(ALLOWED_TYPES))}.'
            })

        # Size check
        file_size = getattr(f, "size", 0)
        if file_size > MAX_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            errors.append({
                "field": "Attachments",
                "message": f'"{filename}" — file size ({size_mb:.1f} MB) exceeds '
                           f'the maximum allowed size of 10 MB.'
            })

    return errors

