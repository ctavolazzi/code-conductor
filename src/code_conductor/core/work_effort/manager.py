#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WorkEffortManager - A centralized class for managing work efforts in a project.

This module provides a WorkEffortManager class that handles operations across
the project that the user is working in. It includes an event loop for processing
various work effort related tasks.

Version: 0.5.0
"""

import os
import time
import json
import logging
import re
import fcntl
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union, IO
from pathlib import Path

from ...work_efforts.counter import WorkEffortCounter, get_counter, format_work_effort_filename
from ...events import EventEmitter, Event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEffortManager")

# Constants for validation
MAX_FILENAME_LENGTH = 200
INVALID_FILENAME_CHARS = r'[\\/*?:"<>|]'
VALID_DATE_FORMAT = r'^\d{4}-\d{2}-\d{2}$'
DEFAULT_TITLE = "Untitled"
DEFAULT_DUE_DATE = "2099-12-31"
DEFAULT_PRIORITY = "medium"
DEFAULT_ASSIGNEE = "unassigned"

class WorkEffortManager:
    """
    A class to manage work efforts across a project.

    This class centralizes operations related to work efforts, including creation,
    management, tracking, and reporting. It implements an event loop for handling
    ongoing operations.
    """

    def __init__(self,
                 project_dir: str = None,
                 config: Dict = None,
                 config_json: str = None,
                 config_file: str = None,
                 auto_start: bool = False):
        """
        Initialize the WorkEffortManager.

        Args:
            project_dir: The root directory of the project. If None, uses current directory.
            config: Configuration dictionary for the manager.
            config_json: JSON string containing configuration.
            config_file: Path to a JSON file containing configuration.
            auto_start: Whether to start the event loop automatically.
        """
        self.project_dir = project_dir or os.getcwd()
        self.event_emitter = EventEmitter()

        # Process configuration in order of precedence
        self.config = {}

        # 1. Base config (if provided)
        if config:
            self.config.update(config)

        # 2. Config from JSON file (if provided)
        if config_file:
            file_config = self.load_json_file(config_file)
            if file_config:
                self.config.update(file_config)

        # 3. Config from JSON string (highest precedence)
        if config_json:
            json_config = self.parse_json(config_json)
            if json_config:
                self.config.update(json_config)

        logger.info(f"Initialized with configuration: {self.config}")

        self.running = False
        self.event_handlers = {}
        self.work_efforts = {}
        self.last_updated = datetime.now()

        # Initialize counter
        self.counter = get_counter(self.project_dir)

        if auto_start:
            self.start()

    def load_json_file(self, file_path: str) -> Optional[Dict]:
        """Load configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
            return None

    def parse_json(self, json_str: str) -> Optional[Dict]:
        """Parse configuration from a JSON string."""
        try:
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing config JSON: {e}")
            return None

    def start(self):
        """Start the event loop."""
        if not self.running:
            self.running = True
            self.event_emitter.emit("start", {"timestamp": datetime.now()})
            logger.info("WorkEffortManager started")

    def stop(self):
        """Stop the event loop."""
        if self.running:
            self.running = False
            self.event_emitter.emit("stop", {"timestamp": datetime.now()})
            logger.info("WorkEffortManager stopped")

    def create_work_effort(self,
                          title: str,
                          description: str = "",
                          assignee: str = None,
                          priority: str = None,
                          due_date: str = None,
                          use_ai: bool = False) -> Optional[str]:
        """
        Create a new work effort.

        Args:
            title: The title of the work effort
            description: Optional description
            assignee: Optional assignee
            priority: Optional priority level
            due_date: Optional due date
            use_ai: Whether to use AI for content generation

        Returns:
            Path to the created work effort file if successful, None otherwise
        """
        try:
            # Validate inputs
            title = self._validate_title(title)
            assignee = assignee or DEFAULT_ASSIGNEE
            priority = priority or DEFAULT_PRIORITY
            due_date = due_date or DEFAULT_DUE_DATE

            # Generate filename
            filename = format_work_effort_filename(self.counter.get_next(), title)

            # Create work effort content
            content = self._generate_work_effort_content(
                title=title,
                description=description,
                assignee=assignee,
                priority=priority,
                due_date=due_date
            )

            # Save to file
            file_path = os.path.join(self.project_dir, "_AI-Setup", "work_efforts", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(content)

            # Emit event
            self.event_emitter.emit("work_effort_created", {
                "filename": filename,
                "title": title,
                "assignee": assignee,
                "priority": priority,
                "due_date": due_date
            })

            return file_path

        except Exception as e:
            logger.error(f"Error creating work effort: {e}")
            return None

    def _validate_title(self, title: str) -> str:
        """Validate and clean the work effort title."""
        if not title:
            return DEFAULT_TITLE

        # Remove invalid characters
        title = re.sub(INVALID_FILENAME_CHARS, '', title)

        # Truncate if too long
        if len(title) > MAX_FILENAME_LENGTH:
            title = title[:MAX_FILENAME_LENGTH]

        return title.strip()

    def _generate_work_effort_content(self,
                                    title: str,
                                    description: str,
                                    assignee: str,
                                    priority: str,
                                    due_date: str) -> str:
        """Generate the content for a new work effort."""
        content = [
            f"# {title}",
            "",
            "## Metadata",
            f"- **Assignee:** {assignee}",
            f"- **Priority:** {priority}",
            f"- **Due Date:** {due_date}",
            f"- **Status:** active",
            f"- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Description",
            description,
            "",
            "## Tasks",
            "- [ ] Initial setup",
            "",
            "## Notes",
            ""
        ]
        return "\n".join(content)

    def get_work_effort(self, identifier: str) -> Optional[Dict]:
        """
        Retrieve a work effort by identifier (filename, ID, or title).

        Args:
            identifier: The identifier to search for

        Returns:
            Dictionary containing work effort data if found, None otherwise
        """
        try:
            # Try to find by filename
            if identifier.endswith('.md'):
                file_path = os.path.join(self.project_dir, "_AI-Setup", "work_efforts", identifier)
                if os.path.exists(file_path):
                    return self._load_work_effort(file_path)

            # Try to find by ID
            if identifier.isdigit():
                for filename in os.listdir(os.path.join(self.project_dir, "_AI-Setup", "work_efforts")):
                    if filename.startswith(f"{int(identifier):04d}_"):
                        file_path = os.path.join(self.project_dir, "_AI-Setup", "work_efforts", filename)
                        return self._load_work_effort(file_path)

            # Try to find by title
            for filename in os.listdir(os.path.join(self.project_dir, "_AI-Setup", "work_efforts")):
                if identifier.lower() in filename.lower():
                    file_path = os.path.join(self.project_dir, "_AI-Setup", "work_efforts", filename)
                    return self._load_work_effort(file_path)

            return None

        except Exception as e:
            logger.error(f"Error retrieving work effort: {e}")
            return None

    def _load_work_effort(self, file_path: str) -> Dict:
        """Load a work effort from a file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract metadata
            metadata = {}
            metadata_match = re.search(r'## Metadata\n(.*?)\n\n', content, re.DOTALL)
            if metadata_match:
                for line in metadata_match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip('* ')] = value.strip()

            return {
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "content": content,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error loading work effort from {file_path}: {e}")
            return None

    def update_work_effort(self,
                          identifier: str,
                          updates: Dict) -> bool:
        """
        Update a work effort with new information.

        Args:
            identifier: The identifier of the work effort to update
            updates: Dictionary of updates to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            work_effort = self.get_work_effort(identifier)
            if not work_effort:
                return False

            # Update content based on provided updates
            content = work_effort["content"]

            # Update metadata section
            if "metadata" in updates:
                metadata_section = "## Metadata\n"
                for key, value in updates["metadata"].items():
                    metadata_section += f"- **{key}:** {value}\n"
                metadata_section += "\n"

                # Replace existing metadata section
                content = re.sub(r'## Metadata\n.*?\n\n', metadata_section, content, flags=re.DOTALL)

            # Write updated content back to file
            with open(work_effort["file_path"], 'w') as f:
                f.write(content)

            # Emit event
            self.event_emitter.emit("work_effort_updated", {
                "filename": work_effort["filename"],
                "updates": updates
            })

            return True

        except Exception as e:
            logger.error(f"Error updating work effort: {e}")
            return False

    def list_work_efforts(self,
                         status: str = None,
                         assignee: str = None,
                         priority: str = None) -> List[Dict]:
        """
        List work efforts with optional filtering.

        Args:
            status: Filter by status
            assignee: Filter by assignee
            priority: Filter by priority

        Returns:
            List of work effort dictionaries
        """
        try:
            work_efforts_dir = os.path.join(self.project_dir, "_AI-Setup", "work_efforts")
            if not os.path.exists(work_efforts_dir):
                return []

            work_efforts = []
            for filename in os.listdir(work_efforts_dir):
                if not filename.endswith('.md'):
                    continue

                work_effort = self.get_work_effort(filename)
                if not work_effort:
                    continue

                metadata = work_effort["metadata"]

                # Apply filters
                if status and metadata.get("Status", "").lower() != status.lower():
                    continue
                if assignee and metadata.get("Assignee", "").lower() != assignee.lower():
                    continue
                if priority and metadata.get("Priority", "").lower() != priority.lower():
                    continue

                work_efforts.append(work_effort)

            return work_efforts

        except Exception as e:
            logger.error(f"Error listing work efforts: {e}")
            return []

    def on(self, event: str, handler: Callable):
        """Register an event handler."""
        self.event_emitter.on(event, handler)

    def off(self, event: str, handler: Callable):
        """Remove an event handler."""
        self.event_emitter.off(event, handler)