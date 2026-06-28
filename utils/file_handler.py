"""
File handler utility for managing file uploads and downloads.
"""

import os
from pathlib import Path
from config.settings import UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_FILE_TYPES


def ensure_upload_dir():
    """Create upload directory if it doesn't exist."""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def validate_file(uploaded_file) -> tuple:
    """
    Validate an uploaded file.
    Returns (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, "No file provided."

    # Check file extension
    filename = uploaded_file.name
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_FILE_TYPES:
        return False, f"File type '.{extension}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"

    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds the limit of {MAX_FILE_SIZE_MB} MB."

    return True, ""


def save_file(uploaded_file, subfolder="") -> dict:
    """
    Save an uploaded file to disk.
    Returns dict with file metadata.
    """
    ensure_upload_dir()

    save_dir = Path(UPLOAD_DIR) / subfolder if subfolder else Path(UPLOAD_DIR)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid collisions
    import time
    timestamp = int(time.time())
    original_name = uploaded_file.name
    safe_name = f"{timestamp}_{original_name}"
    file_path = save_dir / safe_name

    # Write file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""

    return {
        "filename": original_name,
        "file_path": str(file_path),
        "file_type": extension,
        "file_size": uploaded_file.size,
    }


def delete_file(file_path: str) -> bool:
    """Delete a file from disk."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False


def get_file_icon(file_type: str) -> str:
    """Get an emoji icon for a file type."""
    icons = {
        "pdf": "📄",
        "jpg": "🖼️",
        "jpeg": "🖼️",
        "png": "🖼️",
        "docx": "📝",
        "pptx": "📊",
    }
    return icons.get(file_type, "📎")
