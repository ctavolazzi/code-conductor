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

            if not self.dry_run:
                try:
                    shutil.move(old_dir, new_dir)
                    renamed_dirs.append((old_dir, new_dir))
                    logger.info(f"Renamed {old_dir} to {new_dir}")
                except Exception as e:
                    logger.error(f"Error renaming {old_dir} to {new_dir}: {str(e)}")
                    self.errors.append(f"Error renaming {old_dir}: {str(e)}")
            else:
                logger.info(f"Would rename {old_dir} to {new_dir}")
                renamed_dirs.append((old_dir, new_dir))

        self.renamed_dirs = renamed_dirs
        return renamed_dirs

    def find_files_with_references(self):
        """
        Find files that contain references to .AI-Setup.

        Returns:
            List of files with references
        """
        logger.info(f"Searching for files with references to {OLD_DIR_NAME}")

        files_with_refs = []

        for pattern in FILE_PATTERNS:
            for file_path in Path(self.root_dir).glob(f"**/{pattern}"):
                # Skip excluded directories
                if any(excl in str(file_path) for excl in EXCLUDED_DIRS):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if OLD_DIR_NAME in content:
                            files_with_refs.append(str(file_path))
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
                logger.error(f"Error updating {file_path}: {str(e)}")
                self.errors.append(f"Error updating {file_path}: {str(e)}")

        self.updated_files = updated_files
        return updated_files

    def run(self):
        """
        Run the migration process.

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting migration from {OLD_DIR_NAME} to {NEW_DIR_NAME}")
        logger.info(f"Root directory: {self.root_dir}")
        logger.info(f"Dry run: {self.dry_run}")

        # Find .AI-Setup directories
        self.find_ai_setup_dirs()

        if not self.found_dirs:
            logger.info(f"No {OLD_DIR_NAME} directories found. Migration not needed.")
            return True

        # Find files with references
        files_with_refs = self.find_files_with_references()

        # Confirm before proceeding
        if not self.force and not self.dry_run:
            print(f"\nFound {len(self.found_dirs)} {OLD_DIR_NAME} directories to rename:")
            for d in self.found_dirs:
                print(f"  - {d}")

            print(f"\nFound {len(files_with_refs)} files with references to update:")
            for f in files_with_refs[:10]:  # Show first 10
                print(f"  - {f}")

            if len(files_with_refs) > 10:
                print(f"  - ... and {len(files_with_refs) - 10} more")

            confirm = input("\nProceed with migration? [y/N] ")
            if confirm.lower() != 'y':
                logger.info("Migration cancelled by user")
                return False

        # Rename directories
        self.rename_directories()

        # Update file references
        self.update_file_references(files_with_refs)

        # Print summary
        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print a summary of the migration."""
        print("\n" + "=" * 80)
        print(f"Migration Summary ({OLD_DIR_NAME} to {NEW_DIR_NAME})")
        print("=" * 80)

        print(f"\nDirectories found: {len(self.found_dirs)}")
        print(f"Directories renamed: {len(self.renamed_dirs)}")
        print(f"Files updated: {len(self.updated_files)}")
        print(f"Errors encountered: {len(self.errors)}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.dry_run:
            print("\nThis was a dry run. No actual changes were made.")
            print("Run without --dry-run to perform the migration.")

        print("\n" + "=" * 80)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Migrate from .AI-Setup to _AI-Setup')
    parser.add_argument('--root-dir', dest='root_dir', default=None,
                        help='Root directory to search (default: current directory)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="Don't actually make changes, just show what would be done")
    parser.add_argument('--force', dest='force', action='store_true',
                        help="Don't ask for confirmation before making changes")
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help="Show detailed information about each change")
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()

    migrator = AiSetupMigrator(
        root_dir=args.root_dir,
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose
    )

    success = migrator.run()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())