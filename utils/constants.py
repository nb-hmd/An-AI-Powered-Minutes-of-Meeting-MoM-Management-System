"""
Constants used throughout the MoM system.
"""

# ============================================
# User Roles
# ============================================
ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"
USER_ROLES = [ROLE_ADMIN, ROLE_VIEWER]

# ============================================
# Action Item Statuses
# ============================================
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_OVERDUE = "overdue"
ACTION_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_OVERDUE]

# ============================================
# Allowed File Types
# ============================================
ALLOWED_FILE_TYPES = ["pdf", "jpg", "jpeg", "png", "docx", "pptx"]
MAX_FILE_SIZE_MB = 10

# ============================================
# Meeting Categories
# ============================================
MEETING_CATEGORIES = [
    "Project Meeting",
    "Client Meeting",
    "Review Meeting",
    "Team Meeting",
    "Board Meeting",
    "General",
    "Other",
]

# ============================================
# Activity Log Actions
# ============================================
ACTION_LOGIN = "Login"
ACTION_LOGOUT = "Logout"
ACTION_REGISTER = "Registration"
ACTION_MOM_CREATED = "MoM Created"
ACTION_MOM_EDITED = "MoM Edited"
ACTION_MOM_DELETED = "MoM Deleted"
ACTION_MOM_EXPORTED_PDF = "MoM Exported (PDF)"
ACTION_MOM_EXPORTED_DOCX = "MoM Exported (DOCX)"
ACTION_FILE_UPLOADED = "File Uploaded"
ACTION_TEMPLATE_USED = "Template Used"
ACTION_STATUS_UPDATED = "Action Item Status Updated"
ACTION_OVERDUE_FLAGGED = "Action Items Flagged Overdue"
ACTION_AUDIO_TRANSCRIBED = "Audio Transcribed"
ACTION_AI_SUMMARY = "AI Summary Generated"
ACTION_AI_GRAMMAR = "AI Grammar Cleanup"
ACTION_AI_FORMAT = "AI Notes Formatted"
ACTION_AI_QUALITY = "AI Quality Check"

# ============================================
# Audio File Types (F15)
# ============================================
AUDIO_FILE_TYPES = ["mp3", "wav", "m4a"]

