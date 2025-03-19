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
from typing import Dict, List, Optional, Callable, Any, Union, IO, Tuple
from pathlib import Path

from ...work_efforts.counter import WorkEffortCounter, get_counter, format_work_effort_filename
from ...events import EventEmitter, Event
from .manager_indexer import WorkEffortManagerIndexer
from .manager_validator import WorkEffortManagerValidator
from .manager_parser import WorkEffortManagerParser
from .manager_formatter import WorkEffortManagerFormatter
from .manager_tracer import WorkEffortManagerTracer
from ...config import find_nearest_config, create_or_update_config

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
                 name: str,
                 project_dir: str,
                 info: 'WorkEffortManagerInfo',
                 config: 'WorkEffortManagerConfig',
                 indexer: 'WorkEffortIndexer',
                 validator: 'WorkEffortValidator',
                 tracer: 'WorkEffortTracer',
                 counter: 'WorkEffortCounter',
                 template: 'WorkEffortTemplate',
                 event_emitter: 'EventEmitter'):
        """Initialize the work effort manager.

        Args:
            name: The name of the manager.
            project_dir: The root directory of the project.
            info: Manager information component.
            config: Manager configuration component.
            indexer: Work effort indexer component.
            validator: Work effort validator component.
            tracer: Work effort tracer component.
            counter: Work effort counter component.
            template: Work effort template component.
            event_emitter: Event emitter component.
        """
        self.name = name
        self.project_dir = project_dir
        self.info = info
        self.config = config
        self.indexer = indexer
        self.validator = validator
        self.tracer = tracer
        self.counter = counter
        self.template = template
        self.event_emitter = event_emitter
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Set up directories
        self._setup_directories()

    @property
    def work_efforts_dir(self) -> str:
        """Get the directory containing all work efforts.

        Returns:
            str: Path to the work efforts directory
        """
        return self.config.get("work_efforts_dir", os.path.join(self.project_dir, "_AI-Setup", "work_efforts"))

    def _setup_directories(self) -> None:
        """Set up required directories."""
        try:
            # Get directory paths from config or use defaults
            work_efforts_dir = self.config.get("work_efforts_dir")
            if not work_efforts_dir:
                # Find the nearest config file
                config_file, config_data = find_nearest_config(self.project_dir)
                if config_data and "work_managers" in config_data:
                    # Get default manager if available
                    default_manager = config_data.get("default_manager")
                    if default_manager:
                        for manager in config_data["work_managers"]:
                            if manager.get("name") == default_manager:
                                work_efforts_dir = os.path.join(os.path.dirname(config_file), manager["work_efforts_dir"])
                                break

                    # If no default manager or default manager not found, use first available manager
                    if not work_efforts_dir:
                        for manager in config_data["work_managers"]:
                            if "work_efforts_dir" in manager:
                                work_efforts_dir = os.path.join(os.path.dirname(config_file), manager["work_efforts_dir"])
                                break

            # If still no work efforts directory, use default
            if not work_efforts_dir:
                work_efforts_dir = os.path.join(self.project_dir, "_AI-Setup", "work_efforts")

            templates_dir = os.path.join(work_efforts_dir, "templates")
            history_dir = os.path.join(work_efforts_dir, "history")

            # Set up status directories
            self.active_dir = os.path.join(work_efforts_dir, "active")
            self.completed_dir = os.path.join(work_efforts_dir, "completed")
            self.archived_dir = os.path.join(work_efforts_dir, "archived")
            self.paused_dir = os.path.join(work_efforts_dir, "paused")

            # Create directories if they don't exist
            for directory in [
                work_efforts_dir,
                templates_dir,
                history_dir,
                self.active_dir,
                self.completed_dir,
                self.archived_dir,
                self.paused_dir
            ]:
                os.makedirs(directory, exist_ok=True)

            # Update config with actual paths
            self.config.update({
                "work_efforts_dir": work_efforts_dir,
                "templates_dir": templates_dir,
                "history_dir": history_dir
            })

        except Exception as e:
            self.logger.error(f"Error setting up directories: {str(e)}")
            raise

    def create_work_effort(self, title: str, assignee: str = "self", priority: str = "medium",
                          due_date: Optional[str] = None, description: Optional[str] = None,
                          tags: Optional[List[str]] = None, content: Optional[Dict[str, Any]] = None,
                          use_sequential_numbering: bool = False) -> Optional[str]:
        """Create a new work effort.

        Args:
            title: The title of the work effort.
            assignee: The assignee of the work effort.
            priority: The priority of the work effort.
            due_date: Optional due date for the work effort.
            description: Optional description for the work effort.
            tags: Optional list of tags for the work effort.
            content: Optional dictionary containing additional content sections.
            use_sequential_numbering: Whether to use sequential numbering for the work effort ID.

        Returns:
            The ID of the created work effort if successful, None otherwise.
        """
        try:
            # Generate work effort ID
            if use_sequential_numbering:
                counter = WorkEffortCounter(self.active_dir)
                count = counter.get_next_count()
                work_effort_id = f"{datetime.now().strftime('%Y%m%d%H%M')}_{count:04d}_{title.lower().replace(' ', '_')}"
            else:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                work_effort_id = f"{timestamp}_{title.lower().replace(' ', '_')}"

            # Create work effort metadata
            metadata = {
                "id": work_effort_id,
                "title": title,
                "assignee": assignee,
                "priority": priority,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "tags": tags or []
            }

            if due_date:
                metadata["due_date"] = due_date
            if description:
                metadata["description"] = description

            # Create work effort data
            work_effort_data = {
                "id": work_effort_id,
                "metadata": metadata,
                "content": content or {}  # Add content to work effort data
            }

            # Validate work effort data
            if not self.validator.validate_work_effort_data(metadata):
                return None

            # Format content
            content = self.formatter.format_work_effort(work_effort_data)

            # Write to file
            file_path = os.path.join(self.active_dir, f"{work_effort_id}.md")
            with open(file_path, "w") as f:
                f.write(content)

            # Index all work efforts
            self.index_all_work_efforts()

            return file_path

        except Exception as e:
            self.logger.error(f"Error creating work effort: {str(e)}")
            return None

    def list_work_efforts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all work efforts, optionally filtered by status."""
        try:
            # Force reindex to get latest work efforts
            self.index_all_work_efforts()

            # Get work efforts from indexer
            work_efforts = self.indexer.indexed_work_efforts
            if work_efforts is None:
                work_efforts = {}

            # Filter by status if specified
            if status:
                filtered_efforts = []
                for we in work_efforts.values():
                    if we.get("metadata", {}).get("status") == status:
                        filtered_efforts.append(we)
                return filtered_efforts

            return list(work_efforts.values())
        except Exception as e:
            logger.error(f"Error listing work efforts: {str(e)}")
            return []

    def update_status(self, work_effort_id: str, new_status: str) -> bool:
        """Update the status of a work effort.

        Args:
            work_effort_id: The ID of the work effort.
            new_status: The new status to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get work effort data
            work_effort = self.indexer.get_indexed_work_effort(work_effort_id)
            if not work_effort:
                return False

            # Validate new status
            if not self.validator.validate_status(new_status):
                return False

            # Get old and new file paths
            old_status = work_effort.get("metadata", {}).get("status", "active")  # Default to active if not found

            # Get old and new directories
            status_dirs = {
                "active": self.active_dir,
                "completed": self.completed_dir,
                "archived": self.archived_dir,
                "paused": self.paused_dir
            }

            old_dir = status_dirs.get(old_status)
            new_dir = status_dirs.get(new_status)

            if not old_dir or not new_dir:
                return False

            # Move file to new directory
            old_file = os.path.join(old_dir, f"{work_effort_id}.md")
            new_file = os.path.join(new_dir, f"{work_effort_id}.md")

            if not os.path.exists(old_file):
                return False

            # Update work effort data
            if "metadata" not in work_effort:
                work_effort["metadata"] = {}
            work_effort["metadata"]["status"] = new_status
            work_effort["metadata"]["updated_at"] = datetime.now().isoformat()

            # Format and write updated content
            content = self.formatter.format_work_effort(work_effort)

            # Create new directory if it doesn't exist
            os.makedirs(os.path.dirname(new_file), exist_ok=True)

            # Write updated content to new file
            with open(new_file, "w") as f:
                f.write(content)

            # Remove old file if it exists and is different from new file
            if old_file != new_file and os.path.exists(old_file):
                os.remove(old_file)

            # Update index
            self.index_all_work_efforts()

            return True

        except Exception as e:
            self.logger.error(f"Error updating work effort status: {str(e)}")
            return False

    def index_all_work_efforts(self) -> Dict[str, Any]:
        """Index all work efforts in the work efforts directory.

        Returns:
            A dictionary of indexed work efforts.
        """
        try:
            # Get the work efforts directory from config or use default
            work_efforts_dir = self.config.get("work_efforts_dir", self.work_efforts_dir)
            if not os.path.exists(work_efforts_dir):
                os.makedirs(work_efforts_dir)

            # Index work efforts
            self.indexer.index_all_work_efforts()
            logger.info(f"✅ Indexed work efforts in {work_efforts_dir}")
            return self.indexer.indexed_work_efforts
        except Exception as e:
            logger.error(f"❌ Failed to index work efforts: {str(e)}")
            return {}

    def get_counter(self) -> int:
        """Get the next work effort counter value.

        Returns:
            The next counter value.
        """
        try:
            counter_file = os.path.join(self.config["work_efforts_dir"], "counter.json")

            if os.path.exists(counter_file):
                with open(counter_file, "r") as f:
                    counter_data = json.load(f)
                    return counter_data.get("next_counter", 1)
            else:
                return 1

        except Exception as e:
            self.logger.error(f"Error getting counter: {str(e)}")
            return 1

    def increment_counter(self) -> int:
        """Increment and save the work effort counter.

        Returns:
            The new counter value.
        """
        try:
            counter_file = os.path.join(self.config["work_efforts_dir"], "counter.json")
            next_counter = self.get_counter() + 1

            with open(counter_file, "w") as f:
                json.dump({"next_counter": next_counter}, f)

            return next_counter

        except Exception as e:
            self.logger.error(f"Error incrementing counter: {str(e)}")
            return 1

    def create_new_manager(self, manager_name: str, target_dir: str) -> bool:
        """Create a new work effort manager.

        Args:
            manager_name: Name of the manager.
            target_dir: Directory where the manager will be created.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)

            # Create work efforts directory
            work_efforts_dir = os.path.join(target_dir, "work_efforts")
            os.makedirs(work_efforts_dir, exist_ok=True)

            # Create status directories
            for status in ["active", "completed", "archived", "paused"]:
                os.makedirs(os.path.join(work_efforts_dir, status), exist_ok=True)

            # Create counter.json
            counter_file = os.path.join(target_dir, "counter.json")
            with open(counter_file, "w") as f:
                json.dump({"counter": 0}, f)

            # Create manager config
            manager_config = {
                "name": manager_name,
                "path": target_dir,
                "work_efforts_dir": work_efforts_dir,
                "use_manager": True,
                "auto_start": True
            }

            # Update project config
            config_file, config_data = find_nearest_config()
            if config_file and config_data:
                if "work_managers" not in config_data:
                    config_data["work_managers"] = []
                config_data["work_managers"].append(manager_config)
                create_or_update_config(os.path.dirname(config_file), config_data)

            return True

        except Exception as e:
            logger.error(f"Error creating manager {manager_name}: {str(e)}")
            return False

    def stop(self):
        """Stop the manager and clean up resources."""
        self.running = False
        self.logger.info("Work effort manager stopped")

    def has_required_folders(self) -> bool:
        """Check if all required folders exist."""
        try:
            required_dirs = [
                self.work_efforts_dir,
                os.path.join(self.work_efforts_dir, "active"),
                os.path.join(self.work_efforts_dir, "completed"),
                os.path.join(self.work_efforts_dir, "archived"),
                os.path.join(self.work_efforts_dir, "templates")
            ]
            return all(os.path.exists(d) and os.path.isdir(d) for d in required_dirs)
        except Exception as e:
            self.logger.error(f"Error checking required folders: {str(e)}")
            return False

    def get_work_effort_content(self, filename: str) -> Optional[str]:
        """Get the content of a work effort file.

        Args:
            filename: The filename of the work effort.

        Returns:
            The content of the work effort file if found, None otherwise.
        """
        try:
            file_path = os.path.join(self.active_dir, filename)
            if not os.path.exists(file_path):
                # Try other directories
                for dir_name in ["completed", "archived", "paused"]:
                    dir_path = os.path.join(self.work_efforts_dir, dir_name)
                    file_path = os.path.join(dir_path, filename)
                    if os.path.exists(file_path):
                        break
                else:
                    return None

            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading work effort content: {str(e)}")
            return None

    def get_work_efforts(self, status: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get all work efforts, optionally filtered by status.

        Args:
            status: Optional status to filter by.

        Returns:
            Dictionary of work efforts.
        """
        return self.list_work_efforts(status)

    def register_handler(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Register an event handler.

        Args:
            event_type: The type of event to handle.
            handler: The handler function.
        """
        self.event_emitter.register_handler(event_type, handler)

    def _check_for_changes(self) -> None:
        """Check for changes in work effort files."""
        try:
            # Get all work effort files
            work_efforts = {}
            for status in ["active", "completed", "archived", "paused"]:
                dir_path = os.path.join(self.work_efforts_dir, status)
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        if filename.endswith(".md"):
                            file_path = os.path.join(dir_path, filename)
                            work_efforts[filename] = os.path.getmtime(file_path)

            # Compare with previous state
            if hasattr(self, "_previous_work_efforts"):
                # Check for changes
                for filename, mtime in work_efforts.items():
                    if filename not in self._previous_work_efforts or self._previous_work_efforts[filename] != mtime:
                        # File was added or modified
                        self.event_emitter.emit_event("work_effort_changed", {"filename": filename})

                for filename in self._previous_work_efforts:
                    if filename not in work_efforts:
                        # File was removed
                        self.event_emitter.emit_event("work_effort_removed", {"filename": filename})

            # Update previous state
            self._previous_work_efforts = work_efforts

        except Exception as e:
            self.logger.error(f"Error checking for changes: {str(e)}")

    def create_work_effort_from_json(self, json_str: str) -> Optional[str]:
        """Create a work effort from a JSON string.

        Args:
            json_str: JSON string containing work effort data.

        Returns:
            The ID of the created work effort if successful, None otherwise.
        """
        try:
            data = json.loads(json_str)
            return self.create_work_effort(
                title=data.get("title"),
                assignee=data.get("assignee", "self"),
                priority=data.get("priority", "medium"),
                due_date=data.get("due_date"),
                description=data.get("description"),
                tags=data.get("tags"),
                content=data.get("content")
            )
        except Exception as e:
            self.logger.error(f"Error creating work effort from JSON: {str(e)}")
            return None

    def update_work_effort_status(self, work_effort_id: str, new_status: str, keep_lock: bool = False) -> bool:
        """Update the status of a work effort.

        Args:
            work_effort_id: The ID of the work effort.
            new_status: The new status to set.
            keep_lock: Whether to keep the lock on the file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            work_effort = self.get_work_effort(work_effort_id)
            if not work_effort:
                return False

            file_path = work_effort.get("metadata", {}).get("file_path")
            if not file_path:
                return False

            # Read content
            with open(file_path, "r") as f:
                content = f.read()

            # Update status in content
            old_status = work_effort.get("metadata", {}).get("status", "active")
            content = content.replace(f'status: "{old_status}"', f'status: "{new_status}"')

            # Write updated content
            with open(file_path, "w") as f:
                f.write(content)

            return True
        except Exception as e:
            self.logger.error(f"Error updating work effort status: {str(e)}")
            return False

    def find_related_work_efforts(self, work_effort_id: str) -> List[str]:
        """Find work efforts related to the given one.

        Args:
            work_effort_id: The ID of the work effort.

        Returns:
            List of related work effort IDs.
        """
        try:
            # Get all work efforts
            work_efforts = self.list_work_efforts()
            related = []

            # Get content of the target work effort
            target_content = None
            for we in work_efforts:
                if we.get("id") == work_effort_id:
                    target_content = we.get("content", "")
                    break

            if not target_content:
                return []

            # Look for references in other work efforts
            for we in work_efforts:
                if we.get("id") != work_effort_id:
                    content = we.get("content", "")
                    if work_effort_id in content or (
                        target_content and any(
                            ref in content for ref in [
                                we.get("id", ""),
                                we.get("title", "")
                            ]
                        )
                    ):
                        related.append(we.get("id"))

            return related
        except Exception as e:
            self.logger.error(f"Error finding related work efforts: {str(e)}")
            return []

    def get_work_effort_history(self, work_effort_id: str) -> List[Dict[str, Any]]:
        """Get the history of a work effort.

        Args:
            work_effort_id: The ID of the work effort.

        Returns:
            List of history entries.
        """
        try:
            # Get all work efforts
            work_efforts = self.list_work_efforts()
            history = []

            # Find the work effort
            for we in work_efforts:
                if we.get("id") == work_effort_id:
                    # Add creation entry
                    history.append({
                        "type": "created",
                        "timestamp": we.get("created_at"),
                        "details": f"Created by {we.get('assignee', 'unknown')}"
                    })

                    # Add status changes
                    if "status_history" in we:
                        for status_change in we["status_history"]:
                            history.append({
                                "type": "status_change",
                                "timestamp": status_change["timestamp"],
                                "details": f"Status changed from {status_change['old_status']} to {status_change['new_status']}"
                            })

                    break

            return sorted(history, key=lambda x: x["timestamp"])
        except Exception as e:
            self.logger.error(f"Error getting work effort history: {str(e)}")
            return []

    def trace_work_effort_chain(self, work_effort_id: str) -> List[str]:
        """Trace the chain of related work efforts.

        Args:
            work_effort_id: The ID of the work effort.

        Returns:
            List of work effort IDs in the chain.
        """
        try:
            chain = []
            visited = set()

            def trace_recursive(current_id: str) -> None:
                if current_id in visited:
                    return
                visited.add(current_id)
                chain.append(current_id)
                related = self.find_related_work_efforts(current_id)
                for related_id in related:
                    trace_recursive(related_id)

            trace_recursive(work_effort_id)
            return chain
        except Exception as e:
            self.logger.error(f"Error tracing work effort chain: {str(e)}")
            return []

    def get_work_effort(self, work_effort_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific work effort by ID.

        Args:
            work_effort_id: The ID of the work effort.

        Returns:
            The work effort data if found, None otherwise.
        """
        work_efforts = self.get_work_efforts()
        for we in work_efforts:
            if we.get("id") == work_effort_id:
                return we
        return None