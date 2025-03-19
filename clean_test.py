#!/usr/bin/env python3

import os
import sys
import time
import unittest
import tempfile
import shutil

from code_conductor.core.work_effort.manager import WorkEffortManager

def main():
    print("Testing directory cleanup...")
    manager = WorkEffortManager()

    # Create a new work effort
    print("Creating new work effort...")
    result = manager.create_work_effort(
        title="Directory Cleanup Test",
        assignee="tester",
        priority="medium",
        due_date="2025-05-01",
        use_sequential_numbering=True
    )

    if not result:
        print("Failed to create work effort")
        return

    print(f"Work effort created at: {result}")

    # Get the filename
    folder_name = os.path.basename(result)
    filename = f"{folder_name}.md"

    # Verify folder exists in active directory
    active_folder = os.path.join(manager.active_dir, folder_name)
    print(f"Active folder exists: {os.path.exists(active_folder)}")

    # Update the status
    print("Updating status...")
    update_result = manager.update_work_effort_status(filename, "completed", "active")
    print(f"Status update result: {update_result}")

    # Check if the active directory still exists
    print(f"Active folder still exists: {os.path.exists(active_folder)}")

    # Check if the file was moved to completed
    completed_folder = os.path.join(manager.completed_dir, folder_name)
    completed_file = os.path.join(completed_folder, filename)
    print(f"Completed file exists: {os.path.exists(completed_file)}")

    print("Test completed")

if __name__ == "__main__":
    main()