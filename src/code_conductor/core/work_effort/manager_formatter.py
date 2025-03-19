from typing import Dict, List, Any, Optional
import os
import json
import logging
from datetime import datetime
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.text import Text

class WorkEffortManagerFormatter:
    """Formatter for work effort manager data."""

    def __init__(self, project_dir: str):
        """Initialize the formatter with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.console = Console()

    def format_work_effort(self, work_effort_data: Dict[str, Any]) -> str:
        """Format work effort data into markdown content.

        Args:
            work_effort_data: The work effort data to format.

        Returns:
            The formatted markdown content.
        """
        try:
            # Extract required fields
            metadata = work_effort_data.get("metadata", {})
            if not metadata:
                # If metadata is not present, use the work effort data as metadata
                metadata = work_effort_data

            title = metadata.get("title", "Untitled Work Effort")
            assignee = metadata.get("assignee", "self")
            priority = metadata.get("priority", "medium")
            status = metadata.get("status", "active")
            created_at = metadata.get("created_at", datetime.now().isoformat())
            tags = metadata.get("tags", [])

            # Extract optional fields
            description = metadata.get("description", "")
            due_date = metadata.get("due_date", "")
            updated_at = metadata.get("updated_at", "")

            # Format frontmatter
            frontmatter = [
                "---",
                f"id: {metadata.get('id')}",
                f"title: {title}",
                f"assignee: {assignee}",
                f"priority: {priority}",
                f"status: {status}",
                f"created_at: {created_at}"
            ]

            if due_date:
                frontmatter.append(f"due_date: {due_date}")
            if updated_at:
                frontmatter.append(f"updated_at: {updated_at}")
            if tags:
                frontmatter.append(f"tags: {', '.join(tags)}")

            frontmatter.append("---")

            # Format content sections
            sections = [
                f"# {title}",
                "",
                "## Description",
                description or "No description provided.",
                "",
                "## Tasks",
                "- [ ] Initial task",
                "",
                "## Notes",
                "Add notes here.",
                "",
                "## Dependencies",
                "List dependencies here.",
                "",
                "## Related Work Efforts",
                "List related work efforts here."
            ]

            # Combine all parts
            content = "\n".join(frontmatter + [""] + sections)

            return content

        except Exception as e:
            self.logger.error(f"Error formatting work effort: {str(e)}")
            return ""

    def format_list_output(self, work_efforts: Dict[str, Any], format_type: str = "text") -> str:
        """Format work efforts list for output.

        Args:
            work_efforts: Dictionary of work efforts to format.
            format_type: The output format type ("text" or "markdown").

        Returns:
            The formatted output string.
        """
        try:
            if not work_efforts:
                return "No work efforts found."

            if format_type == "markdown":
                return self._format_list_markdown(work_efforts)
            else:
                return self._format_list_text(work_efforts)

        except Exception as e:
            self.logger.error(f"Error formatting work efforts list: {str(e)}")
            return "Error formatting work efforts list."

    def _format_list_markdown(self, work_efforts: Dict[str, Any]) -> str:
        """Format work efforts list in markdown format.

        Args:
            work_efforts: Dictionary of work efforts to format.

        Returns:
            The formatted markdown string.
        """
        lines = ["# Work Efforts", ""]

        for work_effort_id, data in work_efforts.items():
            title = data.get("title", "Untitled")
            status = data.get("status", "unknown")
            assignee = data.get("assignee", "unassigned")
            priority = data.get("priority", "none")

            lines.extend([
                f"## {title}",
                f"- **ID:** {work_effort_id}",
                f"- **Status:** {status}",
                f"- **Assignee:** {assignee}",
                f"- **Priority:** {priority}",
                ""
            ])

        return "\n".join(lines)

    def _format_list_text(self, work_efforts: Dict[str, Any]) -> str:
        """Format work efforts list in plain text format.

        Args:
            work_efforts: Dictionary of work efforts to format.

        Returns:
            The formatted text string.
        """
        lines = ["Work Efforts:", ""]

        for work_effort_id, data in work_efforts.items():
            title = data.get("title", "Untitled")
            status = data.get("status", "unknown")
            assignee = data.get("assignee", "unassigned")
            priority = data.get("priority", "none")

            lines.extend([
                f"{title}",
                f"  ID: {work_effort_id}",
                f"  Status: {status}",
                f"  Assignee: {assignee}",
                f"  Priority: {priority}",
                ""
            ])

        return "\n".join(lines)

    def format_work_efforts_list(self, work_efforts: List[Dict[str, Any]], format_type: str = 'table') -> str:
        """Format a list of work efforts for display."""
        try:
            if format_type == 'json':
                return json.dumps(work_efforts, indent=2)

            if format_type == 'table':
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Title")
                table.add_column("Status")
                table.add_column("Priority")
                table.add_column("Assignee")
                table.add_column("Due Date")

                for work_effort in work_efforts:
                    metadata = work_effort.get('metadata', {})
                    table.add_row(
                        metadata.get('title', 'Untitled'),
                        metadata.get('status', 'unknown'),
                        metadata.get('priority', 'medium'),
                        metadata.get('assignee', 'unassigned'),
                        metadata.get('due_date', 'not set')
                    )

                return self.console.render_str(table)

            # Default to simple text format
            formatted = ""
            for work_effort in work_efforts:
                formatted += self.format_work_effort(work_effort) + "\n\n"
            return formatted
        except Exception as e:
            self.logger.error(f"Error formatting work efforts list: {e}")
            return "Error formatting work efforts list"

    def format_manager_info(self, manager_info: Dict[str, Any], format_type: str = 'text') -> str:
        """Format manager information for display."""
        try:
            if format_type == 'json':
                return json.dumps(manager_info, indent=2)

            formatted = f"Manager Name: {manager_info.get('name', 'unnamed')}\n"
            formatted += f"Created: {manager_info.get('created_at', 'unknown')}\n"
            formatted += f"Work Efforts Directory: {manager_info.get('work_efforts_dir', 'not set')}\n"
            formatted += f"Templates Directory: {manager_info.get('templates_dir', 'not set')}\n"
            formatted += f"History Directory: {manager_info.get('history_dir', 'not set')}\n"

            return formatted
        except Exception as e:
            self.logger.error(f"Error formatting manager info: {e}")
            return "Error formatting manager info"

    def format_managers_list(self, managers: List[Dict[str, Any]], format_type: str = 'table') -> str:
        """Format a list of managers for display."""
        try:
            if format_type == 'json':
                return json.dumps(managers, indent=2)

            if format_type == 'table':
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Name")
                table.add_column("Created At")
                table.add_column("Work Efforts")
                table.add_column("Default")

                for manager in managers:
                    table.add_row(
                        manager.get('name', 'unnamed'),
                        manager.get('created_at', 'unknown'),
                        str(manager.get('work_effort_count', 0)),
                        '✓' if manager.get('is_default', False) else ''
                    )

                return self.console.render_str(table)

            # Default to simple text format
            formatted = ""
            for manager in managers:
                formatted += self.format_manager_info(manager) + "\n\n"
            return formatted
        except Exception as e:
            self.logger.error(f"Error formatting managers list: {e}")
            return "Error formatting managers list"

    def format_error(self, error_message: str) -> str:
        """Format an error message."""
        return f"❌ {error_message}"

    def format_success(self, success_message: str) -> str:
        """Format a success message."""
        return f"✓ {success_message}"

    def format_warning(self, warning_message: str) -> str:
        """Format a warning message."""
        return f"⚠ {warning_message}"

    def format_info(self, info_message: str) -> str:
        """Format an info message."""
        return f"ℹ {info_message}"