#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the create_work_effort function
from cli import create_work_effort

def main():
    # Set up test parameters
    title = "API Testing Framework"
    assignee = "self"
    priority = "high"
    due_date = datetime.now().strftime("%Y-%m-%d")
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/work-effort-template.md")

    # Set target directory to public-apis
    public_apis_dir = "/Users/ctavolazzi/Code/public-apis"
    target_dir = os.path.join(public_apis_dir, ".AI-Setup/work_efforts/active")

    print(f"Creating work effort in: {target_dir}")

    # Create a work effort
    file_path = create_work_effort(
        title=title,
        assignee=assignee,
        priority=priority,
        due_date=due_date,
        template_path=template_path,
        target_dir=target_dir
    )

    print(f"Created work effort at: {file_path}")

    # Check if a folder was created
    if file_path:
        folder_path = os.path.dirname(file_path)
        print(f"Folder path: {folder_path}")
        print(f"Is folder: {os.path.isdir(folder_path)}")
        print(f"Folder contents: {os.listdir(folder_path)}")

        # Try adding a test file to the folder
        test_file_path = os.path.join(folder_path, "test_file.txt")
        with open(test_file_path, "w") as f:
            f.write("This is a test file to demonstrate folder structure.")

        print(f"Added test file: {test_file_path}")
        print(f"Updated folder contents: {os.listdir(folder_path)}")

if __name__ == "__main__":
    main()