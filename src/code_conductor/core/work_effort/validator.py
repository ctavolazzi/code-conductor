from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

class WorkEffortValidator:
    """Validates work effort data."""

    VALID_PRIORITIES = ["high", "medium", "low"]
    VALID_STATUSES = ["active", "completed", "archived", "paused"]

    @staticmethod
    def validate_title(title: str) -> bool:
        """Validate the title.

        Args:
            title: The title to validate.

        Returns:
            True if valid, False otherwise.
        """
        return bool(title and isinstance(title, str))

    @staticmethod
    def validate_description(description: str) -> bool:
        """Validate the description.

        Args:
            description: The description to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(description, str)

    @staticmethod
    def validate_priority(priority: str) -> bool:
        """Validate the priority.

        Args:
            priority: The priority to validate.

        Returns:
            True if valid, False otherwise.
        """
        return priority.lower() in WorkEffortValidator.VALID_PRIORITIES

    @staticmethod
    def validate_assignee(assignee: str) -> bool:
        """Validate the assignee.

        Args:
            assignee: The assignee to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(assignee, str)

    @staticmethod
    def validate_due_date(due_date: str) -> bool:
        """Validate the due date.

        Args:
            due_date: The due date to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            if not due_date:
                return True
            datetime.strptime(due_date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_tags(tags: List[str]) -> bool:
        """Validate the tags.

        Args:
            tags: The tags to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)

    @staticmethod
    def validate_status(status: str) -> bool:
        """Validate the status.

        Args:
            status: The status to validate.

        Returns:
            True if valid, False otherwise.
        """
        return status.lower() in WorkEffortValidator.VALID_STATUSES

    @staticmethod
    def validate_created_at(created_at: str) -> bool:
        """Validate the created_at timestamp.

        Args:
            created_at: The created_at timestamp to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            if not created_at:
                return True
            datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_updated_at(updated_at: str) -> bool:
        """Validate the updated_at timestamp.

        Args:
            updated_at: The updated_at timestamp to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            if not updated_at:
                return True
            datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_completed_at(completed_at: str) -> bool:
        """Validate the completed_at timestamp.

        Args:
            completed_at: The completed_at timestamp to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            if not completed_at:
                return True
            datetime.strptime(completed_at, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_dependencies(dependencies: List[str]) -> bool:
        """Validate the dependencies.

        Args:
            dependencies: The dependencies to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(dependencies, list) and all(isinstance(dep, str) for dep in dependencies)

    @staticmethod
    def validate_related_work_efforts(related: List[str]) -> bool:
        """Validate the related work efforts.

        Args:
            related: The related work efforts to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(related, list) and all(isinstance(rel, str) for rel in related)

    @staticmethod
    def validate_notes(notes: List[str]) -> bool:
        """Validate the notes.

        Args:
            notes: The notes to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(notes, list) and all(isinstance(note, str) for note in notes)

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> bool:
        """Validate all work effort data.

        Args:
            data: The data to validate.

        Returns:
            True if valid, False otherwise.
        """
        validators = {
            "title": cls.validate_title,
            "description": cls.validate_description,
            "priority": cls.validate_priority,
            "assignee": cls.validate_assignee,
            "due_date": cls.validate_due_date,
            "tags": cls.validate_tags,
            "status": cls.validate_status,
            "created_at": cls.validate_created_at,
            "updated_at": cls.validate_updated_at,
            "completed_at": cls.validate_completed_at,
            "dependencies": cls.validate_dependencies,
            "related_work_efforts": cls.validate_related_work_efforts,
            "notes": cls.validate_notes
        }

        return all(
            field not in data or validators[field](data[field])
            for field in validators
        )

class WorkEffortManagerValidator:
    """Validates work effort data."""

    def __init__(self, project_dir: str = None):
        """Initialize the validator.

        Args:
            project_dir: Optional project directory path.
        """
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)

    def validate_work_effort_data(self, metadata: Dict[str, Any]) -> bool:
        """Validate work effort metadata.

        Args:
            metadata: The metadata to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            # Check required fields
            required_fields = ["id", "title", "assignee", "priority", "status"]
            for field in required_fields:
                if field not in metadata:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate status
            if not self.validate_status(metadata["status"]):
                return False

            # Validate priority
            if not self.validate_priority(metadata["priority"]):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating work effort data: {str(e)}")
            return False

    def validate_status(self, status: str) -> bool:
        """Validate work effort status.

        Args:
            status: The status to validate.

        Returns:
            True if valid, False otherwise.
        """
        valid_statuses = ["active", "completed", "archived", "paused"]
        if status not in valid_statuses:
            self.logger.error(f"Invalid status: {status}. Must be one of {valid_statuses}")
            return False
        return True

    def validate_priority(self, priority: str) -> bool:
        """Validate work effort priority.

        Args:
            priority: The priority to validate.

        Returns:
            True if valid, False otherwise.
        """
        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            self.logger.error(f"Invalid priority: {priority}. Must be one of {valid_priorities}")
            return False
        return True