#!/usr/bin/env python3
"""
Test utilities for the work effort manager test suite.

This module provides common functionality used across different test files.
"""

import os
import sys
import json
import time
import shutil
import logging
from typing import Optional, Dict, List, Any, Tuple

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="TEST: %(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_utils")

# Import WorkEffortManager
try:
    from code_conductor.core.work_effort.manager import WorkEffortManager
except ImportError:
    logger.warning("Failed to import from code_conductor.core.work_effort.manager, trying alternative import paths")
    try:
        # Try importing from src directory
        from src.code_conductor.core.work_effort.manager import WorkEffortManager
    except ImportError:
        logger.error("Failed to import WorkEffortManager. Make sure the package is installed or in PYTHONPATH")
        raise

def create_test_environment() -> Tuple[str, WorkEffortManager]:
    """
    Create a clean test environment in a temporary directory.

    Returns:
        Tuple of (test_dir_path, manager_instance)
    """
    # Create a temporary test directory
    test_dir = os.path.join(os.getcwd(), "test_work_efforts_tmp")

    # Clean up any existing test directory
    if os.path.exists(test_dir):
        try:
            shutil.rmtree(test_dir)
            logger.info(f"Cleaned up existing test directory: {test_dir}")
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to clean up existing test directory: {e}")
            # Try renaming instead
            old_dir = f"{test_dir}_old_{int(time.time())}"
            os.rename(test_dir, old_dir)
            logger.info(f"Renamed old test directory to: {old_dir}")

    # Create fresh test directory with required structure
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "work_efforts"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "work_efforts", "active"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "work_efforts", "completed"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "work_efforts", "archived"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "work_efforts", "templates"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "_AI-Setup"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, ".code_conductor"), exist_ok=True)

    # Create counter.json file
    counter_file = os.path.join(test_dir, "work_efforts", "counter.json")
    with open(counter_file, 'w') as f:
        json.dump({"count": 0, "prefix": ""}, f)

    # Initialize manager
    manager = WorkEffortManager(project_dir=test_dir)

    return (test_dir, manager)

def cleanup_test_environment(test_dir: str) -> None:
    """Clean up the test environment after tests."""
    if os.path.exists(test_dir):
        try:
            shutil.rmtree(test_dir)
            logger.info(f"Cleaned up test directory: {test_dir}")
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to clean up test directory: {e}")
            # If we can't delete, at least rename it to indicate it's obsolete
            try:
                new_name = f"{test_dir}_obsolete_{int(time.time())}"
                os.rename(test_dir, new_name)
                logger.info(f"Renamed obsolete test directory to: {new_name}")
            except:
                logger.error(f"Failed to rename test directory")

def verify_file_exists(path: str) -> bool:
    """Verify that a file exists."""
    exists = os.path.isfile(path)
    if exists:
        logger.info(f"File exists: {path}")
    else:
        logger.error(f"File does not exist: {path}")
    return exists

def verify_dir_exists(path: str) -> bool:
    """Verify that a directory exists."""
    exists = os.path.isdir(path)
    if exists:
        logger.info(f"Directory exists: {path}")
    else:
        logger.error(f"Directory does not exist: {path}")
    return exists

def verify_index_contains(index_path: str, filename: str, status: str, expected_fields: Dict[str, Any] = None) -> bool:
    """
    Verify that the index file contains an entry for the given filename with expected values.

    Args:
        index_path: Path to the index file
        filename: Filename to look for
        status: Status section to look in (active, completed, archived)
        expected_fields: Dictionary of fields and values to verify in the metadata

    Returns:
        True if verification passes, False otherwise
    """
    try:
        with open(index_path, 'r') as f:
            index_data = json.load(f)

        # Check if the work_efforts key exists
        if "work_efforts" not in index_data:
            logger.error(f"No work_efforts key in index file")
            return False

        # Check if the status section exists
        if status not in index_data["work_efforts"]:
            logger.error(f"No {status} section in index file")
            return False

        # Check if the filename exists in the status section
        if filename not in index_data["work_efforts"][status]:
            logger.error(f"File {filename} not found in {status} section")
            return False

        # If expected fields were provided, verify them
        if expected_fields:
            work_effort = index_data["work_efforts"][status][filename]
            metadata = work_effort.get("metadata", {})

            for field, expected_value in expected_fields.items():
                if field not in metadata:
                    logger.error(f"Field {field} not found in metadata")
                    return False

                actual_value = metadata[field]
                if actual_value != expected_value:
                    logger.error(f"Field {field} has value {actual_value}, expected {expected_value}")
                    return False

        logger.info(f"Index verification passed for {filename} in {status}")
        return True
    except Exception as e:
        logger.error(f"Error verifying index: {str(e)}")
        return False

def create_test_work_effort(manager: WorkEffortManager, **kwargs) -> Tuple[Optional[str], Optional[str]]:
    """
    Create a test work effort with default or provided parameters.

    Args:
        manager: WorkEffortManager instance
        **kwargs: Parameters to pass to create_work_effort

    Returns:
        Tuple of (folder_path, filename) or (None, None) if creation failed
    """
    # Default parameters
    params = {
        "title": f"Test Work Effort {int(time.time())}",
        "assignee": "tester",
        "priority": "medium",
        "due_date": "2025-12-31",
        "use_sequential_numbering": True
    }

    # Override with provided parameters
    params.update(kwargs)

    # Create the work effort
    folder_path = manager.create_work_effort(**params)

    if not folder_path:
        logger.error("Failed to create work effort")
        return (None, None)

    # Get the filename from the folder path
    folder_name = os.path.basename(folder_path)
    filename = f"{folder_name}.md"

    logger.info(f"Created work effort: {folder_path}")
    return (folder_path, filename)

def verify_work_effort_content(file_path: str, expected_fields: Dict[str, str]) -> bool:
    """
    Verify that a work effort file contains expected fields in its metadata.

    Args:
        file_path: Path to the work effort file
        expected_fields: Dictionary of fields and expected values

    Returns:
        True if verification passes, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        for field, expected_value in expected_fields.items():
            # For YAML frontmatter fields, check for field: "value"
            pattern = f'{field}: "{expected_value}"'
            if pattern not in content:
                logger.error(f"Field {field} with value {expected_value} not found in file content")
                return False

        logger.info(f"Content verification passed for {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error verifying content: {str(e)}")
        return False