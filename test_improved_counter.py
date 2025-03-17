#!/usr/bin/env python3
"""
Test script for the improved work effort counter system.

This script demonstrates how the improved counter handles various scenarios,
particularly with the new regex pattern that prevents misidentifying timestamps as work effort numbers.
"""

import os
import shutil
import tempfile
import logging
from improved_counter import (
    WorkEffortCounter,
    initialize_counter_from_existing_work_efforts
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CounterTest")

def create_test_work_efforts(base_dir):
    """Create test work effort directories and files with various naming patterns."""
    # Create directory structure
    active_dir = os.path.join(base_dir, "active")
    completed_dir = os.path.join(base_dir, "completed")
    archived_dir = os.path.join(base_dir, "archived")

    os.makedirs(active_dir, exist_ok=True)
    os.makedirs(completed_dir, exist_ok=True)
    os.makedirs(archived_dir, exist_ok=True)

    # Create work effort files and directories with various patterns
    # Valid work efforts with 4-digit prefixes
    os.makedirs(os.path.join(active_dir, "0001_first_work_effort"), exist_ok=True)
    os.makedirs(os.path.join(active_dir, "0002_second_work_effort"), exist_ok=True)
    os.makedirs(os.path.join(completed_dir, "0003_third_work_effort"), exist_ok=True)

    # Create markdown files (also valid work efforts)
    with open(os.path.join(active_dir, "0004_fourth_work_effort.md"), 'w') as f:
        f.write("# Work Effort 4\nThis is a test work effort file.")

    with open(os.path.join(completed_dir, "0005_fifth_work_effort.md"), 'w') as f:
        f.write("# Work Effort 5\nThis is a test work effort file.")

    # Files with timestamps or other number patterns that should NOT be identified as work efforts
    os.makedirs(os.path.join(active_dir, "task_1678912345_timestamp"), exist_ok=True)
    os.makedirs(os.path.join(completed_dir, "experiment_20230517_date"), exist_ok=True)

    with open(os.path.join(active_dir, "task_with_1234_in_middle.md"), 'w') as f:
        f.write("# Task with number in middle\nThis shouldn't be counted.")

    with open(os.path.join(archived_dir, "old_task_2345.md"), 'w') as f:
        f.write("# Old task with non-prefixed number\nThis shouldn't be counted.")

def test_counter_with_various_patterns():
    """Test the counter with various naming patterns."""
    # Create temporary test directory
    test_dir = tempfile.mkdtemp()
    try:
        logger.info(f"Created test directory: {test_dir}")

        # Create test work efforts with various patterns
        create_test_work_efforts(test_dir)

        # Initialize counter from existing work efforts
        next_number = initialize_counter_from_existing_work_efforts(test_dir)

        # Verify the counter found the correct highest number (should be 5)
        logger.info(f"Next work effort number: {next_number}")
        assert next_number == 6, f"Expected next number to be 6, got {next_number}"

        # Test creating new work efforts
        counter = WorkEffortCounter(os.path.join(test_dir, "counter.json"))
        new_number = counter.get_next_count()
        logger.info(f"New work effort number from counter: {new_number}")
        assert new_number == 6, f"Expected new number to be 6, got {new_number}"

        logger.info("All tests passed successfully!")

    finally:
        # Clean up test directory
        logger.info(f"Cleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    logger.info("Starting counter test script")
    test_counter_with_various_patterns()
    logger.info("Test completed")