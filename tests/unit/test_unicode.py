#!/usr/bin/env python3
"""
Script to test Unicode characters in work effort titles.
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the work effort creation function
from src.code_conductor.ai_work_effort_creator import create_work_effort

def main():
    """Test Unicode characters in title."""
    print("Testing Unicode characters in title...")

    result = create_work_effort(
        title="Unicode Test 📊 测试 Проверка",
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

        # Add a test file with Unicode content
        test_file_path = os.path.join(folder_path, "unicode_notes.txt")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("Unicode content: 📊 测试 Проверка\n")
            f.write("More symbols: 🚀 ⚡ 🔥 ✨ 🌟 💡 🎯\n")

        print(f"Added Unicode test file: {test_file_path}")
        print(f"Updated folder contents: {os.listdir(folder_path)}")
    else:
        print("❌ Failed to create work effort")

if __name__ == "__main__":
    main()