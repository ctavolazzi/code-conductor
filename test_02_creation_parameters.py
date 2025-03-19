#!/usr/bin/env python3
"""
Test work effort creation with different parameter combinations.

This test file verifies various ways to create work efforts with different parameter
combinations to ensure the system handles all valid input types correctly.

Tests included:
1. Creation with different priority levels (low, medium, high, critical)
2. Creation with different assignees (developer, tester, manager, designer, unassigned)
3. Creation with different due date formats (YYYY-MM-DD)
4. Creation with date-prefixed sequential numbering (YYYYMMDDNNNN_title)
5. Creation with timestamp-based naming (YYYYMMDDHHMM_title)
6. Creation with JSON data for programmatic work effort creation

Each test creates work efforts with specific parameters, verifies the folder and file
creation, validates the content of the generated files, and ensures the central index
has been properly updated.
"""

import os
import sys
import time
import json
import re
import traceback
from test_utils import (
    create_test_environment,
    cleanup_test_environment,
    verify_file_exists,
    verify_dir_exists,
    verify_index_contains,
    verify_work_effort_content,
    logger
)

def test_priority_levels():
    """
    Test creation with different priority levels.

    Creates a work effort for each priority level (low, medium, high, critical)
    and verifies that:
    - The folder structure is correctly created
    - The markdown file contains the correct priority
    - The central index is updated with the correct priority value

    Returns:
        bool: True if all priority tests pass, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting priority levels test")

        priorities = ["low", "medium", "high", "critical"]
        folders = []
        filenames = []

        for i, priority in enumerate(priorities, 1):
            logger.info("Testing priority level %d/%d: '%s'", i, len(priorities), priority)
            title = f"Priority Test - {priority}"

            logger.debug("Creating work effort with title='%s', priority='%s'", title, priority)
            folder_path = manager.create_work_effort(
                title=title,
                assignee="tester",
                priority=priority,
                due_date="2025-12-31",
                use_sequential_numbering=True
            )

            if not folder_path:
                logger.error("Failed to create work effort with priority '%s'", priority)
                return False

            # Verify the folder was created
            logger.debug("Verifying folder exists: %s", folder_path)
            if not verify_dir_exists(folder_path):
                logger.error("Directory verification failed for: %s", folder_path)
                return False
            logger.debug("Folder verification successful")

            folders.append(folder_path)
            folder_name = os.path.basename(folder_path)
            filename = f"{folder_name}.md"
            filenames.append(filename)

            # Verify the file exists
            file_path = os.path.join(folder_path, filename)
            logger.debug("Verifying file exists: %s", file_path)
            if not verify_file_exists(file_path):
                logger.error("File verification failed for: %s", file_path)
                return False
            logger.debug("File verification successful")

            # Verify file content has correct priority
            expected_fields = {
                "title": title,
                "priority": priority
            }
            logger.debug("Verifying file content contains: %s", expected_fields)
            if not verify_work_effort_content(file_path, expected_fields):
                logger.error("Content verification failed for file: %s", file_path)
                return False
            logger.debug("Content verification successful")

            # Verify index has correct priority
            index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
            logger.debug("Verifying index at '%s' contains entry for '%s' with priority '%s'",
                        index_path, filename, priority)
            if not verify_index_contains(index_path, filename, "active", {"priority": priority}):
                logger.error("Index verification failed for file '%s' with priority '%s'",
                            filename, priority)
                return False
            logger.debug("Index verification successful")

            logger.info("Priority '%s' test completed successfully", priority)

        logger.info("Priority levels test PASSED - All %d priority levels verified", len(priorities))
        return True
    except Exception as e:
        logger.error("Priority levels test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def test_different_assignees():
    """
    Test creation with different assignees.

    Creates a work effort for each assignee type (developer, tester, manager,
    designer, unassigned) and verifies that:
    - The folder structure is correctly created
    - The markdown file contains the correct assignee
    - The central index is updated with the correct assignee value

    Returns:
        bool: True if all assignee tests pass, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting assignees test")

        assignees = ["developer", "tester", "manager", "designer", "unassigned"]
        folders = []
        filenames = []

        for i, assignee in enumerate(assignees, 1):
            logger.info("Testing assignee %d/%d: '%s'", i, len(assignees), assignee)
            title = f"Assignee Test - {assignee}"

            logger.debug("Creating work effort with title='%s', assignee='%s'", title, assignee)
            folder_path = manager.create_work_effort(
                title=title,
                assignee=assignee,
                priority="medium",
                due_date="2025-12-31",
                use_sequential_numbering=True
            )

            if not folder_path:
                logger.error("Failed to create work effort with assignee '%s'", assignee)
                return False

            # Verify the folder was created
            logger.debug("Verifying folder exists: %s", folder_path)
            if not verify_dir_exists(folder_path):
                logger.error("Directory verification failed for: %s", folder_path)
                return False
            logger.debug("Folder verification successful")

            folders.append(folder_path)
            folder_name = os.path.basename(folder_path)
            filename = f"{folder_name}.md"
            filenames.append(filename)

            # Verify the file exists
            file_path = os.path.join(folder_path, filename)
            logger.debug("Verifying file exists: %s", file_path)
            if not verify_file_exists(file_path):
                logger.error("File verification failed for: %s", file_path)
                return False
            logger.debug("File verification successful")

            # Verify file content has correct assignee
            expected_fields = {
                "title": title,
                "assignee": assignee
            }
            logger.debug("Verifying file content contains: %s", expected_fields)
            if not verify_work_effort_content(file_path, expected_fields):
                logger.error("Content verification failed for file: %s", file_path)
                return False
            logger.debug("Content verification successful")

            # Verify index has correct assignee
            index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
            logger.debug("Verifying index at '%s' contains entry for '%s' with assignee '%s'",
                        index_path, filename, assignee)
            if not verify_index_contains(index_path, filename, "active", {"assignee": assignee}):
                logger.error("Index verification failed for file '%s' with assignee '%s'",
                            filename, assignee)
                return False
            logger.debug("Index verification successful")

            logger.info("Assignee '%s' test completed successfully", assignee)

        logger.info("Assignees test PASSED - All %d assignee types verified", len(assignees))
        return True
    except Exception as e:
        logger.error("Assignees test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def test_date_formats():
    """
    Test creation with different due date formats.

    Creates work efforts with different due dates in YYYY-MM-DD format and verifies:
    - The folder structure is correctly created
    - The markdown file contains the correct due date
    - The central index is updated with the correct due date value

    Returns:
        bool: True if all due date tests pass, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting date formats test")

        due_dates = ["2025-12-31", "2026-01-15", "2030-06-30"]
        folders = []
        filenames = []

        for i, due_date in enumerate(due_dates, 1):
            logger.info("Testing due date %d/%d: '%s'", i, len(due_dates), due_date)
            title = f"Due Date Test - {due_date}"

            logger.debug("Creating work effort with title='%s', due_date='%s'", title, due_date)
            folder_path = manager.create_work_effort(
                title=title,
                assignee="tester",
                priority="medium",
                due_date=due_date,
                use_sequential_numbering=True
            )

            if not folder_path:
                logger.error("Failed to create work effort with due date '%s'", due_date)
                return False

            # Verify the folder was created
            logger.debug("Verifying folder exists: %s", folder_path)
            if not verify_dir_exists(folder_path):
                logger.error("Directory verification failed for: %s", folder_path)
                return False
            logger.debug("Folder verification successful")

            folders.append(folder_path)
            folder_name = os.path.basename(folder_path)
            filename = f"{folder_name}.md"
            filenames.append(filename)

            # Verify the file exists
            file_path = os.path.join(folder_path, filename)
            logger.debug("Verifying file exists: %s", file_path)
            if not verify_file_exists(file_path):
                logger.error("File verification failed for: %s", file_path)
                return False
            logger.debug("File verification successful")

            # Verify file content has correct due date
            expected_fields = {
                "title": title,
                "due_date": due_date
            }
            logger.debug("Verifying file content contains: %s", expected_fields)
            if not verify_work_effort_content(file_path, expected_fields):
                logger.error("Content verification failed for file: %s", file_path)
                return False
            logger.debug("Content verification successful")

            # Verify index has correct due date
            index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
            logger.debug("Verifying index at '%s' contains entry for '%s' with due_date '%s'",
                        index_path, filename, due_date)
            if not verify_index_contains(index_path, filename, "active", {"due_date": due_date}):
                logger.error("Index verification failed for file '%s' with due date '%s'",
                            filename, due_date)
                return False
            logger.debug("Index verification successful")

            logger.info("Due date '%s' test completed successfully", due_date)

        logger.info("Date formats test PASSED - All %d date formats verified", len(due_dates))
        return True
    except Exception as e:
        logger.error("Date formats test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def test_date_prefixed_numbering():
    """
    Test creation with date-prefixed sequential numbering.

    Creates work efforts with date-prefixed sequential numbering (YYYYMMDDNNNN_title format)
    and verifies:
    - The folder structure follows the expected naming pattern
    - The folders and files are correctly created

    The expected format is: YYYYMMDDNNNN_title_with_spaces
    Example: 202503170001_date_prefix_test

    Returns:
        bool: True if all date-prefixed tests pass, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting date-prefixed numbering test")

        titles = [f"Date Prefix Test {i}" for i in range(1, 4)]
        folders = []

        for i, title in enumerate(titles, 1):
            logger.info("Testing date prefix with title %d/%d: '%s'", i, len(titles), title)

            logger.debug("Creating work effort with title='%s', use_date_prefix=True", title)
            folder_path = manager.create_work_effort(
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31",
                use_sequential_numbering=True,
                use_date_prefix=True
            )

            if not folder_path:
                logger.error("Failed to create work effort with date prefix: '%s'", title)
                return False

            # Verify the folder was created
            logger.debug("Verifying folder exists: %s", folder_path)
            if not verify_dir_exists(folder_path):
                logger.error("Directory verification failed for: %s", folder_path)
                return False
            logger.debug("Folder verification successful")

            folders.append(folder_path)
            folder_name = os.path.basename(folder_path)

            # Verify folder name has a date prefix (YYYYMMDD) followed by a sequential number
            # Format example: 202503170001_title
            logger.debug("Verifying folder name format: %s", folder_name)
            if not re.match(r"^\d{8}\d{4}_", folder_name):
                logger.error("Folder name doesn't match date prefix format (YYYYMMDDNNNN_): %s", folder_name)
                return False
            logger.debug("Folder name format verification successful")

            # Verify the file exists
            filename = f"{folder_name}.md"
            file_path = os.path.join(folder_path, filename)
            logger.debug("Verifying file exists: %s", file_path)
            if not verify_file_exists(file_path):
                logger.error("File verification failed for: %s", file_path)
                return False
            logger.debug("File verification successful")

            logger.info("Date prefix test with title '%s' completed successfully", title)

        logger.info("Date-prefixed numbering test PASSED - All %d date-prefixed formats verified", len(titles))
        return True
    except Exception as e:
        logger.error("Date-prefixed numbering test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def test_timestamp_naming():
    """
    Test creation with timestamp-based naming (not sequential).

    Creates a work effort with timestamp-based naming (YYYYMMDDHHMM_title format)
    instead of sequential numbering and verifies:
    - The folder structure follows the expected naming pattern
    - The folders and files are correctly created

    The expected format is: YYYYMMDDHHMM_title_with_spaces
    Example: 202503171245_timestamp_naming_test

    Returns:
        bool: True if the timestamp naming test passes, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting timestamp naming test")

        title = f"Timestamp Naming Test {int(time.time())}"
        logger.debug("Creating work effort with title='%s', use_sequential_numbering=False", title)

        folder_path = manager.create_work_effort(
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31",
            use_sequential_numbering=False  # Use timestamp-based naming
        )

        if not folder_path:
            logger.error("Failed to create work effort with timestamp naming")
            return False

        # Verify the folder was created
        logger.debug("Verifying folder exists: %s", folder_path)
        if not verify_dir_exists(folder_path):
            logger.error("Directory verification failed for: %s", folder_path)
            return False
        logger.debug("Folder verification successful")

        folder_name = os.path.basename(folder_path)

        # Verify folder name has a timestamp format (YYYYMMDDHHMM)
        # Format example: 202503171245_title
        logger.debug("Verifying folder name format: %s", folder_name)
        if not re.match(r"^\d{12}_", folder_name):
            logger.error("Folder name doesn't match timestamp format (YYYYMMDDHHMM_): %s", folder_name)
            return False
        logger.debug("Folder name format verification successful")

        # Verify the file exists
        filename = f"{folder_name}.md"
        file_path = os.path.join(folder_path, filename)
        logger.debug("Verifying file exists: %s", file_path)
        if not verify_file_exists(file_path):
            logger.error("File verification failed for: %s", file_path)
            return False
        logger.debug("File verification successful")

        logger.info("Timestamp naming test PASSED")
        return True
    except Exception as e:
        logger.error("Timestamp naming test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def test_json_data():
    """
    Test creation with JSON data.

    Creates a work effort using JSON data for programmatic creation and verifies:
    - The folder structure is correctly created
    - The markdown file contains all the expected fields from the JSON
    - The content sections (objectives, tasks, notes) are correctly included
    - The central index is updated with the correct values

    JSON Format Example:
    {
      "title": "JSON Data Test",
      "assignee": "json-developer",
      "priority": "high",
      "due_date": "2026-11-30",
      "content": {
        "objectives": ["Test JSON creation", "Verify content parsing"],
        "tasks": ["Implement test", "Verify results"],
        "notes": ["JSON support allows for programmatic creation"]
      }
    }

    Returns:
        bool: True if the JSON data test passes, False otherwise
    """
    test_dir, manager = create_test_environment()
    logger.info("Created test environment at: %s", test_dir)

    try:
        logger.info("Starting JSON data test")

        # Create JSON data
        json_data = {
            "title": "JSON Data Test",
            "assignee": "json-developer",
            "priority": "high",
            "due_date": "2026-11-30",
            "content": {
                "objectives": ["Test JSON creation", "Verify content parsing"],
                "tasks": ["Implement test", "Verify results"],
                "notes": ["JSON support allows for programmatic creation"]
            }
        }

        try:
            json_str = json.dumps(json_data)
            logger.debug("Created JSON string: %s", json_str)
        except (TypeError, ValueError) as e:
            logger.error("Failed to serialize JSON data: %s", str(e))
            return False

        # Create work effort from JSON
        logger.debug("Creating work effort from JSON data")
        folder_path = manager.create_work_effort_from_json(json_str)

        if not folder_path:
            logger.error("Failed to create work effort from JSON")
            return False

        # Verify the folder was created
        logger.debug("Verifying folder exists: %s", folder_path)
        if not verify_dir_exists(folder_path):
            logger.error("Directory verification failed for: %s", folder_path)
            return False
        logger.debug("Folder verification successful")

        folder_name = os.path.basename(folder_path)
        filename = f"{folder_name}.md"

        # Verify the file exists
        file_path = os.path.join(folder_path, filename)
        logger.debug("Verifying file exists: %s", file_path)
        if not verify_file_exists(file_path):
            logger.error("File verification failed for: %s", file_path)
            return False
        logger.debug("File verification successful")

        # Verify file content matches JSON data
        expected_fields = {
            "title": json_data["title"],
            "assignee": json_data["assignee"],
            "priority": json_data["priority"],
            "due_date": json_data["due_date"]
        }
        logger.debug("Verifying file content contains metadata: %s", expected_fields)
        if not verify_work_effort_content(file_path, expected_fields):
            logger.error("Metadata verification failed for file: %s", file_path)
            return False
        logger.debug("Metadata verification successful")

        # Also verify that custom content sections were included
        logger.debug("Verifying file contains custom content sections")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except IOError as e:
            logger.error("Failed to read file content: %s", str(e))
            return False

        # Check for objectives
        logger.debug("Checking for objectives in content")
        if "- Test JSON creation" not in content or "- Verify content parsing" not in content:
            logger.error("Objectives not found in content")
            return False
        logger.debug("Objectives verification successful")

        # Check for tasks
        logger.debug("Checking for tasks in content")
        if "- [ ] Implement test" not in content or "- [ ] Verify results" not in content:
            logger.error("Tasks not found in content")
            return False
        logger.debug("Tasks verification successful")

        # Check for notes
        logger.debug("Checking for notes in content")
        if "- JSON support allows for programmatic creation" not in content:
            logger.error("Notes not found in content")
            return False
        logger.debug("Notes verification successful")

        # Verify index contains the work effort
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
        logger.debug("Verifying index at '%s' contains entry for '%s'", index_path, filename)
        if not verify_index_contains(index_path, filename, "active", {"title": json_data["title"]}):
            logger.error("Index verification failed for file '%s'", filename)
            return False
        logger.debug("Index verification successful")

        logger.info("JSON data test PASSED")
        return True
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    except Exception as e:
        logger.error("JSON data test failed with exception: %s", str(e))
        logger.debug("Exception details: %s", traceback.format_exc())
        return False
    finally:
        logger.info("Cleaning up test environment")
        cleanup_test_environment(test_dir)

def main():
    """
    Run all tests in this file.

    Executes each test function sequentially, logs the results, and provides
    a summary of passed/failed tests.

    Returns:
        int: 0 if all tests pass, 1 if any test fails
    """
    logger.info("Starting parameter tests suite")

    tests = [
        ("Priority Levels", test_priority_levels),
        ("Different Assignees", test_different_assignees),
        ("Date Formats", test_date_formats),
        ("Date-Prefixed Numbering", test_date_prefixed_numbering),
        ("Timestamp Naming", test_timestamp_naming),
        ("JSON Data", test_json_data),
    ]

    failures = 0
    total_tests = len(tests)

    logger.info("Running %d tests", total_tests)

    for i, (test_name, test_func) in enumerate(tests, 1):
        logger.info("Running test %d/%d: %s", i, total_tests, test_name)
        try:
            result = test_func()

            if result:
                logger.info("✓ %s: PASSED", test_name)
            else:
                logger.error("✗ %s: FAILED", test_name)
                failures += 1
        except Exception as e:
            logger.error("✗ %s: ERRORED - Unexpected exception: %s", test_name, str(e))
            logger.debug("Exception details: %s", traceback.format_exc())
            failures += 1

    if failures:
        logger.error("%d/%d tests failed", failures, total_tests)
        return 1
    else:
        logger.info("All %d tests passed!", total_tests)
        return 0

if __name__ == "__main__":
    sys.exit(main())