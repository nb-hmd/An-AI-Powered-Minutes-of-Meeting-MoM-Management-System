"""
MoM Service - Business logic for Minutes of Meeting operations.
Orchestrates model calls for creating, updating, and deleting MoMs
along with their attendees, action items, and attachments.
"""

from models.mom import MoMModel
from models.attendee import AttendeeModel
from models.action_item import ActionItemModel
from models.attachment import AttachmentModel
from models.activity_log import ActivityLogModel
from utils.file_handler import save_file, delete_file


class MoMService:
    """Business logic layer for MoM operations."""

    @staticmethod
    def create_mom(title, date_time, venue, agenda, discussion, decisions,
                   category, department, created_by, attendees=None,
                   action_items=None, uploaded_files=None):
        """
        Create a complete MoM with attendees, action items, and attachments.
        Returns dict with 'success', 'message', and 'mom_id'.
        """
        # Create the MoM record
        mom = MoMModel.create_mom(
            title=title, date_time=date_time, venue=venue,
            agenda=agenda, discussion=discussion, decisions=decisions,
            category=category, department=department, created_by=created_by,
        )
        if not mom:
            return {"success": False, "message": "Failed to create MoM.", "mom_id": None}

        mom_id = mom["id"]

        # Add attendees
        if attendees:
            AttendeeModel.add_multiple_attendees(mom_id, attendees)

        # Add action items
        if action_items:
            ActionItemModel.add_multiple_action_items(mom_id, action_items)

        # Handle file uploads
        if uploaded_files:
            for f in uploaded_files:
                file_info = save_file(f, subfolder=str(mom_id))
                AttachmentModel.add_attachment(
                    mom_id=mom_id,
                    filename=file_info["filename"],
                    file_path=file_info["file_path"],
                    file_type=file_info["file_type"],
                    file_size=file_info["file_size"],
                )

        # Log activity
        ActivityLogModel.log_activity(
            user_id=created_by, username="",
            action="MoM Created",
            details=f"Created MoM: {title}",
        )

        return {"success": True, "message": "MoM created successfully!", "mom_id": mom_id}

    @staticmethod
    def get_mom_detail(mom_id):
        """Get a MoM with all its related data."""
        mom = MoMModel.get_mom_by_id(mom_id)
        if not mom:
            return None

        mom_dict = dict(mom)
        mom_dict["attendees"] = AttendeeModel.get_attendees_by_mom(mom_id)
        mom_dict["action_items"] = ActionItemModel.get_action_items_by_mom(mom_id)
        mom_dict["attachments"] = AttachmentModel.get_attachments_by_mom(mom_id)
        return mom_dict

    @staticmethod
    def update_mom(mom_id, user_id, title=None, date_time=None, venue=None,
                   agenda=None, discussion=None, decisions=None,
                   category=None, department=None,
                   attendees=None, action_items=None, uploaded_files=None):
        """Update a MoM and its related data."""
        # Update MoM fields
        update_fields = {}
        if title is not None: update_fields["title"] = title
        if date_time is not None: update_fields["date_time"] = date_time
        if venue is not None: update_fields["venue"] = venue
        if agenda is not None: update_fields["agenda"] = agenda
        if discussion is not None: update_fields["discussion"] = discussion
        if decisions is not None: update_fields["decisions"] = decisions
        if category is not None: update_fields["category"] = category
        if department is not None: update_fields["department"] = department

        if update_fields:
            result = MoMModel.update_mom(mom_id, **update_fields)
            if not result:
                return {"success": False, "message": "Failed to update MoM."}

        # Replace attendees (delete old, add new)
        if attendees is not None:
            AttendeeModel.delete_attendees_by_mom(mom_id)
            AttendeeModel.add_multiple_attendees(mom_id, attendees)

        # Replace action items (delete old, add new)
        if action_items is not None:
            ActionItemModel.delete_action_items_by_mom(mom_id)
            ActionItemModel.add_multiple_action_items(mom_id, action_items)

        # Handle new file uploads
        if uploaded_files:
            for f in uploaded_files:
                file_info = save_file(f, subfolder=str(mom_id))
                AttachmentModel.add_attachment(
                    mom_id=mom_id,
                    filename=file_info["filename"],
                    file_path=file_info["file_path"],
                    file_type=file_info["file_type"],
                    file_size=file_info["file_size"],
                )

        ActivityLogModel.log_activity(
            user_id=user_id, username="",
            action="MoM Edited",
            details=f"Updated MoM ID: {mom_id}",
        )
        return {"success": True, "message": "MoM updated successfully!"}

    @staticmethod
    def delete_mom(mom_id, user_id):
        """Soft-delete a MoM."""
        success = MoMModel.soft_delete(mom_id)
        if success:
            ActivityLogModel.log_activity(
                user_id=user_id, username="",
                action="MoM Deleted",
                details=f"Deleted MoM ID: {mom_id}",
            )
            return {"success": True, "message": "MoM deleted successfully."}
        return {"success": False, "message": "Failed to delete MoM."}

    @staticmethod
    def delete_attachment(attachment_id, user_id):
        """Delete a single attachment (file + DB record)."""
        att = AttachmentModel.delete_attachment(attachment_id)
        if att:
            delete_file(att["file_path"])
            ActivityLogModel.log_activity(
                user_id=user_id, username="",
                action="File Deleted",
                details=f"Deleted attachment ID: {attachment_id}",
            )
            return True
        return False
