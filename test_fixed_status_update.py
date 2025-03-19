#!/usr/bin/env python3

import os
import sys
import unittest
import tempfile
import shutil

from code_conductor.core.work_effort.manager import WorkEffortManager

def main():
    print("Testing fixed status update functionality...")
    manager = WorkEffortManager()

    # Create a new work effort to test with
    print("Creating a new test work effort...")
    result = manager.create_work_effort(
        title="Status Update Test",
        assignee="tester",
        priority="medium",
        due_date="2025-04-30",
        use_sequential_numbering=True
    )

    if not result:
        print("Failed to create work effort for testing")
        return

    print(f"Work effort created at: {result}")

    # Extract the filename from the path
    folder_name = os.path.basename(result)
    filename = f"{folder_name}.md"

    print(f"Work effort filename: {filename}")

    # Verify the file exists
    file_path = os.path.join(result, filename)
    if not os.path.exists(file_path):
        print(f"Error: Created file not found at {file_path}")
        return

    print("File exists, proceeding with status update...")

    # Now test updating the status
    update_result = manager.update_work_effort_status(filename, "completed", "active")
    print(f"Status update result: {update_result}")

    # Check if the file was moved to completed directory
    completed_path = os.path.join(manager.completed_dir, folder_name, filename)
    if os.path.exists(completed_path):
        print(f"✅ File successfully moved to: {completed_path}")
    else:
        print(f"❌ File not found at expected destination: {completed_path}")

    # Verify the central index was updated
    central_index = manager.index_file_path
    if os.path.exists(central_index):
        print(f"Central index exists at {central_index}, checking for updated metadata...")

        # Check if our work effort exists in the completed section of the manager's in-memory cache
        if filename in manager.work_efforts.get("completed", {}):
            metadata = manager.work_efforts["completed"][filename]["metadata"]
            if metadata["status"] == "completed":
                print(f"✅ In-memory index shows correct status: {metadata['status']}")
            else:
                print(f"❌ In-memory index shows incorrect status: {metadata['status']}")
        else:
            print("❌ Work effort not found in the completed section of the manager's cache")
    else:
        print(f"❌ Central index not found at {central_index}")

    print("Test completed")

if __name__ == "__main__":
    main()