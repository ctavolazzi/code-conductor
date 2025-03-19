import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class WorkEffortTemplate:
    """Handles work effort templates."""

    def __init__(self, template_path: Optional[str] = None):
        """Initialize the template.

        Args:
            template_path: Optional path to a template file.
        """
        self.template_path = template_path or self._get_default_template_path()
        self._ensure_template_file()

    def _get_default_template_path(self) -> str:
        """Get the default template path."""
        return os.path.join(os.path.dirname(__file__), "templates", "default.json")

    def _ensure_template_file(self) -> None:
        """Ensure the template file exists."""
        template_dir = os.path.dirname(self.template_path)
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)

        if not os.path.exists(self.template_path):
            default_template = {
                "title": "",
                "description": "",
                "priority": "medium",
                "assignee": "Unassigned",
                "due_date": "",
                "tags": [],
                "status": "active",
                "created_at": "",
                "updated_at": "",
                "completed_at": "",
                "dependencies": [],
                "related_work_efforts": [],
                "notes": []
            }

            with open(self.template_path, "w") as f:
                json.dump(default_template, f, indent=2)

    def load(self) -> Dict[str, Any]:
        """Load the template.

        Returns:
            The template data.
        """
        self._ensure_template_file()

        with open(self.template_path, "r") as f:
            return json.load(f)

    def save(self, data: Dict[str, Any]) -> None:
        """Save the template.

        Args:
            data: The template data to save.
        """
        self._ensure_template_file()

        with open(self.template_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_field_names(self) -> List[str]:
        """Get the field names in the template.

        Returns:
            List of field names.
        """
        template = self.load()
        return list(template.keys())

    def get_field_value(self, field_name: str) -> Any:
        """Get the value of a field.

        Args:
            field_name: The name of the field.

        Returns:
            The value of the field.
        """
        template = self.load()
        return template.get(field_name)

    def set_field_value(self, field_name: str, value: Any) -> None:
        """Set the value of a field.

        Args:
            field_name: The name of the field.
            value: The value to set.
        """
        template = self.load()
        template[field_name] = value
        self.save(template)

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data against the template.

        Args:
            data: The data to validate.

        Returns:
            True if valid, False otherwise.
        """
        template = self.load()
        return all(field in template for field in data.keys())