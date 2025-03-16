#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Restructuring

Implementation of a more structured project organizational system.
This script organizes the code conductor project into a logical directory structure,
grouping related functionality and improving maintainability.

Usage:
    python project_restructuring.py [options]

Options:
    --dry-run    Show what would be done without making changes
    --verbose    Show detailed information during execution
    --overwrite  Overwrite existing files and directories (default: skip existing)
    --help       Show this help message
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import re
import importlib
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger("project_restructuring")

# Define the new directory structure
NEW_STRUCTURE = {
    "src": {
        "code_conductor": {
            "core": {},  # Core functionality
            "cli": {},   # Command line interface
            "utils": {}, # Utility functions
            "workflow": {}, # Workflow runner and related
            "work_efforts": {}, # Work effort management
            "templates": {},  # Template files
            "providers": {},  # AI providers
        },
        "tests": {
            "unit": {},  # Unit tests
            "integration": {},  # Integration tests
            "functional": {},  # Functional tests
        },
    },
    "scripts": {},  # Utility scripts
    "docs": {
        "api": {},      # API documentation
        "usage": {},    # Usage guides
        "development": {},  # Development guides
    },
}

# Files to be moved to specific locations
MOVE_MAPPING = {
    # Core functionality
    "cli.py": "src/code_conductor/cli/cli.py",
    "workflow_runner.py": "src/code_conductor/workflow/workflow_runner.py",
    "create_work_node.py": "src/code_conductor/work_efforts/create_work_node.py",
    "consolidate_work_efforts.py": "src/code_conductor/work_efforts/consolidate_work_efforts.py",
    "retrieve_work_effort.py": "src/code_conductor/work_efforts/retrieve_work_effort.py",
    "update_status.py": "src/code_conductor/work_efforts/update_status.py",
    "run_workflow.py": "src/code_conductor/workflow/run_workflow.py",

    # Utilities
    "convert_to_folders.py": "src/code_conductor/utils/convert_to_folders.py",

    # Tests
    "test_workflow_runner.py": "src/tests/unit/test_workflow_runner.py",
    "test_work_node.py": "src/tests/unit/test_work_node.py",
    "test_version_print.py": "src/tests/unit/test_version_print.py",
    "test_version_comprehensive.py": "src/tests/unit/test_version_comprehensive.py",
    "test_setup_version.py": "src/tests/unit/test_setup_version.py",
    "test_status_change.py": "src/tests/functional/test_status_change.py",
    "test_api_integration_layer.py": "src/tests/integration/test_api_integration_layer.py",
    "test_document_management_system.py": "src/tests/integration/test_document_management_system.py",
    "test_new_feature.py": "src/tests/unit/test_new_feature.py",
    "test_feature.py": "src/tests/unit/test_feature.py",
    "test_test_feature.py": "src/tests/unit/test_test_feature.py",
    "test_unicode.py": "src/tests/unit/test_unicode.py",
    "test_single.py": "src/tests/unit/test_single.py",
    "test_edge_cases.py": "src/tests/unit/test_edge_cases.py",
    "test_folder_structure.py": "src/tests/functional/test_folder_structure.py",

    # Feature modules
    "api_integration_layer.py": "src/code_conductor/core/api_integration_layer.py",
    "document_management_system.py": "src/code_conductor/core/document_management_system.py",
    "new_feature.py": "src/code_conductor/core/new_feature.py",
    "simple_workflow.py": "src/code_conductor/workflow/simple_workflow.py",
    "user_authentication__login_system.py": "src/code_conductor/core/user_authentication.py",
    "advanced_search.py": "src/code_conductor/core/advanced_search.py",
    "search_functionality.py": "src/code_conductor/core/search_functionality.py",

    # Shell scripts
    "build_and_upload.sh": "scripts/build_and_upload.sh",
    "run_all_tests.sh": "scripts/run_all_tests.sh",
    "cleanup_large_files.sh": "scripts/cleanup_large_files.sh",
    "test_runner.sh": "scripts/test_runner.sh",
    "test_catalog.sh": "scripts/test_catalog.sh",
    "create_test_work_effort.sh": "scripts/create_test_work_effort.sh",
    "simple_setup_test.sh": "scripts/simple_setup_test.sh",
    "test_discovery.sh": "scripts/test_discovery.sh",
    "test_types.sh": "scripts/test_types.sh",
    "simple_help_test.sh": "scripts/simple_help_test.sh",
    "simple_version_test.sh": "scripts/simple_version_test.sh",
    "test_utils.sh": "scripts/test_utils.sh",
    "test_reporting.sh": "scripts/test_reporting.sh",
    "test_multi_manager.sh": "scripts/test_multi_manager.sh",
    "test_config_system.sh": "scripts/test_config_system.sh",
    "test_work_effort_manager.sh": "scripts/test_work_effort_manager.sh",
    "test_work_effort_commands.sh": "scripts/test_work_effort_commands.sh",

    # Documentation
    "CHANGELOG.md": "docs/CHANGELOG.md",
    "TESTING_FRAMEWORK_DOCUMENTATION.md": "docs/development/TESTING_FRAMEWORK_DOCUMENTATION.md",
    "TEST_README.md": "docs/development/TEST_README.md",
    "GITHUB_GUIDE.md": "docs/development/GITHUB_GUIDE.md",
    "work_node_README.md": "docs/usage/work_node_README.md",
    "CONTRIBUTING.md": "docs/development/CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md": "docs/CODE_OF_CONDUCT.md"
}

# Directories to be copied with all their contents
DIR_COPY_MAPPING = {
    "providers": "src/code_conductor/providers",
    "creators": "src/code_conductor/creators",
    "utils": "src/code_conductor/utils",
    "templates": "src/code_conductor/templates"
}

# Special handling for _AI-Setup directory with proper directory checks
AI_SETUP_MAPPING = {
    # These are files
    "_AI-Setup/AI-setup-instructions.md": "docs/usage/AI-setup-instructions.md",
    "_AI-Setup/AI-work-effort-system.md": "docs/usage/AI-work-effort-system.md",
    "_AI-Setup/AI-setup-validation-instructions.md": "docs/usage/AI-setup-validation-instructions.md",
    "_AI-Setup/INSTRUCTIONS.md": "docs/usage/AI-setup-INSTRUCTIONS.md",
    "_AI-Setup/config.json": "src/code_conductor/config.json",
}

# Directories in _AI-Setup to be copied
AI_SETUP_DIR_MAPPING = {
    "_AI-Setup/work_efforts": "src/code_conductor/work_efforts",
    "_AI-Setup/release_notes": "docs/release_notes"
}

# Directories to be potentially removed (only if empty after restructuring)
CLEANUP_DIRS = [
    "test_dir",
    "setup_test",
    "test_ai_setup",
    "new_test_dir",
    "test_script_copy",
    "config_system_test",
    "multi_manager_test",
    "test_both_methods",
    "ai_setup_only_test",
    "final_test",
    "__pycache__"
]

# Files to be kept at root level
ROOT_LEVEL_FILES = [
    "README.md",
    "setup.py",
    "MANIFEST.in",
    "LICENSE",
    ".gitignore",
    ".env",
    "__init__.py",
    "Cursor-Github_MCP.md", # This seems project-specific, keeping at root
    "DEVLOG.md"  # Main development log
]

# Define readme content at module level for test access
readme_content = {
    "src/code_conductor": "# Code Conductor Core Package\n\nThis directory contains the main code for the Code Conductor package.",
    "src/code_conductor/core": "# Core Functionality\n\nThis directory contains the core functionality modules of Code Conductor.",
    "src/code_conductor/cli": "# Command Line Interface\n\nThis directory contains the CLI functionality for Code Conductor.",
    "src/code_conductor/utils": "# Utilities\n\nThis directory contains utility functions and helpers used throughout Code Conductor.",
    "src/code_conductor/workflow": "# Workflow\n\nThis directory contains workflow-related modules and functionality.",
    "src/code_conductor/work_efforts": "# Work Efforts\n\nThis directory contains work effort management functionality.",
    "src/tests": "# Tests\n\nThis directory contains tests for the Code Conductor package.",
    "src/tests/unit": "# Unit Tests\n\nThis directory contains unit tests for individual components.",
    "src/tests/integration": "# Integration Tests\n\nThis directory contains tests that check integration between components.",
    "src/tests/functional": "# Functional Tests\n\nThis directory contains tests that verify functionality from a user perspective.",
    "scripts": "# Utility Scripts\n\nThis directory contains utility scripts for development, testing, and maintenance.",
    "docs/api": "# API Documentation\n\nThis directory contains documentation for the Code Conductor API.",
    "docs/usage": "# Usage Guides\n\nThis directory contains guides for using Code Conductor.",
    "docs/development": "# Development Documentation\n\nThis directory contains documentation for developers contributing to Code Conductor."
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Implementation of Project Restructuring")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--verbose", action="store_true", help="Show detailed information during execution")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files and directories (default: skip existing)")
    return parser.parse_args()


def create_directory_structure(base_dir, structure, dry_run=False, verbose=False):
    """Create the directory structure recursively."""
    for directory, substructure in structure.items():
        path = os.path.join(base_dir, directory)
        if verbose:
            logger.info(f"Creating directory: {path}")

        if not dry_run:
            os.makedirs(path, exist_ok=True)

            # Create __init__.py file for Python packages
            if directory.startswith("src") or \
               (os.path.basename(base_dir) == "src" and directory != "tests") or \
               (os.path.basename(os.path.dirname(base_dir)) == "src" and os.path.basename(base_dir) != "tests"):
                init_file = os.path.join(path, "__init__.py")
                if not os.path.exists(init_file):
                    if verbose:
                        logger.info(f"Creating __init__.py in: {path}")
                    with open(init_file, 'w') as f:
                        f.write("# Auto-generated by project_restructuring.py\n")

        if substructure:
            create_directory_structure(path, substructure, dry_run, verbose)


def move_files(file_mapping, dry_run=False, verbose=False, overwrite=False):
    """Move files according to the provided mapping."""
    for source, destination in file_mapping.items():
        if not os.path.exists(source):
            if verbose:
                logger.warning(f"Source file does not exist, skipping: {source}")
            continue

        dest_dir = os.path.dirname(destination)
        if not os.path.exists(dest_dir) and not dry_run:
            os.makedirs(dest_dir, exist_ok=True)

        # Skip if destination already exists and overwrite is False
        if os.path.exists(destination) and not overwrite:
            if verbose:
                logger.info(f"Destination file already exists, skipping: {destination}")
            continue

        if verbose:
            logger.info(f"Moving: {source} -> {destination}")

        if not dry_run:
            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)


def copy_directories(dir_mapping, dry_run=False, verbose=False, overwrite=False):
    """Copy directories according to the provided mapping."""
    for source, destination in dir_mapping.items():
        if not os.path.exists(source):
            if verbose:
                logger.warning(f"Source directory does not exist, skipping: {source}")
            continue

        # Skip if destination already exists and overwrite is False
        if os.path.exists(destination) and not overwrite:
            if verbose:
                logger.info(f"Destination directory already exists, skipping: {destination}")
            continue

        if verbose:
            logger.info(f"Copying directory: {source} -> {destination}")

        if not dry_run:
            if os.path.exists(destination) and overwrite:
                shutil.rmtree(destination)
            if not os.path.exists(destination):  # Only copy if destination doesn't exist
                shutil.copytree(source, destination)


def update_imports(files_moved, dry_run=False, verbose=False):
    """Update import statements in Python files."""
    # Get all Python files in the new structure
    python_files = []
    for root, _, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Original to new module mapping
    module_mapping = {}
    for old_path, new_path in files_moved.items():
        if old_path.endswith(".py") and new_path.endswith(".py"):
            old_module = os.path.splitext(old_path)[0].replace("/", ".")
            new_module = os.path.splitext(new_path)[0].replace("/", ".")
            module_mapping[old_module] = new_module

    for filepath in python_files:
        if verbose:
            logger.info(f"Checking imports in: {filepath}")

        with open(filepath, 'r') as file:
            content = file.read()

        # Replace import statements
        updated_content = content
        for old_module, new_module in module_mapping.items():
            # Various import patterns
            patterns = [
                rf"import\s+{re.escape(old_module)}(\s+as\s+[a-zA-Z_][a-zA-Z0-9_]*)?",
                rf"from\s+{re.escape(old_module)}\s+import\s+"
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    if verbose:
                        logger.info(f"  - Replacing: {old_module} with {new_module}")

                    # Replace the module name while keeping the rest of the import statement
                    updated_content = re.sub(
                        pattern,
                        lambda m: m.group(0).replace(old_module, new_module),
                        updated_content
                    )

        if updated_content != content and not dry_run:
            with open(filepath, 'w') as file:
                file.write(updated_content)
                if verbose:
                    logger.info(f"  - Updated imports in {filepath}")


def create_manifest_file(dry_run=False, verbose=False):
    """Create or update MANIFEST.in file to include necessary files."""
    lines = [
        "include LICENSE",
        "include README.md",
        "include CHANGELOG.md",
        "include src/code_conductor/config.json",
        "recursive-include src/code_conductor/templates *",
        "recursive-include docs *",
    ]

    if verbose:
        logger.info("Creating MANIFEST.in")

    if not dry_run:
        with open("MANIFEST.in", 'w') as f:
            f.write("\n".join(lines))


def update_setup_py(dry_run=False, verbose=False):
    """Update setup.py to reflect the new package structure."""
    if not os.path.exists("setup.py"):
        if verbose:
            logger.warning("setup.py not found, skipping update")
        return

    with open("setup.py", 'r') as f:
        content = f.read()

    # Update package references
    updated_content = re.sub(
        r"packages\s*=\s*find_packages\(.*?\)",
        "packages=find_packages(where='src')",
        content
    )

    # Add package_dir parameter if not present
    if "package_dir" not in updated_content:
        updated_content = re.sub(
            r"setup\(",
            "setup(\n    package_dir={'': 'src'},",
            updated_content
        )

    if verbose:
        logger.info("Updating setup.py")

    if not dry_run and updated_content != content:
        with open("setup.py", 'w') as f:
            f.write(updated_content)


def cleanup_empty_directories(dirs_to_check, dry_run=False, verbose=False):
    """Remove empty directories."""
    for directory in dirs_to_check:
        if not os.path.exists(directory):
            continue

        if not os.listdir(directory):
            if verbose:
                logger.info(f"Removing empty directory: {directory}")

            if not dry_run:
                os.rmdir(directory)
        else:
            if verbose:
                logger.info(f"Directory not empty, skipping: {directory}")


def create_readme_files(dry_run=False, verbose=False):
    """Create README.md files in key directories."""
    global readme_content

    for directory, content in readme_content.items():
        if not os.path.exists(directory) and not dry_run:
            os.makedirs(directory, exist_ok=True)

        readme_path = os.path.join(directory, "README.md")

        if verbose:
            logger.info(f"Creating README: {readme_path}")

        if not dry_run:
            with open(readme_path, 'w') as f:
                f.write(content)


def cleanup_files(moved_files, dry_run=False, verbose=False):
    """Remove original files that have been moved."""
    logger.info("Cleaning up original files...")

    # Don't remove _AI-Setup contents since we're copying, not moving
    files_to_remove = [f for f in moved_files.keys() if not f.startswith("_AI-Setup")]

    for file in files_to_remove:
        if os.path.exists(file):
            if verbose:
                logger.info(f"Removing file from original location: {file}")

            if not dry_run:
                os.remove(file)


def main():
    """Main function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Implementing Project Restructuring..." + (" (DRY RUN)" if args.dry_run else ""))
    if args.overwrite:
        logger.info("Overwrite mode: Existing files and directories will be overwritten")
    else:
        logger.info("Safe mode: Existing files and directories will be skipped")

    # Create the new directory structure
    logger.info("Creating directory structure...")
    create_directory_structure(".", NEW_STRUCTURE, args.dry_run, args.verbose)

    # Create README files for the directories
    logger.info("Creating README files...")
    create_readme_files(args.dry_run, args.verbose)

    # Move the files to their new locations
    logger.info("Moving files...")
    move_files(MOVE_MAPPING, args.dry_run, args.verbose, args.overwrite)

    # Copy full directories
    logger.info("Copying directories...")
    copy_directories(DIR_COPY_MAPPING, args.dry_run, args.verbose, args.overwrite)

    # Handle _AI-Setup directory - files only
    logger.info("Processing _AI-Setup files...")
    move_files(AI_SETUP_MAPPING, args.dry_run, args.verbose, args.overwrite)

    # Handle _AI-Setup directory - directories
    logger.info("Processing _AI-Setup directories...")
    copy_directories(AI_SETUP_DIR_MAPPING, args.dry_run, args.verbose, args.overwrite)

    # Update import statements
    logger.info("Updating import statements...")
    update_imports(MOVE_MAPPING, args.dry_run, args.verbose)

    # Update setup.py
    logger.info("Updating setup.py...")
    update_setup_py(args.dry_run, args.verbose)

    # Create or update MANIFEST.in
    logger.info("Creating MANIFEST.in...")
    create_manifest_file(args.dry_run, args.verbose)

    # Remove moved files from their original locations
    logger.info("Cleaning up moved files...")
    cleanup_files(MOVE_MAPPING, args.dry_run, args.verbose)

    # Clean up empty directories
    logger.info("Cleaning up empty directories...")
    cleanup_empty_directories(CLEANUP_DIRS, args.dry_run, args.verbose)

    logger.info("Project restructuring " +
                ("would be " if args.dry_run else "") +
                "completed successfully!")

    if args.dry_run:
        logger.info("This was a dry run. No files were actually modified.")
        logger.info("Run without --dry-run to actually make the changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
