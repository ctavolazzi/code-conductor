#!/usr/bin/env python3
"""
Test Status Change Feature

This script tests the status change functionality in the WorkflowRunner.
"""

import os
import sys
from workflow_runner import WorkflowRunner, ACTIVE_DIR, COMPLETED_DIR, ARCHIVED_DIR

def main():
    """Demonstrate the work effort status change functionality."""
    print("Testing Work Effort Status Change Functionality\n")

    # Create a test work effort
    runner = WorkflowRunner(interactive=False)
    runner.feature_name = "Status Change Test"
    runner.feature_title = "Status Change Test"
    runner.feature_description = "Testing the status change functionality"
    runner.script_name = "status_change_test"
    runner.class_name = "StatusChangeTest"

    # Create the work effort document
    work_effort_filename = runner.create_work_effort()
    print(f"\nCreated work effort at: {runner.work_effort_path}")
    print(f"Current status: {runner.status}")

    # Test changing to completed status
    print("\nChanging status to 'completed'...")
    success = runner.update_work_effort_status("completed")
    if success:
        print(f"New work effort path: {runner.work_effort_path}")
        print(f"New status: {runner.status}")
        print(f"File exists in completed dir: {os.path.exists(runner.work_effort_path)}")
        print(f"File exists in active dir: {os.path.exists(os.path.join(ACTIVE_DIR, work_effort_filename))}")
    else:
        print("Failed to change status to 'completed'")

    # Test changing to archived status
    print("\nChanging status to 'archived'...")
    success = runner.update_work_effort_status("archived")
    if success:
        print(f"New work effort path: {runner.work_effort_path}")
        print(f"New status: {runner.status}")
        print(f"File exists in archived dir: {os.path.exists(runner.work_effort_path)}")
        print(f"File exists in completed dir: {os.path.exists(os.path.join(COMPLETED_DIR, work_effort_filename))}")
    else:
        print("Failed to change status to 'archived'")

    # Test changing back to active status
    print("\nChanging status back to 'active'...")
    success = runner.update_work_effort_status("active")
    if success:
        print(f"New work effort path: {runner.work_effort_path}")
        print(f"New status: {runner.status}")
        print(f"File exists in active dir: {os.path.exists(runner.work_effort_path)}")
        print(f"File exists in archived dir: {os.path.exists(os.path.join(ARCHIVED_DIR, work_effort_filename))}")
    else:
        print("Failed to change status to 'active'")

    print("\nStatus change functionality test completed.")

    # Clean up test files
    if os.path.exists(runner.work_effort_path):
        os.remove(runner.work_effort_path)
        print(f"Cleaned up test work effort file")

    return 0

if __name__ == "__main__":
    sys.exit(main())