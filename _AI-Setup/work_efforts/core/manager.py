#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort Manager.

This module provides the main WorkEffortManager class that ties together
all the functionality for managing work efforts.
"""

import os
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union, IO

# Import from other modules
from work_efforts.models.work_effort import (
    WorkEffort,
    WorkEffortStatus,
    WorkEffortPriority,
    create_filename_from_title,
    extract_metadata_from_markdown
)
from work_efforts.filesystem.operations import (
    ensure_directory_structure,
    ensure_required_folders,
    load_work_efforts,
    save_work_effort,
    move_work_effort,
    get_template_path,
    read_work_effort_content
)
from work_efforts.events.event_system import (
    EventEmitter,
    Event,
    register_handler,
    emit_event,
    start_event_loop,
    stop_event_loop
)
from work_efforts.utils.config import (
    parse_json,
    load_json_file,
    save_json_file,
    load_config,
    save_config,
    get_config
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEfforts.Manager")

class WorkEffortManager:
    """
    A class to manage work efforts across a project.

    This class centralizes operations related to work efforts, including creation,
    management, tracking, and reporting. It implements an event loop for handling
    ongoing operations.
    """

    def __init__(
        self,
        project_dir: str = None,
        config: Dict = None,
        config_json: str = None,
        config_file: str = None,
        auto_start: bool = False
    ):
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

        # Process configuration in order of precedence
        self.config = {}

        # 1. Base config (if provided)
        if config:
            self.config.update(config)

        # 2. Config from JSON file (if provided)
        if config_file:
            file_config = load_json_file(config_file)
            if file_config:
                self.config.update(file_config)

        # 3. Config from JSON string (highest precedence)
        if config_json:
            json_config = parse_json(config_json)
            if json_config:
                self.config.update(json_config)

        # 4. Project config (if available)
        project_config = load_config(self.project_dir)

        # Only update with project config if not already set
        for key, value in project_config.items():
            if key not in self.config:
                self.config[key] = value

        logger.info(f"Initialized with configuration: {self.config}")

        # Create event emitter
        self.event_emitter = EventEmitter()

        # Setup work efforts directory structure
        self.path_info = ensure_directory_structure(self.project_dir)
        self.work_efforts_dir = self.path_info["work_efforts"]
        self.active_dir = self.path_info["active"]
        self.completed_dir = self.path_info["completed"]
        self.archived_dir = self.path_info["archived"]

        # Check required folders
        self.has_required_folders_flag = ensure_required_folders(self.project_dir)

        # Load work efforts
        self.work_efforts = load_work_efforts(self.project_dir)

        # Set up state
        self.running = False
        self.last_updated = datetime.now()

        # Start the event loop if requested
        if auto_start:
            self.start()

    # Add essential methods only to keep this file smaller

    def has_required_folders(self) -> bool:
        """
        Check if required folders exist.

        Returns:
            True if both work_efforts and _AI-Setup folders exist
        """
        return self.has_required_folders_flag

    def start(self) -> None:
        """Start the event loop."""
        if self.running:
            logger.warning("Event loop is already running")
            return

        self.running = True

        # Start the event loop
        start_event_loop(self.event_emitter,
                        check_interval=self.config.get("check_interval", 1.0),
                        check_function=self._check_for_changes)

        logger.info("Started event loop")

    def stop(self) -> None:
        """Stop the event loop."""
        if not self.running:
            logger.warning("Event loop is not running")
            return

        self.running = False

        # Stop the event loop
        stop_event_loop(self.event_emitter)

        logger.info("Stopped event loop")

    def _check_for_changes(self) -> None:
        """Check for changes in the work efforts directories."""
        # Reload work efforts
        new_work_efforts = load_work_efforts(self.project_dir)

        # Update state
        self.work_efforts = new_work_efforts
        self.last_updated = datetime.now()

    def create_work_effort(
        self,
        title: str,
        assignee: str,
        priority: str,
        due_date: str,
        content: Dict = None,
        json_data: str = None
    ) -> Optional[str]:
        """
        Create a new work effort.

        Args:
            title: Title of the work effort
            assignee: Person assigned to the work
            priority: Priority level (low, medium, high, critical)
            due_date: Due date in YYYY-MM-DD format
            content: Optional dictionary with content sections
            json_data: Optional JSON string with work effort data

        Returns:
            Path to the created work effort file, or None if required folders don't exist
        """
        # Check if required folders exist
        if not self.has_required_folders():
            logger.error("Cannot create work effort: Required folders (work_efforts and _AI-Setup) not found")
            return None

        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M")

        # Create a WorkEffort object
        work_effort = WorkEffort(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date,
            content=content or {}
        )

        # Generate a filename
        work_effort.filename = create_filename_from_title(title, timestamp)

        # Save the work effort
        file_path = save_work_effort(work_effort, self.active_dir)

        logger.info(f"Created work effort: {file_path}")
        return file_path

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type.

        Args:
            event_type: The type of event to handle
            handler: The function to call when the event occurs
        """
        register_handler(self.event_emitter, event_type, handler)

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event_type: The type of event
            data: The data associated with the event
        """
        emit_event(self.event_emitter, event_type, data)

    # Work effort retrieval methods

    def get_work_efforts(self, status: str = None) -> Dict:
        """
        Get work efforts, optionally filtered by status.

        Args:
            status: Filter by status (active, completed, archived, or None for all)

        Returns:
            Dictionary of work efforts
        """
        if status:
            return self.work_efforts.get(status, {})
        return self.work_efforts

    def filter_work_efforts(
        self,
        location: str = None,
        status: str = None,
        assignee: str = None,
        priority: str = None,
        title_contains: str = None,
        created_after: str = None,
        created_before: str = None,
        due_after: str = None,
        due_before: str = None,
        tags: List[str] = None,
        sort_by: str = None,
        reverse: bool = False,
        limit: int = None
    ) -> List[Dict]:
        """
        Get work efforts with advanced filtering and sorting options.

        Args:
            location: Filter by location folder (active, completed, archived)
            status: Filter by status value in the metadata
            assignee: Filter by assignee
            priority: Filter by priority (low, medium, high, critical)
            title_contains: Filter by title containing this string
            created_after: Filter by creation date after this date (format: YYYY-MM-DD)
            created_before: Filter by creation date before this date (format: YYYY-MM-DD)
            due_after: Filter by due date after this date (format: YYYY-MM-DD)
            due_before: Filter by due date before this date (format: YYYY-MM-DD)
            tags: Filter by having all of these tags
            sort_by: Sort results by this field (created, due_date, priority, title)
            reverse: Reverse the sort order if True
            limit: Limit the number of results

        Returns:
            List of work effort dictionaries with metadata
        """
        results = []

        # Convert string dates to datetime objects for comparison
        created_after_dt = datetime.strptime(created_after, "%Y-%m-%d") if created_after else None
        created_before_dt = datetime.strptime(created_before, "%Y-%m-%d") if created_before else None
        due_after_dt = datetime.strptime(due_after, "%Y-%m-%d") if due_after else None
        due_before_dt = datetime.strptime(due_before, "%Y-%m-%d") if due_before else None

        # Find locations to search
        locations = [location] if location else ["active", "completed", "archived"]
        locations = [loc for loc in locations if loc in self.work_efforts]

        # Filter work efforts
        for loc in locations:
            for filename, info in self.work_efforts[loc].items():
                metadata = info.get("metadata", {})

                # Skip if doesn't match status
                if status and metadata.get("status") != status:
                    continue

                # Skip if doesn't match assignee
                if assignee and metadata.get("assignee") != assignee:
                    continue

                # Skip if doesn't match priority
                if priority and metadata.get("priority") != priority:
                    continue

                # Skip if title doesn't contain the search string
                if title_contains and title_contains.lower() not in metadata.get("title", "").lower():
                    continue

                # Date filtering
                if created_after_dt or created_before_dt:
                    created_str = metadata.get("created", "")
                    if not created_str:
                        continue

                    try:
                        created_dt = datetime.strptime(created_str.split()[0], "%Y-%m-%d")

                        if created_after_dt and created_dt < created_after_dt:
                            continue

                        if created_before_dt and created_dt > created_before_dt:
                            continue
                    except ValueError:
                        continue

                # Due date filtering
                if due_after_dt or due_before_dt:
                    due_date_str = metadata.get("due_date", "")
                    if not due_date_str:
                        continue

                    try:
                        due_date_value = datetime.strptime(due_date_str, "%Y-%m-%d")

                        if due_after_dt and due_date_value < due_after_dt:
                            continue

                        if due_before_dt and due_date_value > due_before_dt:
                            continue
                    except ValueError:
                        continue

                # Tag filtering
                if tags:
                    metadata_tags = metadata.get("tags", [])
                    if not all(tag in metadata_tags for tag in tags):
                        continue

                # If we get here, the work effort passed all filters
                results.append({
                    "filename": filename,
                    "path": info.get("path", ""),
                    "metadata": metadata,
                    "last_modified": info.get("last_modified", 0)
                })

        # Sort results if requested
        if sort_by:
            if sort_by == "created":
                results.sort(key=lambda x: x["metadata"].get("created", ""), reverse=reverse)
            elif sort_by == "due_date":
                results.sort(key=lambda x: x["metadata"].get("due_date", ""), reverse=reverse)
            elif sort_by == "priority":
                # Custom sort order for priority
                priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
                results.sort(
                    key=lambda x: priority_order.get(x["metadata"].get("priority", "low"), 4),
                    reverse=not reverse  # Reverse the reverse since lower numbers are higher priority
                )
            elif sort_by == "title":
                results.sort(key=lambda x: x["metadata"].get("title", ""), reverse=reverse)
            elif sort_by == "last_modified":
                results.sort(key=lambda x: x["last_modified"], reverse=reverse)

        # Apply limit if specified
        if limit and isinstance(limit, int) and limit > 0:
            results = results[:limit]

        return results

    # Helper methods for common queries

    def get_active_work_efforts(self, **kwargs) -> List[Dict]:
        """
        Get active work efforts.

        Args:
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of active work efforts
        """
        # Make sure we don't override location
        kwargs.pop("location", None)

        return self.filter_work_efforts(location="active", **kwargs)

    def get_recent_work_efforts(self, days: int = 7, **kwargs) -> List[Dict]:
        """
        Get work efforts created in the last N days.

        Args:
            days: Number of days to look back
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of recently created work efforts
        """
        # Calculate the date N days ago
        date_n_days_ago = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Make sure we don't override created_after
        kwargs.pop("created_after", None)

        return self.filter_work_efforts(created_after=date_n_days_ago, **kwargs)

    def get_overdue_work_efforts(self, **kwargs) -> List[Dict]:
        """
        Get work efforts that are overdue.

        Args:
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of overdue work efforts
        """
        # Today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Make sure we don't override due_before and status
        kwargs.pop("due_before", None)
        kwargs.pop("status", None)

        return self.filter_work_efforts(
            location="active",  # Only look at active work efforts
            due_before=today,  # Due date is before today
            **kwargs
        )

    def get_work_efforts_by_assignee(self, assignee: str, **kwargs) -> List[Dict]:
        """
        Get work efforts assigned to a specific person.

        Args:
            assignee: The assignee name to filter by
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of work efforts assigned to the specified person
        """
        # Make sure we don't override assignee
        kwargs.pop("assignee", None)

        return self.filter_work_efforts(assignee=assignee, **kwargs)

    def get_work_efforts_by_priority(self, priority: str, **kwargs) -> List[Dict]:
        """
        Get work efforts with a specific priority.

        Args:
            priority: The priority to filter by (low, medium, high, critical)
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of work efforts with the specified priority
        """
        # Make sure we don't override priority
        kwargs.pop("priority", None)

        return self.filter_work_efforts(priority=priority, **kwargs)

    def get_work_effort_content(self, filename: str, status: str = "active") -> Optional[str]:
        """
        Get the content of a work effort.

        Args:
            filename: The filename of the work effort
            status: The status of the work effort

        Returns:
            The content of the work effort, or None if not found
        """
        if status in self.work_efforts and filename in self.work_efforts[status]:
            file_path = self.work_efforts[status][filename]["path"]
            try:
                with open(file_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading work effort {filename}: {str(e)}")
        return None

    def update_work_effort_status(self, filename: str, new_status: str,
                               old_status: str = "active") -> bool:
        """
        Update the status of a work effort.

        Args:
            filename: The filename of the work effort
            new_status: The new status (active, completed, archived)
            old_status: The current status of the work effort

        Returns:
            True if successful, False otherwise
        """
        if old_status not in self.work_efforts or filename not in self.work_efforts[old_status]:
            logger.error(f"Work effort {filename} not found in {old_status}")
            return False

        if new_status not in ["active", "completed", "archived"]:
            logger.error(f"Invalid status: {new_status}")
            return False

        # Get file paths
        old_path = self.work_efforts[old_status][filename]["path"]
        new_dir = getattr(self, f"{new_status}_dir")

        try:
            # Move the work effort
            new_path = move_work_effort(filename, os.path.dirname(old_path), new_dir)

            # Update the in-memory cache
            info = self.work_efforts[old_status].pop(filename)
            info["path"] = new_path
            info["metadata"]["status"] = new_status
            info["last_modified"] = os.path.getmtime(new_path)
            self.work_efforts[new_status][filename] = info

            # Emit an event
            self.emit_event("work_effort_status_changed", {
                "filename": filename,
                "old_status": old_status,
                "new_status": new_status
            })

            logger.info(f"Updated work effort status: {filename} from {old_status} to {new_status}")
            return True
        except Exception as e:
            logger.error(f"Error updating work effort status: {str(e)}")
            return False

    def __str__(self) -> str:
        """String representation of the WorkEffortManager."""
        counts = {status: len(items) for status, items in self.work_efforts.items()}
        return (f"WorkEffortManager(project={os.path.basename(self.project_dir)}, "
                f"active={counts['active']}, completed={counts['completed']}, "
                f"archived={counts['archived']}, running={self.running})")


# Factory function to create a manager
def create_manager(project_dir: str = None, **kwargs) -> WorkEffortManager:
    """
    Create a WorkEffortManager.

    Args:
        project_dir: The project directory
        **kwargs: Additional arguments to pass to the WorkEffortManager constructor

    Returns:
        A new WorkEffortManager
    """
    return WorkEffortManager(project_dir=project_dir, **kwargs)


# Module-level functions that use the manager

def create_work_effort(manager: WorkEffortManager, title: str, assignee: str, priority: str,
                     due_date: str, content: Dict = None, json_data: str = None) -> Optional[str]:
    """
    Create a work effort using a manager.

    Args:
        manager: The WorkEffortManager to use
        title: Title of the work effort
        assignee: Person assigned to the work
        priority: Priority level (low, medium, high, critical)
        due_date: Due date in YYYY-MM-DD format
        content: Optional dictionary with content sections
        json_data: Optional JSON string with work effort data

    Returns:
        Path to the created work effort file, or None if required folders don't exist
    """
    return manager.create_work_effort(title, assignee, priority, due_date, content, json_data)

def get_work_efforts(manager: WorkEffortManager, status: str = None) -> Dict:
    """
    Get work efforts from a manager.

    Args:
        manager: The WorkEffortManager to use
        status: Filter by status (active, completed, archived, or None for all)

    Returns:
        Dictionary of work efforts
    """
    return manager.get_work_efforts(status)

def filter_work_efforts(manager: WorkEffortManager, **kwargs) -> List[Dict]:
    """
    Filter work efforts using a manager.

    Args:
        manager: The WorkEffortManager to use
        **kwargs: Filter arguments to pass to filter_work_efforts

    Returns:
        List of filtered work efforts
    """
    return manager.filter_work_efforts(**kwargs)

def update_work_effort_status(manager: WorkEffortManager, filename: str, new_status: str,
                           old_status: str = "active") -> bool:
    """
    Update the status of a work effort using a manager.

    Args:
        manager: The WorkEffortManager to use
        filename: The filename of the work effort
        new_status: The new status (active, completed, archived)
        old_status: The current status of the work effort

    Returns:
        True if successful, False otherwise
    """
    return manager.update_work_effort_status(filename, new_status, old_status)