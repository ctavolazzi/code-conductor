#!/usr/bin/env python3
"""
Test script for verifying the counter functionality with large numbers.

This script tests the counter's ability to handle numbers larger than 9999
and the formatting features for variable-length numbers.
"""

import os
import logging
import shutil
import tempfile
from improved_counter import (
    WorkEffortCounter,
    get_counter,
    initialize_counter_from_existing_work_efforts,
    format_work_effort_filename
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LargeNumberTest")

def create_test_files_with_large_numbers(test_dir):
    """Create test files with some large numbers to verify handling."""
    # Create directory structure
    active_dir = os.path.join(test_dir, "active")
    os.makedirs(active_dir, exist_ok=True)

    # Create work efforts with various number formats
    work_efforts = [
        # Regular 4-digit numbers
        ("0001_first_work_effort.md", 1),
        ("0042_meaning_of_life.md", 42),
        ("9999_last_four_digit.md", 9999),
        # Numbers exceeding 4 digits
        ("10000_five_digits.md", 10000),
        ("12345_another_five_digit.md", 12345),
        ("100000_six_digits.md", 100000),
    ]

    # Create the files
    for filename, number in work_efforts:
        filepath = os.path.join(active_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"# Test Work Effort {number}\nThis is a test file.")
        logger.info(f"Created test file: {filename}")

    return work_efforts

def test_large_number_handling():
    """Test counter handling of numbers beyond 9999."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    try:
        logger.info(f"Created test directory: {test_dir}")

        # Create test files with various numbers
        work_efforts = create_test_files_with_large_numbers(test_dir)

        # Initialize counter from existing work efforts
        counter_file = os.path.join(test_dir, "counter.json")
        next_number = initialize_counter_from_existing_work_efforts(test_dir, counter_file)

        # Check if it found the highest number correctly (should be 100000 + 1)
        logger.info(f"Next work effort number: {next_number}")
        expected_next = 100001
        assert next_number == expected_next, f"Expected next number to be {expected_next}, got {next_number}"

        # Test getting the next count
        counter = get_counter(counter_file)
        new_number = counter.get_next_count()
        logger.info(f"New work effort number: {new_number}")
        assert new_number == expected_next, f"Expected new number to be {expected_next}, got {new_number}"

        # Test formatting of work effort numbers
        # 1. Test standard 4-digit formatting
        regular_number = 42
        formatted_regular = counter.format_work_effort_number(regular_number)
        logger.info(f"Formatted regular number ({regular_number}): {formatted_regular}")
        assert formatted_regular == "0042", f"Expected '0042', got '{formatted_regular}'"

        # 2. Test 5-digit formatting
        five_digit = 12345
        formatted_five = counter.format_work_effort_number(five_digit)
        logger.info(f"Formatted five-digit number ({five_digit}): {formatted_five}")
        assert formatted_five == "12345", f"Expected '12345', got '{formatted_five}'"

        # 3. Test 6-digit formatting
        six_digit = 123456
        formatted_six = counter.format_work_effort_number(six_digit)
        logger.info(f"Formatted six-digit number ({six_digit}): {formatted_six}")
        assert formatted_six == "123456", f"Expected '123456', got '{formatted_six}'"

        # 4. Test with date prefix
        with_date = counter.format_work_effort_number(regular_number, use_date_prefix=True)
        logger.info(f"Formatted with date prefix ({regular_number}): {with_date}")
        assert len(with_date) >= 12, f"Date prefix format incorrect: {with_date}"

        # Test format_work_effort_filename function
        filename = format_work_effort_filename("Test Title", five_digit)
        logger.info(f"Formatted filename: {filename}")
        assert filename == "12345_test_title", f"Expected '12345_test_title', got '{filename}'"

        # Test with date prefix
        date_filename = format_work_effort_filename("Date Test", regular_number, use_date_prefix=True)
        logger.info(f"Formatted filename with date: {date_filename}")

        logger.info("All large number handling tests passed!")

    finally:
        # Clean up
        logger.info(f"Cleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)

def test_counter_overflow_handling():
    """Test how the counter handles exceeding 9999."""
    # Create a test counter
    counter_file = tempfile.mktemp(suffix=".json")
    try:
        # Create counter and set it to 9998
        counter = get_counter(counter_file)
        counter.initialize(9998)

        # Get counts crossing the 9999 threshold
        count1 = counter.get_next_count()  # Should be 9998
        count2 = counter.get_next_count()  # Should be 9999
        count3 = counter.get_next_count()  # Should be 10000

        logger.info(f"Counts around threshold: {count1}, {count2}, {count3}")
        assert count1 == 9998, f"Expected 9998, got {count1}"
        assert count2 == 9999, f"Expected 9999, got {count2}"
        assert count3 == 10000, f"Expected 10000, got {count3}"

        # Check the formatting
        formatted1 = counter.format_work_effort_number(count1)
        formatted2 = counter.format_work_effort_number(count2)
        formatted3 = counter.format_work_effort_number(count3)

        logger.info(f"Formatted counts: {formatted1}, {formatted2}, {formatted3}")
        assert formatted1 == "9998", f"Expected '9998', got '{formatted1}'"
        assert formatted2 == "9999", f"Expected '9999', got '{formatted2}'"
        assert formatted3 == "10000", f"Expected '10000', got '{formatted3}'"

        logger.info("Counter successfully handled the 9999 to 10000 transition")
    finally:
        # Clean up
        if os.path.exists(counter_file):
            os.remove(counter_file)

if __name__ == "__main__":
    logger.info("Starting large number counter tests")
    test_large_number_handling()
    test_counter_overflow_handling()
    logger.info("All tests completed successfully")