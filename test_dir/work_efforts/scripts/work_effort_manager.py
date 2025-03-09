#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WorkEffortManager - A centralized class for managing work efforts in a project.

This module provides a WorkEffortManager class that handles operations across
the project that the user is working in. It includes an event loop for processing
various work effort related tasks.

Version: 0.4.2
"""

import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union, IO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEffortManager")

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

        # Setup work efforts directory structure if it doesn't exist
        self.work_efforts_dir = os.path.join(self.project_dir, "work_efforts")
        self.active_dir = os.path.join(self.work_efforts_dir, "active")
        self.completed_dir = os.path.join(self.work_efforts_dir, "completed")
        self.archived_dir = os.path.join(self.work_efforts_dir, "archived")
        self.templates_dir = os.path.join(self.work_efforts_dir, "templates")
        self.scripts_dir = os.path.join(self.work_efforts_dir, "scripts")
        self.ai_setup_dir = os.path.join(self.project_dir, ".AI-Setup")

        # Check if required directories exist
        self.has_work_efforts_dir = os.path.exists(self.work_efforts_dir) and os.path.isdir(self.work_efforts_dir)
        self.has_ai_setup_dir = os.path.exists(self.ai_setup_dir) and os.path.isdir(self.ai_setup_dir)

        logger.info(f"Work efforts directory exists: {self.has_work_efforts_dir}")
        logger.info(f".AI-Setup directory exists: {self.has_ai_setup_dir}")

        # We only load work efforts if the directory exists
        if self.has_work_efforts_dir:
            self._load_work_efforts()

        if auto_start:
            self.start()

    @staticmethod
    def parse_json(json_str: str) -> Dict:
        """
        Parse a JSON string into a dictionary.

        Args:
            json_str: JSON string to parse

        Returns:
            Dictionary parsed from JSON, or empty dict if parsing fails
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return {}

    @staticmethod
    def load_json_file(file_path: str) -> Dict:
        """
        Load a JSON file into a dictionary.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary loaded from JSON file, or empty dict if loading fails
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            return {}

    def save_json_file(self, data: Dict, file_path: str) -> bool:
        """
        Save a dictionary as a JSON file.

        Args:
            data: Dictionary to save
            file_path: Path where the JSON file should be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved JSON data to {file_path}")
            return True
        except (TypeError, PermissionError) as e:
            logger.error(f"Error saving JSON to {file_path}: {str(e)}")
            return False

    def has_required_folders(self) -> bool:
        """
        Check if the required folders exist.

        Returns:
            True if both work_efforts and .AI-Setup folders exist
        """
        return self.has_work_efforts_dir and self.has_ai_setup_dir

    def _ensure_directory_structure(self) -> None:
        """Ensure all required directories exist if work_efforts directory exists."""
        if not self.has_work_efforts_dir:
            logger.warning(f"work_efforts directory does not exist at {self.work_efforts_dir}")
            return

        for dir_path in [
            self.active_dir,
            self.completed_dir,
            self.archived_dir,
            self.templates_dir,
            self.scripts_dir
        ]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")

        logger.info(f"Ensured directory structure at {self.work_efforts_dir}")

    def _load_work_efforts(self) -> None:
        """Load all work efforts from the filesystem."""
        self.work_efforts = {
            "active": self._load_work_efforts_from_dir(self.active_dir),
            "completed": self._load_work_efforts_from_dir(self.completed_dir),
            "archived": self._load_work_efforts_from_dir(self.archived_dir)
        }
        logger.info(f"Loaded {sum(len(v) for v in self.work_efforts.values())} work efforts")

    def _load_work_efforts_from_dir(self, directory: str) -> Dict[str, Dict]:
        """
        Load work efforts from a specific directory.

        Args:
            directory: The directory to load from

        Returns:
            Dictionary mapping filenames to work effort metadata
        """
        if not os.path.exists(directory):
            return {}

        work_efforts = {}
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                file_path = os.path.join(directory, filename)
                try:
                    metadata = self._extract_metadata(file_path)
                    if metadata:
                        work_efforts[filename] = {
                            "path": file_path,
                            "metadata": metadata,
                            "last_modified": os.path.getmtime(file_path)
                        }
                except Exception as e:
                    logger.error(f"Error loading work effort {filename}: {str(e)}")

        return work_efforts

    def _extract_metadata(self, file_path: str) -> Dict:
        """
        Extract metadata from a work effort markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary of metadata
        """
        metadata = {}
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Extract YAML frontmatter
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    frontmatter = content[3:end_idx].strip()
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = value.strip().strip('"')
                            metadata[key] = value
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")

        return metadata

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: The type of event to handle
            handler: The function to call when this event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event_type: The type of event
            data: Data to pass to the handlers
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")

    def start(self) -> None:
        """Start the event loop."""
        if self.running:
            logger.warning("Event loop already running")
            return

        self.running = True
        logger.info("Starting WorkEffortManager event loop")

        try:
            self._run_event_loop()
        except KeyboardInterrupt:
            logger.info("WorkEffortManager event loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in WorkEffortManager event loop: {str(e)}")
        finally:
            self.running = False

    def stop(self) -> None:
        """Stop the event loop."""
        if not self.running:
            logger.warning("Event loop not running")
            return

        logger.info("Stopping WorkEffortManager event loop")
        self.running = False

    def _run_event_loop(self) -> None:
        """Run the main event loop."""
        while self.running:
            # Check for file system changes
            self._check_for_changes()

            # Emit a heartbeat event
            self.emit_event("heartbeat", {"timestamp": datetime.now()})

            # Sleep to avoid high CPU usage
            time.sleep(self.config.get("loop_interval", 2))

    def _check_for_changes(self) -> None:
        """Check for changes in the work efforts directories."""
        # We'll implement a simple polling mechanism here
        # In a production system, you might want to use something like watchdog
        for status, directory in [
            ("active", self.active_dir),
            ("completed", self.completed_dir),
            ("archived", self.archived_dir)
        ]:
            current = self._load_work_efforts_from_dir(directory)

            # Check for new or modified files
            for filename, info in current.items():
                if filename not in self.work_efforts[status]:
                    # New file
                    self.work_efforts[status][filename] = info
                    self.emit_event("work_effort_created", {
                        "filename": filename,
                        "status": status,
                        "metadata": info["metadata"]
                    })
                elif info["last_modified"] > self.work_efforts[status][filename]["last_modified"]:
                    # Modified file
                    self.work_efforts[status][filename] = info
                    self.emit_event("work_effort_updated", {
                        "filename": filename,
                        "status": status,
                        "metadata": info["metadata"]
                    })

            # Check for deleted files
            for filename in list(self.work_efforts[status].keys()):
                if filename not in current:
                    # Deleted file
                    self.emit_event("work_effort_deleted", {
                        "filename": filename,
                        "status": status
                    })
                    del self.work_efforts[status][filename]

        self.last_updated = datetime.now()

    def create_work_effort(self, title: str, assignee: str, priority: str,
                          due_date: str, content: Dict = None, json_data: str = None) -> Optional[str]:
        """
        Create a new work effort if both work_efforts and .AI-Setup folders exist.

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
            logger.error("Cannot create work effort: Required folders (work_efforts and .AI-Setup) not found")
            return None

        # Process JSON data if provided
        if json_data:
            try:
                json_content = self.parse_json(json_data)
                # Extract main fields from JSON if available
                title = json_content.get("title", title)
                assignee = json_content.get("assignee", assignee)
                priority = json_content.get("priority", priority)
                due_date = json_content.get("due_date", due_date)

                # Merge content dictionaries if both exist
                if "content" in json_content:
                    if content:
                        content.update(json_content["content"])
                    else:
                        content = json_content["content"]

                logger.info(f"Processed JSON data for work effort: {title}")
            except Exception as e:
                logger.error(f"Error processing JSON data: {str(e)}")

        # This is a simplified version - in practice you'd probably want to
        # reuse code from existing work effort scripts
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        filename_timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"{filename_timestamp}_{title.lower().replace(' ', '_')}.md"
        file_path = os.path.join(self.active_dir, filename)

        # Basic template
        template = f"""---
title: "{title}"
status: "active"
priority: "{priority}"
assignee: "{assignee}"
created: "{timestamp}"
last_updated: "{timestamp}"
due_date: "{due_date}"
tags: []
---

# {title}

## 🚩 Objectives
- Define the goals of this work effort

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Add context and notes here

## 🐞 Issues Encountered
- Document any issues

## ✅ Outcomes & Results
- Record outcomes when completed

## 📌 Linked Items
- Link to related work efforts or issues

## 📅 Timeline & Progress
- **Started**: {timestamp}
- **Updated**: {timestamp}
- **Target Completion**: {due_date}
"""

        # Customize template with content if provided
        if content:
            if "objectives" in content:
                objectives = "\n".join([f"- {obj}" for obj in content["objectives"]]) if isinstance(content["objectives"], list) else content["objectives"]
                template = template.replace("- Define the goals of this work effort", objectives)

            if "tasks" in content:
                tasks = "\n".join([f"- [ ] {task}" for task in content["tasks"]]) if isinstance(content["tasks"], list) else content["tasks"]
                template = template.replace("- [ ] Task 1\n- [ ] Task 2", tasks)

            if "notes" in content:
                notes = "\n".join([f"- {note}" for note in content["notes"]]) if isinstance(content["notes"], list) else content["notes"]
                template = template.replace("- Add context and notes here", notes)

        with open(file_path, "w") as f:
            f.write(template)

        # Update in-memory cache
        self.work_efforts["active"][filename] = {
            "path": file_path,
            "metadata": {
                "title": title,
                "status": "active",
                "priority": priority,
                "assignee": assignee,
                "created": timestamp,
                "last_updated": timestamp,
                "due_date": due_date
            },
            "last_modified": os.path.getmtime(file_path)
        }

        self.emit_event("work_effort_created", {
            "filename": filename,
            "status": "active",
            "metadata": self.work_efforts["active"][filename]["metadata"]
        })

        logger.info(f"Created work effort: {file_path}")
        return file_path

    def create_work_effort_from_json(self, json_data: Union[str, Dict, IO]) -> Optional[str]:
        """
        Create a work effort from JSON data.

        Args:
            json_data: JSON string, file-like object, or dictionary

        Returns:
            Path to the created work effort file, or None if creation fails
        """
        # Process various input formats
        if isinstance(json_data, str):
            # If it's a string, try to parse it as JSON
            data = self.parse_json(json_data)
        elif hasattr(json_data, 'read'):
            # If it's a file-like object
            try:
                data = json.load(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading JSON from file: {str(e)}")
                return None
        elif isinstance(json_data, dict):
            # If it's already a dictionary
            data = json_data
        else:
            logger.error(f"Unsupported JSON data type: {type(json_data)}")
            return None

        # Extract required fields
        title = data.get("title")
        assignee = data.get("assignee")
        priority = data.get("priority")
        due_date = data.get("due_date")

        # Validate required fields
        if not all([title, assignee, priority, due_date]):
            missing = []
            if not title: missing.append("title")
            if not assignee: missing.append("assignee")
            if not priority: missing.append("priority")
            if not due_date: missing.append("due_date")

            logger.error(f"Missing required fields in JSON data: {', '.join(missing)}")
            return None

        # Extract content if present
        content = data.get("content")

        # Create the work effort
        return self.create_work_effort(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date,
            content=content
        )

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

    def filter_work_efforts(self,
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
                           limit: int = None) -> List[Dict]:
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
        # Start with all work efforts or filter by location
        if location:
            work_efforts_dict = self.work_efforts.get(location, {})
        else:
            # Combine all locations into a single dictionary
            work_efforts_dict = {}
            for loc in self.work_efforts:
                work_efforts_dict.update(self.work_efforts[loc])

        # Convert to list for easier filtering and sorting
        results = []

        for filename, info in work_efforts_dict.items():
            metadata = info.get("metadata", {})

            # Apply filters
            if status and metadata.get("status") != status:
                continue

            if assignee and metadata.get("assignee") != assignee:
                continue

            if priority and metadata.get("priority") != priority:
                continue

            if title_contains and title_contains.lower() not in metadata.get("title", "").lower():
                continue

            # Date filtering
            if created_after or created_before:
                created_date = metadata.get("created", "").split(" ")[0]  # Get just the date part

                if created_after and created_date < created_after:
                    continue

                if created_before and created_date > created_before:
                    continue

            if due_after or due_before:
                due_date_value = metadata.get("due_date", "")

                if due_after and due_date_value < due_after:
                    continue

                if due_before and due_date_value > due_before:
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

    def get_active_work_efforts(self, **kwargs) -> List[Dict]:
        """
        Convenience method to get active work efforts with optional additional filtering.

        Args:
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of active work efforts
        """
        # Make sure we don't override location and status
        kwargs.pop("location", None)
        kwargs.pop("status", None)

        return self.filter_work_efforts(location="active", status="active", **kwargs)

    def get_recent_work_efforts(self, days: int = 7, **kwargs) -> List[Dict]:
        """
        Get work efforts created in the last N days.

        Args:
            days: Number of days to look back
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of recent work efforts
        """
        from datetime import datetime, timedelta

        # Calculate the date N days ago
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Make sure we don't override created_after
        kwargs.pop("created_after", None)

        return self.filter_work_efforts(created_after=start_date,
                                       sort_by="created",
                                       reverse=True,
                                       **kwargs)

    def get_overdue_work_efforts(self, **kwargs) -> List[Dict]:
        """
        Get work efforts that are past their due date.

        Args:
            **kwargs: Additional filter arguments to pass to filter_work_efforts

        Returns:
            List of overdue work efforts
        """
        from datetime import datetime

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Make sure we don't override due_before and status
        kwargs.pop("due_before", None)

        # Only include active work efforts that are overdue
        return self.filter_work_efforts(status="active",
                                       due_before=today,
                                       sort_by="due_date",
                                       **kwargs)

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
        new_path = os.path.join(new_dir, filename)

        try:
            # Read the content
            with open(old_path, "r") as f:
                content = f.read()

            # Update the status in the content
            content = content.replace('status: "' + old_status + '"', 'status: "' + new_status + '"')

            # Write to the new location
            with open(new_path, "w") as f:
                f.write(content)

            # Remove the old file
            os.remove(old_path)

            # Update the in-memory cache
            info = self.work_efforts[old_status].pop(filename)
            info["path"] = new_path
            info["metadata"]["status"] = new_status
            info["last_modified"] = os.path.getmtime(new_path)
            self.work_efforts[new_status][filename] = info

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


# Example usage when run as script
if __name__ == "__main__":
    try:
        print("Initializing WorkEffortManager...")
        manager = WorkEffortManager(auto_start=True)
    except KeyboardInterrupt:
        print("\nWorkEffortManager terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}")