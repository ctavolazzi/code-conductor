#!/usr/bin/env python3
"""
Test runner for work effort manager tests.

This script runs all the work effort tests in sequence and reports the results.
"""

import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ANSI color codes for colorful output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_subheader(message):
    """Print a formatted subheader message."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'-' * 80}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'-' * 80}{Colors.ENDC}\n")

def print_test_result(test_name, success, duration):
    """Print a formatted test result."""
    if success:
        status = f"{Colors.GREEN}PASSED{Colors.ENDC}"
    else:
        status = f"{Colors.RED}FAILED{Colors.ENDC}"

    print(f"{Colors.BOLD}{test_name}{Colors.ENDC}: {status} (took {duration:.2f}s)")

def run_test(test_file):
    """Run a test file and return the result."""
    start_time = time.time()
    test_name = os.path.basename(test_file)

    print_subheader(f"Running {test_name}")

    # Check if file exists
    if not os.path.exists(test_file):
        logger.error(f"Test file not found: {test_file}")
        return test_name, False, 0

    try:
        # Run the test script
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
        success = result.returncode == 0

        # Print output
        if result.stdout:
            for line in result.stdout.splitlines():
                if "PASSED" in line:
                    print(f"{Colors.GREEN}{line}{Colors.ENDC}")
                elif "FAILED" in line:
                    print(f"{Colors.RED}{line}{Colors.ENDC}")
                else:
                    print(line)

        if result.stderr and result.stderr.strip():
            print(f"\n{Colors.RED}STDERR:{Colors.ENDC}")
            print(result.stderr)

        duration = time.time() - start_time
        return test_name, success, duration
    except Exception as e:
        logger.error(f"Error running test {test_file}: {str(e)}")
        duration = time.time() - start_time
        return test_name, False, duration

def main():
    """Run all work effort tests in sequence."""
    print_header("WORK EFFORT MANAGER TEST SUITE")

    # List of test files to run in sequence
    test_files = [
        "test_01_creation_basic.py",
        "test_02_creation_parameters.py",
        "test_03_status_transitions.py",
        "test_04_filtering_and_querying.py",
        "test_05_error_handling.py",
        # Add more test files here as needed
    ]

    results = []
    start_time = time.time()

    for test_file in test_files:
        test_name, success, duration = run_test(test_file)
        results.append((test_name, success, duration))

    total_duration = time.time() - start_time

    # Print summary
    print_header("TEST RESULTS SUMMARY")

    for test_name, success, duration in results:
        print_test_result(test_name, success, duration)

    # Calculate stats
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    failed_tests = total_tests - passed_tests

    # Print final summary
    print("\n" + "=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.ENDC}")

    if failed_tests > 0:
        print(f"Failed: {Colors.RED}{failed_tests}{Colors.ENDC}")
    else:
        print(f"Failed: {failed_tests}")

    print(f"Total Duration: {total_duration:.2f}s")
    print("=" * 80)

    # Return 0 if all tests passed, otherwise return number of failed tests
    return failed_tests

if __name__ == "__main__":
    sys.exit(main())