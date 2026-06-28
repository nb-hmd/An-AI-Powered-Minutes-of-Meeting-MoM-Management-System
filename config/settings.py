"""
Application configuration settings.
Loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ============================================
# Database Configuration
# ============================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "mom_system"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# SQLAlchemy connection string
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)


# ============================================
# Application Settings
# ============================================
APP_NAME = os.getenv("APP_NAME", "Minutes of Meeting System")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")


# ============================================
# File Upload Settings
# ============================================
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads/attachments")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
ALLOWED_FILE_TYPES = ["pdf", "jpg", "jpeg", "png", "docx", "pptx"]


# ============================================
# Export Settings
# ============================================
EXPORT_DIR_PDF = BASE_DIR / "exports" / "pdf"
EXPORT_DIR_DOCX = BASE_DIR / "exports" / "docx"


# ============================================
# Session Settings
# ============================================
SESSION_TIMEOUT_MINUTES = 60


# ============================================
# Pagination
# ============================================
DEFAULT_PAGE_SIZE = 10
