#!/usr/bin/env python3
"""
Test work effort status transitions.

This test verifies:
1. Transition from active to completed
2. Transition from active to archived
3. Transition from completed to active
4. Transition from completed to archived
5. Transition from archived to active
6. Transition from archived to completed
7. Folder structure maintenance during transitions
8. Index updates during transitions
9. Content updates during transitions
"""

import os
import sys
import time
import re
import logging
from test_utils import (
    create_test_environment,
    cleanup_test_environment,
    verify_file_exists,
    verify_dir_exists,
    verify_index_contains,
    verify_work_effort_content,
    create_test_work_effort,
    logger
)

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

    # Enable transition details logging
    logging.getLogger('work_effort_manager.transitions').setLevel(logging.DEBUG)

    logger.debug("Running test_03_status_transitions.py with enhanced logging")

def test_active_to_completed():
    """Test transition from active to completed."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting active to completed transition test")

        # Create a work effort
        title = f"Active to Completed Test {int(time.time())}"
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

        # Initial verification
        src_file_path = os.path.join(folder_path, filename)
        if not verify_file_exists(src_file_path):
            return False

        # Verify in active section of index
        index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
        if not verify_index_contains(index_path, filename, "active", {"title": title}):
            return False

        # Update status from active to completed
        result = manager.update_work_effort_status(filename, "completed", "active")
        if not result:
            logger.error("Failed to update work effort status from active to completed")
            return False

        # Verify file now exists in completed directory
        folder_name = os.path.splitext(filename)[0]
        completed_folder = os.path.join(manager.completed_dir, folder_name)
        completed_file = os.path.join(completed_folder, filename)

        if not verify_dir_exists(completed_folder):
            return False

        if not verify_file_exists(completed_file):
            return False

        # Verify original file/folder no longer exists in active directory
        if verify_file_exists(src_file_path):
            logger.error(f"Original file still exists: {src_file_path}")
            return False

        if verify_dir_exists(folder_path):
            logger.error(f"Original folder still exists: {folder_path}")
            return False

        # Verify index updated
        if not verify_index_contains(index_path, filename, "completed", {"title": title, "status": "completed"}):
            return False

        # Verify content updated
        if not verify_work_effort_content(completed_file, {"status": "completed"}):
            return False

        logger.info("Active to completed transition test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_all_transitions():
    """Test all possible status transitions."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting all transitions test")

        # Define all possible transitions
        transitions = [
            ("active", "completed"),
            ("active", "archived"),
            ("completed", "active"),
            ("completed", "archived"),
            ("archived", "active"),
            ("archived", "completed")
        ]

        for from_status, to_status in transitions:
            logger.info(f"Testing transition from {from_status} to {to_status}")

            # Create a work effort and move it to the from_status
            title = f"Transition Test {from_status} to {to_status} {int(time.time())}"

            # First create in active
            folder_path, filename = create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )

            if not folder_path or not filename:
                logger.error(f"Failed to create work effort for {from_status} to {to_status} test")
                return False

            # Move to from_status if it's not active
            if from_status != "active":
                result = manager.update_work_effort_status(filename, from_status, "active")
                if not result:
                    logger.error(f"Failed to move work effort to initial status {from_status}")
                    return False

            # Determine source path based on status
            from_dir = getattr(manager, f"{from_status}_dir")
            folder_name = os.path.splitext(filename)[0]
            from_folder = os.path.join(from_dir, folder_name)
            from_file = os.path.join(from_folder, filename)

            # Verify file exists at expected source location
            if not verify_file_exists(from_file):
                return False

            # Perform the transition
            result = manager.update_work_effort_status(filename, to_status, from_status)
            if not result:
                logger.error(f"Failed to update work effort status from {from_status} to {to_status}")
                return False

            # Verify file moved to destination
            to_dir = getattr(manager, f"{to_status}_dir")
            to_folder = os.path.join(to_dir, folder_name)
            to_file = os.path.join(to_folder, filename)

            if not verify_dir_exists(to_folder):
                return False

            if not verify_file_exists(to_file):
                return False

            # Verify source no longer exists
            if verify_file_exists(from_file):
                logger.error(f"Source file still exists: {from_file}")
                return False

            if verify_dir_exists(from_folder):
                logger.error(f"Source folder still exists: {from_folder}")
                return False

            # Verify index updated
            index_path = os.path.join(test_dir, ".code_conductor", "work_index.json")
            if not verify_index_contains(index_path, filename, to_status, {"title": title, "status": to_status}):
                return False

            # Verify content updated
            if not verify_work_effort_content(to_file, {"status": to_status}):
                return False

        logger.info("All transitions test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_update_timestamp():
    """Test that the last_updated timestamp is updated during transitions."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting update timestamp test")

        # Create a work effort
        title = f"Update Timestamp Test {int(time.time())}"
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

        # Get the original creation timestamp
        src_file_path = os.path.join(folder_path, filename)
        with open(src_file_path, 'r') as f:
            content = f.read()

        created_match = re.search(r'created: "([^"]+)"', content)
        if not created_match:
            logger.error("Could not find creation timestamp in file")
            return False

        original_created = created_match.group(1)

        updated_match = re.search(r'last_updated: "([^"]+)"', content)
        if not updated_match:
            logger.error("Could not find last_updated timestamp in file")
            return False

        original_updated = updated_match.group(1)

        # Sleep to ensure timestamp will be different
        time.sleep(2)

        # Update status
        result = manager.update_work_effort_status(filename, "completed", "active")
        if not result:
            logger.error("Failed to update work effort status")
            return False

        # Check new file in completed directory
        folder_name = os.path.splitext(filename)[0]
        completed_folder = os.path.join(manager.completed_dir, folder_name)
        completed_file = os.path.join(completed_folder, filename)

        with open(completed_file, 'r') as f:
            new_content = f.read()

        # Verify created timestamp is unchanged
        new_created_match = re.search(r'created: "([^"]+)"', new_content)
        if not new_created_match:
            logger.error("Could not find creation timestamp in updated file")
            return False

        new_created = new_created_match.group(1)

        if new_created != original_created:
            logger.error(f"Creation timestamp changed from {original_created} to {new_created}")
            return False

        # Verify last_updated timestamp has changed
        new_updated_match = re.search(r'last_updated: "([^"]+)"', new_content)
        if not new_updated_match:
            logger.error("Could not find last_updated timestamp in updated file")
            return False

        new_updated = new_updated_match.group(1)

        if new_updated == original_updated:
            logger.error(f"Last updated timestamp did not change: {original_updated}")
            return False

        logger.info("Update timestamp test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def main():
    """Run all tests in this file."""
    tests = [
        ("Active to Completed", test_active_to_completed),
        ("All Transitions", test_all_transitions),
        ("Update Timestamp", test_update_timestamp),
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