#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort data model.

This module provides data structures for representing work efforts
and functions for converting between different representations.
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

class WorkEffortStatus(Enum):
    """Enumeration of possible work effort statuses."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    PAUSED = "paused"

    @classmethod
    def from_string(cls, status_str: str) -> 'WorkEffortStatus':
        """Convert a string to a WorkEffortStatus."""
        for status in cls:
            if status.value == status_str.lower():
                return status
        return cls.ACTIVE  # Default to active if not found

class WorkEffortPriority(Enum):
    """Enumeration of possible work effort priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def from_string(cls, priority_str: str) -> 'WorkEffortPriority':
        """Convert a string to a WorkEffortPriority."""
        for priority in cls:
            if priority.value == priority_str.lower():
                return priority
        return cls.MEDIUM  # Default to medium if not found

class WorkEffort:
    """
    Representation of a work effort.

    A work effort is a task or project tracked with metadata like title,
    assignee, priority, etc. and content sections like objectives, tasks, etc.
    """

    def __init__(
        self,
        title: str,
        assignee: str,
        priority: Union[str, WorkEffortPriority],
        due_date: str,
        status: Union[str, WorkEffortStatus] = WorkEffortStatus.ACTIVE,
        created: Optional[str] = None,
        last_updated: Optional[str] = None,
        tags: Optional[List[str]] = None,
        content: Optional[Dict[str, str]] = None,
        path: Optional[str] = None,
        filename: Optional[str] = None,
        last_modified: Optional[float] = None
    ):
        """
        Initialize a WorkEffort.

        Args:
            title: Title of the work effort
            assignee: Person assigned to the work
            priority: Priority level (low, medium, high, critical)
            due_date: Due date in YYYY-MM-DD format
            status: Status of the work effort (active, completed, archived, paused)
            created: Creation timestamp (YYYY-MM-DD HH:MM)
            last_updated: Last update timestamp (YYYY-MM-DD HH:MM)
            tags: List of tags
            content: Dictionary of content sections
            path: Path to the file on disk
            filename: Name of the file
            last_modified: Last modified timestamp
        """
        # Basic information
        self.title = title
        self.assignee = assignee

        # Handle status as string or enum
        if isinstance(status, str):
            self.status = WorkEffortStatus.from_string(status)
        else:
            self.status = status

        # Handle priority as string or enum
        if isinstance(priority, str):
            self.priority = WorkEffortPriority.from_string(priority)
        else:
            self.priority = priority

        # Timestamps
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.created = created or now
        self.last_updated = last_updated or now
        self.due_date = due_date

        # Optional metadata
        self.tags = tags or []
        self.content = content or {}

        # File information
        self.path = path
        self.filename = filename
        self.last_modified = last_modified

    @classmethod
    def from_markdown(cls, content: str, path: Optional[str] = None, filename: Optional[str] = None, last_modified: Optional[float] = None) -> 'WorkEffort':
        """
        Create a WorkEffort from markdown content.

        Args:
            content: Markdown content of the work effort
            path: Path to the file
            filename: Name of the file
            last_modified: Last modified timestamp

        Returns:
            A WorkEffort instance
        """
        # Extract metadata from frontmatter
        metadata_match = re.search(r'---\s+(.*?)\s+---', content, re.DOTALL)
        if not metadata_match:
            raise ValueError("No metadata found in markdown content")

        metadata_text = metadata_match.group(1)
        metadata = {}

        # Parse frontmatter
        for line in metadata_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue

            # Try to parse the line as key-value pair
            try:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                # Special handling for tags
                if key == 'tags':
                    # Try to parse as JSON array
                    try:
                        tags = json.loads(value.replace("'", '"'))
                        metadata[key] = tags
                    except json.JSONDecodeError:
                        # Fallback to manual parsing
                        tags = value.strip('[]').split(',')
                        metadata[key] = [tag.strip() for tag in tags]
                else:
                    metadata[key] = value
            except ValueError:
                # Skip line if it can't be parsed
                continue

        # Extract content sections
        content_dict = {}
        section_pattern = r'## ([^\n]+)\n(.*?)(?=\n## |$)'
        for match in re.finditer(section_pattern, content, re.DOTALL):
            section_title = match.group(1).strip()
            section_content = match.group(2).strip()

            # Convert section title to key
            key = section_title.lower()
            if key.startswith('🚩'):  # Handle emoji in section title
                key = "objectives"
            elif key.startswith('🛠'):
                key = "tasks"
            elif key.startswith('📝'):
                key = "notes"
            elif key.startswith('🐞'):
                key = "issues"
            elif key.startswith('✅'):
                key = "outcomes"
            elif key.startswith('📌'):
                key = "links"
            elif key.startswith('📅'):
                key = "timeline"

            content_dict[key] = section_content

        # Create the WorkEffort
        return cls(
            title=metadata.get('title', "Untitled"),
            assignee=metadata.get('assignee', "self"),
            priority=metadata.get('priority', "medium"),
            due_date=metadata.get('due_date', datetime.now().strftime("%Y-%m-%d")),
            status=metadata.get('status', "active"),
            created=metadata.get('created'),
            last_updated=metadata.get('last_updated'),
            tags=metadata.get('tags', []),
            content=content_dict,
            path=path,
            filename=filename,
            last_modified=last_modified
        )

    @classmethod
    def from_json(cls, json_data: Union[str, Dict]) -> 'WorkEffort':
        """
        Create a WorkEffort from JSON data.

        Args:
            json_data: JSON string or dictionary

        Returns:
            A WorkEffort instance
        """
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Extract metadata
        metadata = data.get('metadata', {})

        # Create the WorkEffort
        return cls(
            title=metadata.get('title', data.get('title', "Untitled")),
            assignee=metadata.get('assignee', data.get('assignee', "self")),
            priority=metadata.get('priority', data.get('priority', "medium")),
            due_date=metadata.get('due_date', data.get('due_date', datetime.now().strftime("%Y-%m-%d"))),
            status=metadata.get('status', data.get('status', "active")),
            created=metadata.get('created', data.get('created')),
            last_updated=metadata.get('last_updated', data.get('last_updated')),
            tags=metadata.get('tags', data.get('tags', [])),
            content=data.get('content', {}),
            path=data.get('path'),
            filename=data.get('filename'),
            last_modified=data.get('last_modified')
        )

    def to_markdown(self) -> str:
        """
        Convert the work effort to markdown format.

        Returns:
            Markdown representation of the work effort
        """
        # Start with metadata
        lines = [
            "---",
            f'title: "{self.title}"',
            f'status: "{self.status.value}" # options: active, paused, completed',
            f'priority: "{self.priority.value}" # options: low, medium, high, critical',
            f'assignee: "{self.assignee}"',
            f'created: "{self.created}" # YYYY-MM-DD HH:mm',
            f'last_updated: "{self.last_updated}" # YYYY-MM-DD HH:mm',
            f'due_date: "{self.due_date}" # YYYY-MM-DD'
        ]

        # Add tags if present
        if self.tags:
            tags_str = ', '.join(self.tags)
            lines.append(f'tags: [{tags_str}]')

        # End metadata
        lines.append("---")
        lines.append("")

        # Add title
        lines.append(f"# {self.title}")
        lines.append("")

        # Add content sections with emojis
        section_emojis = {
            'objectives': '🚩',
            'tasks': '🛠',
            'notes': '📝',
            'issues': '🐞',
            'outcomes': '✅',
            'links': '📌',
            'timeline': '📅'
        }

        for section, emoji in section_emojis.items():
            if section in self.content:
                lines.append(f"## {emoji} {section.title()}")
                lines.append(self.content[section])
                lines.append("")

        # Add any other sections that might not have emojis
        for section, content in self.content.items():
            if section not in section_emojis:
                lines.append(f"## {section.title()}")
                lines.append(content)
                lines.append("")

        return "\n".join(lines)

    def to_json(self, include_content: bool = True) -> Dict:
        """
        Convert the work effort to JSON format.

        Args:
            include_content: Whether to include the content sections

        Returns:
            Dictionary representation of the work effort
        """
        result = {
            "metadata": {
                "title": self.title,
                "status": self.status.value,
                "priority": self.priority.value,
                "assignee": self.assignee,
                "created": self.created,
                "last_updated": self.last_updated,
                "due_date": self.due_date,
                "tags": self.tags
            },
            "filename": self.filename,
            "path": self.path,
            "last_modified": self.last_modified
        }

        if include_content:
            result["content"] = self.content

        return result

    def update_status(self, new_status: Union[str, WorkEffortStatus]) -> None:
        """
        Update the status of this work effort.

        Args:
            new_status: New status to set
        """
        if isinstance(new_status, str):
            self.status = WorkEffortStatus.from_string(new_status)
        else:
            self.status = new_status

        # Update last_updated time
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    def update_content(self, section: str, content: str) -> None:
        """
        Update a content section of this work effort.

        Args:
            section: Section to update
            content: New content
        """
        self.content[section] = content

        # Update last_updated time
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    def __str__(self) -> str:
        """String representation of the work effort."""
        return f"WorkEffort(title={self.title}, status={self.status.value}, priority={self.priority.value})"

    def __repr__(self) -> str:
        """Representation of the work effort for debugging."""
        return self.__str__()


# Standalone functions for working with work efforts

def create_filename_from_title(title: str, timestamp: str, max_length: int = 200) -> str:
    """
    Create a filename from a title and timestamp.

    Args:
        title: The title to use for the filename
        timestamp: The timestamp to prepend to the filename
        max_length: Maximum length of the title part of the filename

    Returns:
        A sanitized filename
    """
    # Convert max_length to int if it's a string
    if isinstance(max_length, str):
        try:
            max_length = int(max_length)
        except ValueError:
            max_length = 200

    # Sanitize title for filename
    safe_title = title.lower()
    # Replace spaces with underscores
    safe_title = safe_title.replace(' ', '_')

    # Replace all special characters - more comprehensive than before
    # This includes: /, \, :, *, ?, ", <, >, |, !, @, #, $, %, ^, &, (, ), +, =, ~, `, [, ], {, }, ;, ', ,, .
    special_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|',
                    '!', '@', '#', '$', '%', '^', '&', '(', ')', '+',
                    '=', '~', '`', '[', ']', '{', '}', ';', "'", ',', '.']

    for char in special_chars:
        safe_title = safe_title.replace(char, '_')

    # Truncate if too long
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length]

    # Create filename
    filename = f"{timestamp}_{safe_title}.md"
    return filename

def extract_metadata_from_markdown(markdown_content: str) -> Dict[str, Any]:
    """
    Extract metadata from markdown frontmatter.

    Args:
        markdown_content: Content of a markdown file with frontmatter

    Returns:
        Dictionary of metadata values
    """
    metadata_match = re.search(r'---\s+(.*?)\s+---', markdown_content, re.DOTALL)
    if not metadata_match:
        return {}

    metadata_text = metadata_match.group(1)
    metadata = {}

    # Parse frontmatter
    for line in metadata_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue

        # Try to parse the line as key-value pair
        try:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Special handling for tags
            if key == 'tags':
                # Try to parse as JSON array
                try:
                    tags = json.loads(value.replace("'", '"'))
                    metadata[key] = tags
                except json.JSONDecodeError:
                    # Fallback to manual parsing
                    tags = value.strip('[]').split(',')
                    metadata[key] = [tag.strip() for tag in tags]
            else:
                metadata[key] = value
        except ValueError:
            # Skip line if it can't be parsed
            continue

    return metadata

def sanitize_title_for_filename(title: str, max_length: int = 200) -> str:
    """
    Sanitize a title for use in a filename.

    Args:
        title: The title to sanitize
        max_length: Maximum length of the title part of the filename

    Returns:
        A sanitized title suitable for use in a filename
    """
    # Convert max_length to int if it's a string
    if isinstance(max_length, str):
        try:
            max_length = int(max_length)
        except ValueError:
            max_length = 200

    # Sanitize title for filename
    safe_title = title.lower()
    # Replace spaces with underscores
    safe_title = safe_title.replace(' ', '_')

    # Replace all special characters - more comprehensive than before
    # This includes: /, \, :, *, ?, ", <, >, |, !, @, #, $, %, ^, &, (, ), +, =, ~, `, [, ], {, }, ;, ', ,, .
    special_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|',
                    '!', '@', '#', '$', '%', '^', '&', '(', ')', '+',
                    '=', '~', '`', '[', ']', '{', '}', ';', "'", ',', '.']

    for char in special_chars:
        safe_title = safe_title.replace(char, '_')

    # Truncate if too long
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length]

    return safe_title