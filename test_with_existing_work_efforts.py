#!/usr/bin/env python3
"""
Test script to verify counter functionality with existing work efforts.

This script demonstrates that the counter correctly finds the highest work effort
number and continues from there, even when there are files with timestamps or other
number patterns that might confuse the counter.
"""

import os
import logging
from improved_counter import initialize_counter_from_existing_work_efforts, get_counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ExistingWorkEffortsTest")

def create_mixed_test_files(work_dir):
    """Create a mix of valid work effort files and files with misleading number patterns."""
    # Create some additional files with timestamp-like numbers
    active_dir = os.path.join(work_dir, "active")

    # Create files that should NOT affect the counter
    with open(os.path.join(active_dir, "task_with_9999_in_middle.md"), 'w') as f:
        f.write("# Task with number in middle\nThis should be ignored by counter.")

    with open(os.path.join(active_dir, "log_20250317_134500.md"), 'w') as f:
        f.write("# Log with timestamp\nThis should be ignored by counter.")

    # Create a file with a large timestamp-like number that would break the old counter
    with open(os.path.join(active_dir, "event_1678912345_large_timestamp.md"), 'w') as f:
        f.write("# Event with large timestamp\nThis would break the old counter.")

    logger.info("Created mixed test files with misleading number patterns")

def test_with_existing_work_efforts(work_dir="./work_efforts"):
    """Test counter with existing work efforts."""
    logger.info(f"Testing with existing work efforts in: {work_dir}")

    # Create some additional mixed test files
    create_mixed_test_files(work_dir)

    # First, get information about current counter state
    counter_file = os.path.join(work_dir, "counter.json")
    if os.path.exists(counter_file):
        counter = get_counter(counter_file)
        logger.info(f"Current counter value before re-initialization: {counter.get_current_count()}")

    # Initialize counter from existing work efforts (should find our 0001 and 0002 work efforts)
    next_number = initialize_counter_from_existing_work_efforts(work_dir)
    logger.info(f"Next work effort number after initialization: {next_number}")

    # Verify counter correctly found the highest work effort number (should be 3 after our two work efforts)
    assert next_number == 3, f"Expected next number to be 3, got {next_number}"

    # Create a new work effort using the counter
    counter = get_counter(counter_file)
    new_number = counter.get_next_count()
    logger.info(f"New work effort number: {new_number}")

    # Verify new number is 3
    assert new_number == 3, f"Expected new number to be 3, got {new_number}"

    logger.info("Test passed: Counter correctly handled existing work efforts and ignored misleading numbers")
    return new_number

if __name__ == "__main__":
    logger.info("Starting test with existing work efforts")
    test_with_existing_work_efforts()
    logger.info("Test completed")