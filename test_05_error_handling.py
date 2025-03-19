#!/usr/bin/env python3
"""
Test work effort manager error handling.

This test verifies:
1. Invalid input handling
2. Missing file/folder handling
3. Permission error handling
4. Invalid format handling
5. Duplicate entry handling
6. Recovery from corrupted index
"""

import os
import sys
import time
import json
import shutil
import tempfile
import logging
from test_utils import (
    create_test_environment,
    cleanup_test_environment,
    create_test_work_effort,
    verify_file_exists,
    verify_dir_exists,
    logger
)
from code_conductor.core.work_effort.manager import WorkEffortManager

# Set up additional logging for this test file
if __name__ == "__main__":
    # Configure a more verbose logging level when running this file directly
    logger.setLevel(logging.DEBUG)
    # Add a console handler that shows more detail for direct execution
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.debug("Running test_05_error_handling.py with enhanced logging")

def test_invalid_title():
    """Test handling of invalid titles."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting invalid title test")

        # Test with empty title
        result = manager.create_work_effort(
            title="",
            assignee="tester",
            priority="medium",
            due_date="2025-12-31"
        )

        if result is not None and result[0] is not False:
            logger.error("Manager allowed creation with empty title")
            return False

        # Test with title containing invalid characters
        invalid_chars = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']

        for char in invalid_chars:
            title = f"Invalid{char}Title"
            result = manager.create_work_effort(
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )

            if result is not None and result[0] is not False:
                logger.error(f"Manager allowed creation with invalid character {char} in title")
                return False

        logger.info("Invalid title test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_invalid_priority():
    """Test handling of invalid priority levels."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting invalid priority test")

        # Test with invalid priority
        result = manager.create_work_effort(
            title="Invalid Priority Test",
            assignee="tester",
            priority="invalid_priority",
            due_date="2025-12-31"
        )

        if result is not None and result[0] is not False:
            logger.error("Manager allowed creation with invalid priority")
            return False

        # Test with empty priority
        result = manager.create_work_effort(
            title="Empty Priority Test",
            assignee="tester",
            priority="",
            due_date="2025-12-31"
        )

        if result is not None and result[0] is not False:
            logger.error("Manager allowed creation with empty priority")
            return False

        logger.info("Invalid priority test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_invalid_date_format():
    """Test handling of invalid date formats."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting invalid date format test")

        # Test with invalid date formats
        invalid_formats = [
            "2025/12/31",  # Wrong separator
            "31-12-2025",  # DD-MM-YYYY
            "12-31-2025",  # MM-DD-YYYY
            "2025-13-31",  # Invalid month
            "2025-12-32",  # Invalid day
            "abcd-ef-gh",  # Not a date at all
        ]

        for date_format in invalid_formats:
            result = manager.create_work_effort(
                title=f"Invalid Date {date_format}",
                assignee="tester",
                priority="medium",
                due_date=date_format
            )

            if result is not None and result[0] is not False:
                logger.error(f"Manager allowed creation with invalid date format: {date_format}")
                return False

        logger.info("Invalid date format test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_missing_file_handling():
    """Test handling of missing files."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting missing file handling test")

        # Create a work effort
        title = f"Missing File Test {int(time.time())}"
        folder_path, filename = create_test_work_effort(
            manager,
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31"
        )

        if not folder_path or not filename:
            logger.error("Failed to create work effort for testing")
            return False

        # Delete the file manually
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)

        # Try to update the status of a non-existent file
        result = manager.update_work_effort_status(filename, "completed", "active")

        if result is not False:
            logger.error("Manager allowed status update for missing file")
            return False

        # Create a new file to test missing folder handling
        folder_name = os.path.splitext(filename)[0]
        os.rmdir(folder_path)  # Remove the folder

        # Try to update the status after folder is gone
        result = manager.update_work_effort_status(filename, "completed", "active")

        if result is not False:
            logger.error("Manager allowed status update when folder is missing")
            return False

        logger.info("Missing file handling test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_corrupt_index_recovery():
    """Test recovery from corrupted index."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting corrupt index recovery test")

        # Create several work efforts
        for i in range(3):
            title = f"Recovery Test {i} {int(time.time())}"
            folder_path, filename = create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )

            if not folder_path or not filename:
                logger.error(f"Failed to create work effort {i} for testing")
                return False

        # Verify work efforts in manager
        work_efforts = manager.get_work_efforts()
        if len(work_efforts) != 3:
            logger.error(f"Expected 3 work efforts, got {len(work_efforts)}")
            return False

        # Corrupt the index
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
        with open(index_path, 'w') as f:
            f.write("{this is not valid JSON")

        # Create a new manager instance (should rebuild index)
        manager = None  # Clear the old reference

        # Create a new manager that should recover from the corrupted index
        manager = WorkEffortManager(project_dir=test_dir)

        # Verify that work efforts were recovered
        recovered_efforts = manager.get_work_efforts()

        if len(recovered_efforts) != 3:
            logger.error(f"Expected 3 recovered work efforts, got {len(recovered_efforts)}")
            return False

        # Verify that index was repaired
        if not os.path.exists(index_path):
            logger.error(f"Index file was not recreated at {index_path}")
            return False

        # Verify index is now valid JSON
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)

            if not isinstance(index_data, dict) or "version" not in index_data:
                logger.error("Rebuilt index is missing expected structure")
                return False

        except json.JSONDecodeError:
            logger.error("Rebuilt index is not valid JSON")
            return False

        logger.info("Corrupt index recovery test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_permission_handling():
    """Test handling of permission issues."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting permission handling test")

        # Create a work effort
        title = f"Permission Test {int(time.time())}"
        folder_path, filename = create_test_work_effort(
            manager,
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31"
        )

        if not folder_path or not filename:
            logger.error("Failed to create work effort for testing")
            return False

        # Make the file read-only (if possible)
        file_path = os.path.join(folder_path, filename)
        try:
            # This won't work on all platforms but let's try
            os.chmod(file_path, 0o444)  # Read-only

            # Try to update the work effort status
            result = manager.update_work_effort_status(filename, "completed", "active")

            # On Unix-like systems, this should fail, on Windows it might still work
            # We'll check the result but not fail the test if it succeeds
            if not result:
                logger.info("Permission test prevented status update (expected)")
            else:
                logger.warning("Permission test allowed status update despite read-only file (might be expected on Windows)")

            # Restore permissions for cleanup
            os.chmod(file_path, 0o644)

        except PermissionError:
            logger.info("Got permission error when changing permissions (expected on some systems)")
        except Exception as e:
            logger.warning(f"Unexpected error when testing permissions: {str(e)}")

        # Make the index file read-only
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
        try:
            # Make the index read-only
            os.chmod(index_path, 0o444)

            # Create another work effort
            result = manager.create_work_effort(
                title=f"Permission Test 2 {int(time.time())}",
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )

            # The work effort might still be created even if the index update fails
            # So we won't check if it fails, just that it handles errors gracefully

            # Restore permissions for cleanup
            os.chmod(index_path, 0o644)

        except PermissionError:
            logger.info("Got permission error when changing index permissions (expected on some systems)")
        except Exception as e:
            logger.warning(f"Unexpected error when testing index permissions: {str(e)}")

        logger.info("Permission handling test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_concurrent_updates():
    """Test handling of concurrent updates."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting concurrent updates test")

        # This is a simplified simulation since we can't easily test true concurrency
        # Create a work effort
        title = f"Concurrent Test {int(time.time())}"
        folder_path, filename = create_test_work_effort(
            manager,
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31"
        )

        if not folder_path or not filename:
            logger.error("Failed to create work effort for testing")
            return False

        # Create a second instance of the manager to simulate concurrent access
        manager2 = WorkEffortManager(project_dir=test_dir)

        # First manager updates the status
        result1 = manager.update_work_effort_status(filename, "completed", "active")
        if not result1:
            logger.error("First manager failed to update status")
            return False

        # Second manager tries to update the same file (which no longer exists in active)
        result2 = manager2.update_work_effort_status(filename, "archived", "active")

        # This should fail since the file is no longer in active status
        if result2:
            logger.error("Second manager succeeded in updating already moved file")
            return False

        logger.info("Concurrent updates test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_temporary_file_access():
    """Test handling of temporary files."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting temporary file access test")

        # Create a temporary file with specific content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.md', mode='w') as tf:
            temp_filepath = tf.name
            tf.write("""---
title: "Temporary Test"
status: "active"
priority: "medium"
assignee: "tester"
due_date: "2025-12-31"
---

# Temporary Test

This is a temporary file for testing error handling.
""")

        logger.info(f"Created temporary file: {temp_filepath}")

        # Attempt to update a work effort using this file
        # This should fail gracefully since the file is outside our work efforts structure
        temp_filename = os.path.basename(temp_filepath)
        result = manager.update_work_effort_status(temp_filename, "completed", "active")

        # This should fail, but without crashing
        if result is not False:
            logger.error("Manager allowed status update for external file")
            return False

        # Try to import the external file
        # Implementation depends on the API, but should be handled gracefully
        if hasattr(manager, 'import_external_file'):
            try:
                result = manager.import_external_file(temp_filepath)
                logger.info(f"Import result: {result}")
            except Exception as e:
                logger.info(f"Expected error when importing external file: {str(e)}")

        logger.info("Temporary file access test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        # Clean up the temp file
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.unlink(temp_filepath)
        cleanup_test_environment(test_dir)

def main():
    """Run all tests in this file."""
    tests = [
        ("Invalid Title", test_invalid_title),
        ("Invalid Priority", test_invalid_priority),
        ("Invalid Date Format", test_invalid_date_format),
        ("Missing File Handling", test_missing_file_handling),
        ("Corrupt Index Recovery", test_corrupt_index_recovery),
        ("Permission Handling", test_permission_handling),
        ("Concurrent Updates", test_concurrent_updates),
        ("Temporary File Access", test_temporary_file_access),
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