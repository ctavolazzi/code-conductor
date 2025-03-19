#!/usr/bin/env python3
"""
Test basic work effort creation functionality.

This test verifies:
1. Creation of a new work effort with default parameters
2. Folder structure is correctly created
3. Markdown file is properly generated
4. Central index is updated
"""

import os
import sys
import time
import logging
from test_utils import (
    create_test_environment,
    cleanup_test_environment,
    verify_file_exists,
    verify_dir_exists,
    verify_index_contains,
    verify_work_effort_content,
    logger
)

def test_basic_creation():
    """Test basic work effort creation."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting basic work effort creation test")

        # Create a work effort with default parameters
        title = f"Basic Test Work Effort {int(time.time())}"
        folder_path = manager.create_work_effort(
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31",
            use_sequential_numbering=True
        )

        if not folder_path:
            logger.error("Failed to create work effort")
            return False

        # Get the filename
        folder_name = os.path.basename(folder_path)
        filename = f"{folder_name}.md"
        file_path = os.path.join(folder_path, filename)

        # Verify folder and file exist
        if not verify_dir_exists(folder_path):
            return False

        if not verify_file_exists(file_path):
            return False

        # Verify central index is updated
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
        if not verify_file_exists(index_path):
            return False

        if not verify_index_contains(index_path, filename, "active", {"title": title}):
            return False

        # Verify file content
        expected_fields = {
            "title": title,
            "status": "active",
            "priority": "medium",
            "assignee": "tester",
            "due_date": "2025-12-31"
        }
        if not verify_work_effort_content(file_path, expected_fields):
            return False

        logger.info("Basic work effort creation test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_sequential_numbering():
    """Test that sequential numbering works correctly."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting sequential numbering test")

        # Create multiple work efforts and verify numbering
        titles = [
            f"Numbering Test {i}" for i in range(1, 4)
        ]

        filenames = []
        for i, title in enumerate(titles, 1):
            folder_path = manager.create_work_effort(
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31",
                use_sequential_numbering=True
            )

            if not folder_path:
                logger.error(f"Failed to create work effort #{i}")
                return False

            folder_name = os.path.basename(folder_path)

            # Verify the folder name starts with the correct sequential number
            expected_prefix = f"{i:04d}_"  # 0001_, 0002_, etc.
            if not folder_name.startswith(expected_prefix):
                logger.error(f"Invalid sequential numbering. Expected prefix {expected_prefix}, got folder {folder_name}")
                return False

            filenames.append(f"{folder_name}.md")

        # Verify all work efforts exist in the index
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")

        for i, (title, filename) in enumerate(zip(titles, filenames), 1):
            if not verify_index_contains(index_path, filename, "active", {"title": title}):
                return False

        logger.info("Sequential numbering test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def main():
    """Run all tests in this file."""
    tests = [
        ("Basic Creation", test_basic_creation),
        ("Sequential Numbering", test_sequential_numbering),
    ]

    failures = 0

    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        result = test_func()

        if result:
            logger.info(f"✓ {test_name}: PASSED")
        else:
            logger.error(f"✗ {test_name}: FAILED")
            failures += 1

    if failures:
        logger.error(f"{failures} tests failed")
        return 1
    else:
        logger.info("All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())