#!/usr/bin/env python3
"""
Script to fix work effort file structure by identifying work effort files
that don't have corresponding folders and moving them into new folders.
"""

import os
import re
import shutil

# Base directory for work efforts
WORK_EFFORTS_DIR = "_AI-Setup/work_efforts/active"

def has_timestamp_prefix(filename):
    """Check if filename has a timestamp prefix like 202503161730"""
    return bool(re.match(r'^\d{12}_.*\.md$', filename))

def main():
    print("Analyzing work effort structure...")
    files_to_fix = []
    existing_folders = set()

    # Get list of all files and folders in the active directory
    all_items = os.listdir(WORK_EFFORTS_DIR)

    # Identify folders
    for item in all_items:
        item_path = os.path.join(WORK_EFFORTS_DIR, item)
        if os.path.isdir(item_path):
            existing_folders.add(item)

    # Identify md files with timestamp prefixes
    for item in all_items:
        if item.endswith('.md') and has_timestamp_prefix(item):
            folder_name = item[:-3]  # Remove .md extension

            # Check if file already has a folder
            if folder_name in existing_folders:
                # File has a corresponding folder but is not in it
                files_to_fix.append(item)
            else:
                # File doesn't have a corresponding folder
                files_to_fix.append(item)

    print(f"Found {len(files_to_fix)} work effort files to fix")

    # Move files to their folders
    for file in files_to_fix:
        folder_name = file[:-3]  # Remove .md extension
        folder_path = os.path.join(WORK_EFFORTS_DIR, folder_name)

        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            print(f"Creating folder: {folder_path}")
            os.makedirs(folder_path)

        # Move file to folder
        src_path = os.path.join(WORK_EFFORTS_DIR, file)
        dst_path = os.path.join(folder_path, file)
        print(f"Moving {file} to {folder_name}/")
        shutil.move(src_path, dst_path)

    print("\nWork effort structure fixing complete!")
    print(f"Total files fixed: {len(files_to_fix)}")

if __name__ == "__main__":
    main()