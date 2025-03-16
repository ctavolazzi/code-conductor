#!/usr/bin/env python3
"""
Script to test a single edge case for folder-based work efforts.
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the work effort creation function
from work_efforts.scripts.ai_work_effort_creator import create_work_effort

def main():
    """Run a single test."""
    print("Testing special characters in title...")

    result = create_work_effort(
        title="Special Ch@r$ & Symbols!?",
        assignee="self",
        priority="medium",
        due_date=datetime.now().strftime("%Y-%m-%d")
    )

    if result:
        print(f"✅ Created work effort at: {result}")
        folder_path = os.path.dirname(result)
        print(f"Folder path: {folder_path}")
        print(f"Folder exists: {os.path.isdir(folder_path)}")
        print(f"Folder contents: {os.listdir(folder_path)}")

        # Add a test file to the folder
        test_file_path = os.path.join(folder_path, "test_file.txt")
        with open(test_file_path, "w") as f:
            f.write("This is a test file in the work effort folder.")

        print(f"Added test file: {test_file_path}")
        print(f"Updated folder contents: {os.listdir(folder_path)}")
    else:
        print("❌ Failed to create work effort")

if __name__ == "__main__":
    main()