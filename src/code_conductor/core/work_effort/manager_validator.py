from typing import Dict, Optional, Any
import os
import logging
import re
from datetime import datetime

class WorkEffortManagerValidator:
    """Validator for work effort managers."""

    def __init__(self, project_dir: str):
        """Initialize the validator with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)

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

    def validate_manager_name(self, manager_name: str) -> bool:
        """Validate a manager name."""
        if not manager_name:
            self.logger.error("Manager name cannot be empty")
            return False

        # Check if the name contains only alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', manager_name):
            self.logger.error("Manager name can only contain alphanumeric characters, underscores, and hyphens")
            return False

        return True

    def validate_manager_config(self, config: Dict[str, Any]) -> bool:
        """Validate a manager configuration."""
        required_fields = ['work_efforts_dir', 'templates_dir', 'history_dir']

        # Check for required fields
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field in manager config: {field}")
                return False

            # Check if the directories exist or can be created
            dir_path = os.path.join(self.project_dir, config[field])
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except Exception as e:
                    self.logger.error(f"Failed to create directory {dir_path}: {e}")
                    return False

        return True

    def validate_work_effort_id(self, work_effort_id: str) -> bool:
        """Validate a work effort ID."""
        if not work_effort_id:
            self.logger.error("Work effort ID cannot be empty")
            return False

        # Check if the ID matches the expected format (e.g., YYYYMMDDHHMI_title)
        if not re.match(r'^\d{12}_[a-zA-Z0-9_-]+$', work_effort_id):
            self.logger.error("Invalid work effort ID format")
            return False

        return True

    def validate_work_effort_data(self, data: Dict[str, Any]) -> bool:
        """Validate work effort data."""
        required_fields = ['title', 'status', 'created_at']

        # Check for required fields
        for field in required_fields:
            if field not in data:
                self.logger.error(f"Missing required field in work effort data: {field}")
                return False

        # Validate title
        if not data['title'] or not isinstance(data['title'], str):
            self.logger.error("Invalid work effort title")
            return False

        # Validate status
        valid_statuses = ['active', 'completed', 'archived', 'paused']
        if data['status'] not in valid_statuses:
            self.logger.error(f"Invalid work effort status. Must be one of: {', '.join(valid_statuses)}")
            return False

        # Validate created_at timestamp
        try:
            datetime.fromisoformat(data['created_at'])
        except (ValueError, TypeError):
            self.logger.error("Invalid created_at timestamp")
            return False

        return True

    def validate_file_path(self, file_path: str) -> bool:
        """Validate a file path."""
        if not file_path:
            self.logger.error("File path cannot be empty")
            return False

        # Check if the path is within the project directory
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(os.path.abspath(self.project_dir)):
            self.logger.error("File path must be within the project directory")
            return False

        # Check if the directory exists or can be created
        dir_path = os.path.dirname(abs_path)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as e:
                self.logger.error(f"Failed to create directory {dir_path}: {e}")
                return False

        return True

    def validate_dependencies(self, dependencies: list[str]) -> bool:
        """Validate work effort dependencies."""
        if not isinstance(dependencies, list):
            self.logger.error("Dependencies must be a list")
            return False

        for dep in dependencies:
            if not self.validate_work_effort_id(dep):
                self.logger.error(f"Invalid dependency ID: {dep}")
                return False

        return True