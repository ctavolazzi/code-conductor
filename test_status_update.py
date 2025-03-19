#!/usr/bin/env python3

import os
import sys
import json
import shutil
from code_conductor.core.work_effort.manager import WorkEffortManager

def main():
    print("Starting direct file test...")

    # Full paths
    work_effort_dir = os.path.join(os.getcwd(), "work_efforts/active/0007_system_verification_test")
    source_file = os.path.join(work_effort_dir, "0007_system_verification_test.md")
    dest_dir = os.path.join(os.getcwd(), "work_efforts/completed/0007_system_verification_test")
    dest_file = os.path.join(dest_dir, "0007_system_verification_test.md")

    print(f"Source file exists: {os.path.exists(source_file)}")

    # 1. First create the destination directory
    print("Creating destination directory...")
    os.makedirs(dest_dir, exist_ok=True)

    # 2. Update the content to mark as completed
    print("Updating content status...")
    with open(source_file, 'r') as f:
        content = f.read()

    # Replace status in content
    updated_content = content.replace('status: "active"', 'status: "completed"')

    # 3. Write to destination
    print("Writing to destination file...")
    with open(dest_file, 'w') as f:
        f.write(updated_content)

    # 4. Remove source file and directory if empty
    print("Removing source file...")
    os.remove(source_file)

    # 5. Remove empty directory if needed
    if not os.listdir(work_effort_dir):
        print("Removing empty source directory...")
        os.rmdir(work_effort_dir)

    print("File moved successfully")

    # 6. Update the central index manually
    central_index_path = ".code_conductor/work_index.json"
    if os.path.exists(central_index_path):
        print("Updating central index...")
        with open(central_index_path, 'r') as f:
            index_data = json.load(f)

        # Check if our work effort exists in active
        work_efforts = index_data.get("work_efforts", {})
        active = work_efforts.get("active", {})
        filename = "0007_system_verification_test.md"

        if filename in active:
            # Move to completed
            print("Moving entry in index from active to completed...")
            work_effort = active.pop(filename)

            # Update the metadata
            work_effort["path"] = dest_file
            work_effort["folder_path"] = dest_dir
            work_effort["metadata"]["status"] = "completed"

            # Add to completed
            if "completed" not in work_efforts:
                work_efforts["completed"] = {}

            work_efforts["completed"][filename] = work_effort

            # Write back to the index
            with open(central_index_path, 'w') as f:
                json.dump(index_data, f, indent=2)

            print("Central index updated successfully")
        else:
            print(f"Work effort {filename} not found in active section")
    else:
        print("Central index not found")

    # 7. Verify file was moved
    print(f"Destination file exists: {os.path.exists(dest_file)}")

if __name__ == "__main__":
    main()