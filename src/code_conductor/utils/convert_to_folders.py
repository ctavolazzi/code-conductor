#!/usr/bin/env python3
"""
Script to convert existing work efforts to the new folder structure.

This script identifies work effort files that aren't in their own folder and
creates a folder for each one, moving the file inside.
"""

import os
import sys
import shutil
import argparse

def convert_work_efforts_to_folders(work_efforts_dir, dry_run=False):
    """
    Convert existing work effort files to the folder structure.

    Args:
        work_efforts_dir: Path to the work_efforts directory
        dry_run: If True, don't actually make changes, just report what would be done

    Returns:
        Tuple of (converted_count, skipped_count, error_count)
    """
    converted_count = 0
    skipped_count = 0
    error_count = 0

    # Statuses to process
    statuses = ["active", "completed", "archived"]

    for status in statuses:
        status_dir = os.path.join(work_efforts_dir, status)
        if not os.path.exists(status_dir) or not os.path.isdir(status_dir):
            print(f"Skipping {status} - directory not found")
            continue

        print(f"\nProcessing {status} work efforts:")

        # Get all files in the directory
        for item in os.listdir(status_dir):
            item_path = os.path.join(status_dir, item)

            # Skip directories and non-markdown files
            if os.path.isdir(item_path) or not item.endswith(".md"):
                continue

            try:
                # This is a work effort file that needs a folder
                filename_without_ext = os.path.splitext(item)[0]
                folder_path = os.path.join(status_dir, filename_without_ext)
                new_file_path = os.path.join(folder_path, item)

                print(f"  - {item} -> {filename_without_ext}/{item}")

                if not dry_run:
                    # Create folder and move file
                    os.makedirs(folder_path, exist_ok=True)
                    shutil.move(item_path, new_file_path)
                    print(f"    ✅ Converted successfully")
                else:
                    print(f"    ✅ Would convert (dry run)")

                converted_count += 1
            except Exception as e:
                print(f"    ❌ Error converting {item}: {str(e)}")
                error_count += 1

    return converted_count, skipped_count, error_count

def main():
    parser = argparse.ArgumentParser(description="Convert existing work efforts to folder structure")
    parser.add_argument("--dir", help="Path to the _AI-Setup/work_efforts directory")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes, just show what would be done")
    args = parser.parse_args()

    if args.dir:
        work_efforts_dir = args.dir
    else:
        # Try to find the work_efforts directory
        current_dir = os.getcwd()
        work_efforts_dir = os.path.join(current_dir, "_AI-Setup", "work_efforts")

        if not os.path.exists(work_efforts_dir):
            # Try one level up
            parent_dir = os.path.dirname(current_dir)
            work_efforts_dir = os.path.join(parent_dir, "_AI-Setup", "work_efforts")

            if not os.path.exists(work_efforts_dir):
                print("❌ Could not find work_efforts directory. Please specify with --dir.")
                return 1

    print(f"Converting work efforts in: {work_efforts_dir}")
    if args.dry_run:
        print("DRY RUN: No changes will be made")

    converted, skipped, errors = convert_work_efforts_to_folders(work_efforts_dir, args.dry_run)

    print(f"\nConversion complete:")
    print(f"  - {converted} work efforts converted to folder structure")
    print(f"  - {skipped} work efforts skipped (already in folders)")
    print(f"  - {errors} errors encountered")

    return 0

if __name__ == "__main__":
    sys.exit(main())