#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort filesystem operations.

This module provides functions for working with work effort files and directories.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Import models
from work_efforts.models.work_effort import (
    WorkEffort,
    extract_metadata_from_markdown,
    create_filename_from_title
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEfforts.Filesystem")

def ensure_directory_structure(project_dir: str) -> Dict[str, str]:
    """
    Ensure that the work efforts directory structure exists.

    Args:
        project_dir: The project directory

    Returns:
        Dictionary of paths to the work effort directories
    """
    # Define paths
    work_efforts_dir = os.path.join(project_dir, "work_efforts")
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")
    templates_dir = os.path.join(work_efforts_dir, "templates")
    scripts_dir = os.path.join(work_efforts_dir, "scripts")

    # Create directories
    os.makedirs(active_dir, exist_ok=True)
    os.makedirs(completed_dir, exist_ok=True)
    os.makedirs(archived_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    logger.info(f"Ensured directory structure in {project_dir}")

    return {
        "work_efforts": work_efforts_dir,
        "active": active_dir,
        "completed": completed_dir,
        "archived": archived_dir,
        "templates": templates_dir,
        "scripts": scripts_dir
    }

def ensure_required_folders(project_dir: str) -> bool:
    """
    Check if the required folders exist in the project.

    Args:
        project_dir: The project directory

    Returns:
        True if both work_efforts and .AI-Setup folders exist
    """
    work_efforts_dir = os.path.join(project_dir, "work_efforts")
    ai_setup_dir = os.path.join(project_dir, ".AI-Setup")

    has_work_efforts = os.path.exists(work_efforts_dir) and os.path.isdir(work_efforts_dir)
    has_ai_setup = os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir)

    return has_work_efforts and has_ai_setup

def load_work_efforts(project_dir: str) -> Dict[str, Dict[str, Dict]]:
    """
    Load all work efforts from the filesystem.

    Args:
        project_dir: The project directory

    Returns:
        Dictionary of work efforts grouped by status
    """
    # Define paths
    work_efforts_dir = os.path.join(project_dir, "work_efforts")
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")

    # Load work efforts from each directory
    work_efforts = {
        "active": load_work_efforts_from_dir(active_dir),
        "completed": load_work_efforts_from_dir(completed_dir),
        "archived": load_work_efforts_from_dir(archived_dir)
    }

    logger.info(f"Loaded {sum(len(v) for v in work_efforts.values())} work efforts from {project_dir}")

    return work_efforts

def load_work_efforts_from_dir(directory: str) -> Dict[str, Dict]:
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
                metadata = extract_metadata_from_file(file_path)
                if metadata:
                    work_efforts[filename] = {
                        "path": file_path,
                        "metadata": metadata,
                        "last_modified": os.path.getmtime(file_path)
                    }
            except Exception as e:
                logger.error(f"Error loading work effort {filename}: {str(e)}")

    return work_efforts

def extract_metadata_from_file(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a work effort file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary of metadata values
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()

        metadata = extract_metadata_from_markdown(content)

        # Add the filename as metadata
        filename = os.path.basename(file_path)
        if "filename" not in metadata:
            metadata["filename"] = filename

        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
        return {}

def save_work_effort(work_effort: WorkEffort, directory: str) -> str:
    """
    Save a work effort to the filesystem.

    Args:
        work_effort: The work effort to save
        directory: The directory to save to

    Returns:
        The path to the saved file
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Generate filename if not provided
    if not work_effort.filename:
        work_effort.filename = create_filename_from_title(work_effort.title)

    # Create the file path
    file_path = os.path.join(directory, work_effort.filename)

    # Update the path in the work effort
    work_effort.path = file_path

    # Convert to markdown
    markdown = work_effort.to_markdown()

    # Write to file
    with open(file_path, "w") as f:
        f.write(markdown)

    # Update last_modified
    work_effort.last_modified = os.path.getmtime(file_path)

    logger.info(f"Saved work effort to {file_path}")

    return file_path

def move_work_effort(filename: str, source_dir: str, target_dir: str) -> str:
    """
    Move a work effort from one directory to another.

    Args:
        filename: The filename of the work effort
        source_dir: The source directory
        target_dir: The target directory

    Returns:
        The path to the moved file
    """
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Create paths
    source_path = os.path.join(source_dir, filename)
    target_path = os.path.join(target_dir, filename)

    # Read the content
    with open(source_path, "r") as f:
        content = f.read()

    # Load as a work effort
    work_effort = WorkEffort.from_markdown(content, path=source_path, filename=filename)

    # Determine the new status based on the target directory
    if "active" in target_dir:
        new_status = "active"
    elif "completed" in target_dir:
        new_status = "completed"
    elif "archived" in target_dir:
        new_status = "archived"
    else:
        new_status = work_effort.status.value  # Keep the same status

    # Update the status
    work_effort.update_status(new_status)

    # Save to target
    with open(target_path, "w") as f:
        f.write(work_effort.to_markdown())

    # Remove the source file
    os.remove(source_path)

    logger.info(f"Moved work effort from {source_path} to {target_path}")

    return target_path

def get_template_path(project_dir: str, use_current_dir: bool = False) -> str:
    """
    Get the path to the work effort template.

    Args:
        project_dir: The project directory
        use_current_dir: Whether to use the current directory

    Returns:
        The path to the template file
    """
    if use_current_dir:
        templates_dir = os.path.join(project_dir, "work_efforts", "templates")
    else:
        # Get the absolute path to the work-efforts directory from the package
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(package_dir, "templates")

    # Create the path to the template
    template_path = os.path.join(templates_dir, "work-effort-template.md")

    # If the template doesn't exist in the specified location, create it
    if not os.path.exists(template_path):
        # Get the default template
        default_template = get_default_template()

        # Create the directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)

        # Write the default template
        with open(template_path, "w") as f:
            f.write(default_template)

        logger.info(f"Created template file at: {template_path}")

    return template_path

def get_default_template() -> str:
    """
    Get the default work effort template.

    Returns:
        The default template content
    """
    return """---
title: "{{title}}"
status: "active" # options: active, paused, completed
priority: "{{priority}}" # options: low, medium, high, critical
assignee: "{{assignee}}"
created: "{{created}}" # YYYY-MM-DD HH:mm
last_updated: "{{last_updated}}" # YYYY-MM-DD HH:mm
due_date: "{{due_date}}" # YYYY-MM-DD
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# {{title}}

## 🚩 Objectives
- Clearly define goals for this work effort.

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references.

## 🐞 Issues Encountered
- Document issues and obstacles clearly.

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes.

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""

def read_work_effort_content(filename: str, status_dir: str) -> Optional[str]:
    """
    Read the content of a work effort.

    Args:
        filename: The filename of the work effort
        status_dir: The directory containing the work effort

    Returns:
        The content of the work effort, or None if not found
    """
    file_path = os.path.join(status_dir, filename)

    if not os.path.exists(file_path):
        logger.error(f"Work effort {filename} not found in {status_dir}")
        return None

    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading work effort {filename}: {str(e)}")
        return None

def load_json_file(file_path: str) -> Dict:
    """
    Load JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary of JSON data
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON in {file_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Save JSON data to a file.

    Args:
        data: Dictionary of JSON data
        file_path: Path to save the JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the JSON data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON data to {file_path}")

        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False