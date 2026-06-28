"""
Attendee Model - Database operations for the attendees table.
"""

from config.database import get_cursor


class AttendeeModel:
    """Handles all database operations for the attendees table."""

    @staticmethod
    def add_attendee(mom_id, name, role="", email="", department=""):
        """Add an attendee to a MoM."""
        query = """
            INSERT INTO attendees (mom_id, name, role, email, department)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, mom_id, name, role, email, department
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id, name, role, email, department))
                return cur.fetchone()
        except Exception as e:
            print(f"Error adding attendee: {e}")
            return None

    @staticmethod
    def add_multiple_attendees(mom_id, attendees_list):
        """Add multiple attendees at once. attendees_list = list of dicts."""
        results = []
        for att in attendees_list:
            result = AttendeeModel.add_attendee(
                mom_id=mom_id,
                name=att.get("name", ""),
                role=att.get("role", ""),
                email=att.get("email", ""),
                department=att.get("department", ""),
            )
            if result:
                results.append(result)
        return results

    @staticmethod
    def get_attendees_by_mom(mom_id):
        """Fetch all attendees for a specific MoM."""
        query = """
            SELECT id, mom_id, name, role, email, department
            FROM attendees WHERE mom_id = %s ORDER BY id
        """
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching attendees: {e}")
            return []

    @staticmethod
    def delete_attendees_by_mom(mom_id):
        """Delete all attendees for a MoM (used before re-adding on edit)."""
        query = "DELETE FROM attendees WHERE mom_id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (mom_id,))
                return True
        except Exception as e:
            print(f"Error deleting attendees: {e}")
            return False

    @staticmethod
    def delete_attendee(attendee_id):
        """Delete a single attendee."""
        query = "DELETE FROM attendees WHERE id = %s"
        try:
            with get_cursor() as cur:
                cur.execute(query, (attendee_id,))
                return True
        except Exception as e:
            print(f"Error deleting attendee: {e}")
            return False
