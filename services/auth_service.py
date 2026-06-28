"""
Authentication Service - Handles user authentication, registration, and session management.
"""

import bcrypt
import streamlit as st
from datetime import datetime
from models.user import UserModel
from models.activity_log import ActivityLogModel


class AuthService:
    """Authentication and session management service."""

    # ========================================
    # Password Hashing
    # ========================================
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception:
            return False

    # ========================================
    # Authentication
    # ========================================
    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        Authenticate a user.
        Returns dict with 'success', 'message', and 'user' keys.
        """
        if not username or not password:
            return {"success": False, "message": "Username and password are required.", "user": None}

        user = UserModel.get_user_by_username(username)
        if not user:
            return {"success": False, "message": "Invalid username or password.", "user": None}

        if not user.get("is_active", True):
            return {"success": False, "message": "Your account has been deactivated.", "user": None}

        if not AuthService.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid username or password.", "user": None}

        # Successful login — set session state
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]
        st.session_state["user_role"] = user["role"]
        st.session_state["full_name"] = user.get("full_name", user["username"])
        st.session_state["login_time"] = datetime.now().isoformat()

        # Log the login activity
        ActivityLogModel.log_activity(
            user_id=user["id"],
            username=user["username"],
            action="Login",
            details="User logged in successfully.",
        )

        return {"success": True, "message": "Login successful!", "user": user}

    @staticmethod
    def register(username: str, email: str, password: str, confirm_password: str, full_name: str = "") -> dict:
        """
        Register a new user.
        Returns dict with 'success' and 'message' keys.
        """
        # Validate inputs
        if not username or not email or not password:
            return {"success": False, "message": "All fields are required."}

        if len(username) < 3:
            return {"success": False, "message": "Username must be at least 3 characters."}

        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters."}

        if password != confirm_password:
            return {"success": False, "message": "Passwords do not match."}

        if "@" not in email or "." not in email:
            return {"success": False, "message": "Please enter a valid email address."}

        # Check if username or email already exists
        if UserModel.check_username_exists(username):
            return {"success": False, "message": "Username already exists."}

        if UserModel.check_email_exists(email):
            return {"success": False, "message": "Email already registered."}

        # Hash password and create user
        password_hash = AuthService.hash_password(password)
        user = UserModel.create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role="viewer",  # New users start as viewers
        )

        if user:
            # Log the registration activity
            ActivityLogModel.log_activity(
                user_id=user["id"],
                username=user["username"],
                action="Registration",
                details="New user registered.",
            )
            return {"success": True, "message": "Registration successful! Please log in."}
        else:
            return {"success": False, "message": "Registration failed. Please try again."}

    @staticmethod
    def logout():
        """Log out the current user and clear session state."""
        user_id = st.session_state.get("user_id")
        username = st.session_state.get("username", "Unknown")

        # Log the logout activity
        if user_id:
            ActivityLogModel.log_activity(
                user_id=user_id,
                username=username,
                action="Logout",
                details="User logged out.",
            )

        # Clear session
        keys_to_clear = [
            "authenticated", "user_id", "username",
            "user_role", "full_name", "login_time",
        ]
        for key in keys_to_clear:
            st.session_state.pop(key, None)

    # ========================================
    # Session Management
    # ========================================
    @staticmethod
    def is_authenticated() -> bool:
        """Check if the current user is authenticated."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_current_user_id() -> int:
        """Get the current logged-in user's ID."""
        return st.session_state.get("user_id")

    @staticmethod
    def get_current_username() -> str:
        """Get the current logged-in user's username."""
        return st.session_state.get("username", "")

    @staticmethod
    def get_current_user_role() -> str:
        """Get the current logged-in user's role."""
        return st.session_state.get("user_role", "viewer")

    @staticmethod
    def is_admin() -> bool:
        """Check if the current user is an admin."""
        return st.session_state.get("user_role") == "admin"

    @staticmethod
    def require_auth():
        """
        Authentication decorator for pages.
        Call at the top of a page to require login.
        Returns True if authenticated, False otherwise.
        """
        if not AuthService.is_authenticated():
            st.warning("⚠️ Please log in to access this page.")
            st.stop()
            return False
        return True

    @staticmethod
    def require_admin():
        """
        Admin decorator for pages.
        Call at the top of a page to require admin role.
        """
        AuthService.require_auth()
        if not AuthService.is_admin():
            st.error("🚫 You don't have permission to access this page.")
            st.stop()
            return False
        return True
