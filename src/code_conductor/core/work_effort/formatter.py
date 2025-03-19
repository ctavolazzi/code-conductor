from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.text import Text

class WorkEffortFormatter:
    """Formatter for work effort data for display."""

    def __init__(self):
        self.console = Console()

    @staticmethod
    def format_date(date_str: Optional[str]) -> str:
        """Format a date string for display."""
        if not date_str:
            return "Not set"
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return date_str

    def format_table(self, work_efforts: List[Dict[str, Any]], format_type: str = "simple") -> str:
        """Format work efforts as a table."""
        if not work_efforts:
            return "No work efforts found."

        headers = ["Title", "Status", "Priority", "Assignee", "Due Date"]
        rows = []

        for we in work_efforts:
            rows.append([
                we.get("title", "Untitled"),
                we.get("status", "Not started"),
                we.get("priority", "Medium"),
                we.get("assignee", "Unassigned"),
                self.format_date(we.get("due_date"))
            ])

        return tabulate(rows, headers=headers, tablefmt=format_type)

    def format_rich_table(self, work_efforts: List[Dict[str, Any]]) -> None:
        """Format work efforts as a rich table with colors."""
        if not work_efforts:
            self.console.print("No work efforts found.")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("Priority")
        table.add_column("Assignee")
        table.add_column("Due Date")

        status_colors = {
            "not_started": "red",
            "in_progress": "yellow",
            "completed": "green",
            "blocked": "red"
        }

        priority_colors = {
            "high": "red",
            "medium": "yellow",
            "low": "green"
        }

        for we in work_efforts:
            status = we.get("status", "not_started").lower()
            priority = we.get("priority", "medium").lower()

            table.add_row(
                we.get("title", "Untitled"),
                Text(status, style=status_colors.get(status, "white")),
                Text(priority, style=priority_colors.get(priority, "white")),
                we.get("assignee", "Unassigned"),
                self.format_date(we.get("due_date"))
            )

        self.console.print(table)

    def format_json(self, work_efforts: List[Dict[str, Any]], indent: int = 2) -> str:
        """Format work efforts as JSON."""
        return json.dumps(work_efforts, indent=indent)

    def format_summary(self, work_effort: Dict[str, Any]) -> str:
        """Format a single work effort as a summary."""
        summary = [
            f"Title: {work_effort.get('title', 'Untitled')}",
            f"Status: {work_effort.get('status', 'Not started')}",
            f"Priority: {work_effort.get('priority', 'Medium')}",
            f"Assignee: {work_effort.get('assignee', 'Unassigned')}",
            f"Due Date: {self.format_date(work_effort.get('due_date'))}",
            f"Description: {work_effort.get('description', 'No description')}"
        ]

        if work_effort.get("tags"):
            summary.append(f"Tags: {', '.join(work_effort['tags'])}")

        if work_effort.get("dependencies"):
            summary.append(f"Dependencies: {', '.join(work_effort['dependencies'])}")

        if work_effort.get("related_work_efforts"):
            summary.append(f"Related: {', '.join(work_effort['related_work_efforts'])}")

        return "\n".join(summary)

    def format_list(self, work_efforts: List[Dict[str, Any]]) -> str:
        """Format work efforts as a simple list."""
        if not work_efforts:
            return "No work efforts found."

        formatted = []
        for we in work_efforts:
            formatted.append(
                f"- {we.get('title', 'Untitled')} "
                f"({we.get('status', 'Not started')}, "
                f"{we.get('priority', 'Medium')} priority, "
                f"assigned to {we.get('assignee', 'Unassigned')})"
            )

        return "\n".join(formatted)