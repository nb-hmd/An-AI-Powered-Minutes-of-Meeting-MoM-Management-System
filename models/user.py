"""
User Model - Database operations for users table.
"""

from config.database import get_cursor
from datetime import datetime


class UserModel:
    """Handles all database operations for the users table."""

    @staticmethod
    def create_user(username, email, password_hash, full_name="", role="viewer"):
        """Create a new user in the database."""
        query = """
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, username, email, full_name, role, created_at
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (username, email, password_hash, full_name, role))
                return cur.fetchone()
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_user_by_username(username):
        """Fetch a user by their username."""
        query = """
            SELECT id, username, email, password_hash, full_name, role,
                   profile_picture, is_active, created_at, updated_at
            FROM users
            WHERE username = %s AND is_active = TRUE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (username,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching user by username: {e}")
            return None

    @staticmethod
    def get_user_by_email(email):
        """Fetch a user by their email."""
        query = """
            SELECT id, username, email, password_hash, full_name, role,
                   profile_picture, is_active, created_at, updated_at
            FROM users
            WHERE email = %s AND is_active = TRUE
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (email,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch a user by their ID."""
        query = """
            SELECT id, username, email, full_name, role,
                   profile_picture, is_active, created_at, updated_at
            FROM users
            WHERE id = %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (user_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None

    @staticmethod
    def get_all_users():
        """Fetch all active users."""
        query = """
            SELECT id, username, email, full_name, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user fields dynamically."""
        allowed_fields = {"email", "full_name", "role", "profile_picture", "is_active"}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields:
            return None

        set_clause = ", ".join([f"{k} = %s" for k in fields])
        values = list(fields.values())
        values.append(datetime.now())  # updated_at
        values.append(user_id)

        query = f"""
            UPDATE users
            SET {set_clause}, updated_at = %s
            WHERE id = %s
            RETURNING id, username, email, full_name, role, is_active
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, values)
                return cur.fetchone()
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    @staticmethod
    def update_password(user_id, new_password_hash):
        """Update a user's password."""
        query = """
            UPDATE users
            SET password_hash = %s, updated_at = %s
            WHERE id = %s
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (new_password_hash, datetime.now(), user_id))
                return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    @staticmethod
    def check_username_exists(username):
        """Check if a username already exists."""
        query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (username,))
                result = cur.fetchone()
                return result["count"] > 0
        except Exception as e:
            print(f"Error checking username: {e}")
            return True  # Assume exists on error (safer)

    @staticmethod
    def check_email_exists(email):
        """Check if an email already exists."""
        query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (email,))
                result = cur.fetchone()
                return result["count"] > 0
        except Exception as e:
            print(f"Error checking email: {e}")
            return True  # Assume exists on error (safer)
