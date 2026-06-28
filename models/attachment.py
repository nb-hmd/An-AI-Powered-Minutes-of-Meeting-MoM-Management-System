"""
Attachment Model - Database operations for the attachments table.
"""

from config.database import get_cursor


class AttachmentModel:
    """Handles all database operations for the attachments table."""

    @staticmethod
    def add_attachment(mom_id, filename, file_path, file_type="", file_size=0):
        """Add an attachment record to the database."""
        query = """
            INSERT INTO attachments (mom_id, filename, file_path, file_type, file_size)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, mom_id, filename, file_path, file_type, file_size, uploaded_at
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id, filename, file_path, file_type, file_size))
                return cur.fetchone()
        except Exception as e:
            print(f"Error adding attachment: {e}")
            return None

    @staticmethod
    def get_attachments_by_mom(mom_id):
        """Fetch all attachments for a specific MoM."""
        query = """
            SELECT id, mom_id, filename, file_path, file_type, file_size, uploaded_at
            FROM attachments WHERE mom_id = %s ORDER BY uploaded_at DESC
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching attachments: {e}")
            return []

    @staticmethod
    def get_attachment_by_id(attachment_id):
        """Fetch a single attachment by ID."""
        query = "SELECT * FROM attachments WHERE id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (attachment_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching attachment: {e}")
            return None

    @staticmethod
    def delete_attachment(attachment_id):
        """Delete an attachment record from the database."""
        query = "DELETE FROM attachments WHERE id = %s RETURNING file_path"
        try:
            with get_cursor() as cur:
                cur.execute(query, (attachment_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error deleting attachment: {e}")
            return None

    @staticmethod
    def delete_attachments_by_mom(mom_id):
        """Delete all attachment records for a MoM."""
        query = "DELETE FROM attachments WHERE mom_id = %s RETURNING file_path"
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error deleting attachments: {e}")
            return []
