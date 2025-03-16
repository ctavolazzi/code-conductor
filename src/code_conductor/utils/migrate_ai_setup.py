#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-Setup Migration Script

This script helps users migrate from the old .AI-Setup directory naming convention
to the new _AI-Setup convention. It performs the following tasks:

1. Finds all .AI-Setup directories in the project
2. Renames them to _AI-Setup
3. Updates references in files to use the new naming convention
4. Provides a detailed report of changes made

Usage:
    python migrate_ai_setup.py [--dry-run] [--force] [--verbose]

Options:
    --dry-run       Don't actually make changes, just show what would be done
    --force         Don't ask for confirmation before making changes
    --verbose       Show detailed information about each change
"""

import os
import sys
import re
import shutil
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migrate_ai_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
OLD_DIR_NAME = ".AI-Setup"
NEW_DIR_NAME = "_AI-Setup"
EXCLUDED_DIRS = ['.git', 'node_modules', 'venv', '.env', '__pycache__']
FILE_PATTERNS = ['*.py', '*.md', '*.json', '*.sh', '*.txt']
EXCLUDED_FILES = ['migrate_ai_setup.py', 'CHANGELOG.md', 'devlog.md', '*.log']

class AiSetupMigrator:
    """
    Handles the migration from .AI-Setup to _AI-Setup directory naming convention.
    """

    def __init__(self, root_dir=None, dry_run=False, force=False, verbose=False):
        """
        Initialize the migrator.

        Args:
            root_dir: Root directory to search for .AI-Setup directories
            dry_run: If True, don't actually make changes
            force: If True, don't ask for confirmation
            verbose: If True, show detailed information
        """
        self.root_dir = os.path.abspath(root_dir or os.getcwd())
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        self.found_dirs = []
        self.renamed_dirs = []
        self.updated_files = []
        self.errors = []

    def find_ai_setup_dirs(self):
        """
        Find all .AI-Setup directories in the project.

        Returns:
            List of paths to .AI-Setup directories
        """
        logger.info(f"Searching for {OLD_DIR_NAME} directories in {self.root_dir}")

        found_dirs = []

        for root, dirs, _ in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            if OLD_DIR_NAME in dirs:
                found_dir = os.path.join(root, OLD_DIR_NAME)
                found_dirs.append(found_dir)
                logger.debug(f"Found {OLD_DIR_NAME} directory: {found_dir}")

        self.found_dirs = found_dirs
        logger.info(f"Found {len(found_dirs)} {OLD_DIR_NAME} directories")
        return found_dirs

    def rename_directories(self):
        """
        Rename .AI-Setup directories to _AI-Setup.

        Returns:
            List of renamed directories
        """
        if not self.found_dirs:
            logger.info(f"No {OLD_DIR_NAME} directories found to rename")
            return []

        renamed_dirs = []

        for old_dir in self.found_dirs:
            new_dir = os.path.join(os.path.dirname(old_dir), NEW_DIR_NAME)

            if os.path.exists(new_dir):
                logger.warning(f"{NEW_DIR_NAME} already exists at {new_dir}, skipping rename")
                self.errors.append(f"Could not rename {old_dir} because {new_dir} already exists")
                continue

            try:
                if not self.dry_run:
                    shutil.move(old_dir, new_dir)
                    renamed_dirs.append((old_dir, new_dir))
                    logger.info(f"Renamed {old_dir} to {new_dir}")
                else:
                    logger.info(f"Would rename {old_dir} to {new_dir}")
                    renamed_dirs.append((old_dir, new_dir))
            except Exception as e:
                logger.error(f"Error renaming {old_dir} to {new_dir}: {str(e)}")
                self.errors.append(f"Error renaming {old_dir}: {str(e)}")

        self.renamed_dirs = renamed_dirs
        return renamed_dirs

    def _is_excluded_file(self, file_path):
        """
        Check if a file should be excluded from processing.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be excluded, False otherwise
        """
        file_name = os.path.basename(file_path)

        # Check for exact filename matches
        if file_name in ['migrate_ai_setup.py', 'CHANGELOG.md', 'devlog.md']:
            return True

        # Check for file extensions
        if file_name.endswith('.log'):
            return True

        return False

    def find_files_with_references(self):
        """
        Find files containing references to .AI-Setup.

        Returns:
            List of files with references
        """
        logger.info(f"Searching for files with references to {OLD_DIR_NAME}")

        files_with_refs = []

        for root, _, files in os.walk(self.root_dir):
            # Skip excluded directories
            if any(excl in root for excl in EXCLUDED_DIRS):
                continue

            for file in files:
                # Check file extension matches patterns
                if not any(file.endswith(pat[1:]) for pat in FILE_PATTERNS):
                    continue

                file_path = os.path.join(root, file)

                # Skip excluded files
                if self._is_excluded_file(file_path):
                    logger.debug(f"Skipping excluded file: {file_path}")
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if OLD_DIR_NAME in content:
                        files_with_refs.append(file_path)
                        if self.verbose:
                            logger.debug(f"Found reference in {file_path}")
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {str(e)}")

        logger.info(f"Found {len(files_with_refs)} files with references to {OLD_DIR_NAME}")
        return files_with_refs

    def update_file_references(self, files):
        """
        Update references to .AI-Setup in files.

        Args:
            files: List of files to update

        Returns:
            List of updated files
        """
        if not files:
            logger.info(f"No files found with references to {OLD_DIR_NAME}")
            return []

        updated_files = []

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace references
                new_content = content.replace(OLD_DIR_NAME, NEW_DIR_NAME)

                if new_content != content:
                    if not self.dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_files.append(file_path)
                        logger.info(f"Updated references in {file_path}")
                    else:
                        logger.info(f"Would update references in {file_path}")
                        updated_files.append(file_path)
            except Exception as e:
                logger.error(f"Error updating references in {file_path}: {str(e)}")
                self.errors.append(f"Error updating {file_path}: {str(e)}")

        self.updated_files = updated_files
        return updated_files

    def run(self):
        """
        Run the migration process.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting migration from .AI-Setup to _AI-Setup")

        try:
            # Step 1: Find .AI-Setup directories
            self.find_ai_setup_dirs()

            if not self.found_dirs:
                logger.info("No .AI-Setup directories found. Migration complete.")
                return True

            # Step 2: Ask for confirmation
            if not self.force and not self.dry_run:
                print("\nFound the following .AI-Setup directories:")
                for d in self.found_dirs:
                    print(f"  {d}")

                confirmation = input("\nDo you want to rename these directories and update references? (y/N): ")
                if confirmation.lower() not in ('y', 'yes'):
                    logger.info("Migration cancelled by user")
                    return False

            # Step 3: Rename directories
            self.rename_directories()

            # Step 4: Find files with references
            files_with_refs = self.find_files_with_references()

            # Step 5: Update references in files
            self.update_file_references(files_with_refs)

            # Step 6: Print summary
            self.print_summary()

            return len(self.errors) == 0

        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            return False

    def print_summary(self):
        """
        Print a summary of the migration process.
        """
        print("\nMigration Summary:")
        print("==================")
        print(f"Mode: {'Dry run' if self.dry_run else 'Live run'}")
        print(f"Root directory: {self.root_dir}")
        print("")

        print(f"Directories found: {len(self.found_dirs)}")
        print(f"Directories renamed: {len(self.renamed_dirs)}")
        print(f"Files updated: {len(self.updated_files)}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.dry_run:
            print("\nThis was a dry run. No changes were made to the filesystem.")
            print("Run without --dry-run to apply changes.")

        print(f"\nNote: The following files were intentionally skipped:")
        print("  - migrate_ai_setup.py (this script)")
        print("  - CHANGELOG.md (historical record)")
        print("  - devlog.md (development log)")
        print("  - *.log files (log files)")


def parse_args():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Migrate from .AI-Setup to _AI-Setup naming convention')
    parser.add_argument('--dry-run', action='store_true', help="Don't actually make changes")
    parser.add_argument('--force', action='store_true', help="Don't ask for confirmation")
    parser.add_argument('--verbose', action='store_true', help="Show detailed information")
    parser.add_argument('--root-dir', type=str, help="Root directory to search", default=None)
    return parser.parse_args()


def main():
    """
    Main entry point.
    """
    args = parse_args()
    migrator = AiSetupMigrator(
        root_dir=args.root_dir,
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose
    )
    success = migrator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()