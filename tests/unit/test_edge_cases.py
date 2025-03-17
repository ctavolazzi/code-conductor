#!/usr/bin/env python3
"""
Script to test edge cases for folder-based work efforts.
"""

import os
import sys
import shutil
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the work effort creation function
from src.code_conductor.ai_work_effort_creator import create_work_effort

def test_special_characters():
    """Test work effort creation with special characters in title."""
    print("\n=== Testing Special Characters in Title ===")
    result = create_work_effort(
        title="Special Ch@r$ & Symbols!?",
        assignee="self",
        priority="medium",
        due_date=datetime.now().strftime("%Y-%m-%d")
    )
    if result:
        print(f"✅ Created work effort at: {result}")
        print(f"Folder exists: {os.path.isdir(os.path.dirname(result))}")
        print(f"Folder contents: {os.listdir(os.path.dirname(result))}")
    else:
        print("❌ Failed to create work effort")

def test_very_long_title():
    """Test work effort creation with a very long title."""
    print("\n=== Testing Very Long Title ===")
    long_title = "This is an extremely long title that exceeds the typical length " + \
                "of a title and tests the system's ability to handle such cases " + \
                "without breaking or causing any issues in the file system"
    result = create_work_effort(
        title=long_title,
        assignee="self",
        priority="high",
        due_date=datetime.now().strftime("%Y-%m-%d")
    )
    if result:
        print(f"✅ Created work effort at: {result}")
        print(f"Folder exists: {os.path.isdir(os.path.dirname(result))}")
        print(f"Folder contents: {os.listdir(os.path.dirname(result))}")
    else:
        print("❌ Failed to create work effort")

def test_unicode_characters():
    """Test work effort creation with Unicode characters in title."""
    print("\n=== Testing Unicode Characters in Title ===")
    result = create_work_effort(
        title="Unicode Test 📊 测试 Проверка",
        assignee="self",
        priority="medium",
        due_date=datetime.now().strftime("%Y-%m-%d")
    )
    if result:
        print(f"✅ Created work effort at: {result}")
        print(f"Folder exists: {os.path.isdir(os.path.dirname(result))}")
        print(f"Folder contents: {os.listdir(os.path.dirname(result))}")
    else:
        print("❌ Failed to create work effort")

def test_adding_files():
    """Test adding files to a work effort folder."""
    print("\n=== Testing Adding Files to Work Effort ===")
    result = create_work_effort(
        title="File Test",
        assignee="self",
        priority="medium",
        due_date=datetime.now().strftime("%Y-%m-%d")
    )
    if not result:
        print("❌ Failed to create work effort")
        return

    folder_path = os.path.dirname(result)

    # Add a text file
    text_file_path = os.path.join(folder_path, "notes.txt")
    with open(text_file_path, "w") as f:
        f.write("These are some notes for the work effort.")

    # Add a markdown file
    md_file_path = os.path.join(folder_path, "research.md")
    with open(md_file_path, "w") as f:
        f.write("# Research\n\nFindings related to this work effort.")

    print(f"✅ Created work effort at: {result}")
    print(f"Added files to folder: {os.listdir(folder_path)}")

def main():
    """Run all tests."""
    # Make sure we're using the package directory
    os.environ['USE_CURRENT_DIR'] = 'False'

    print("Running edge case tests for folder-based work efforts...")

    test_special_characters()
    test_very_long_title()
    test_unicode_characters()
    test_adding_files()

    print("\nAll tests completed.")

if __name__ == "__main__":
    main()