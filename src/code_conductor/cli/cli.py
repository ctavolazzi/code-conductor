#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code Conductor: AI Development Environment Setup Tool

This script sets up a directory with AI assistance tools and
a work effort tracking system.
"""

import os
import sys
import shutil
import argparse
import asyncio
import json
from datetime import datetime
import logging
import re

# Import version from package
try:
    from code_conductor import __version__
except ImportError:
    # Fallback version if imports fail
    __version__ = "0.4.6"

# Use imported version
VERSION = __version__

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CodeConductor')

# Import core components
from code_conductor.core.work_effort.manager import WorkEffortManager
from code_conductor.events import EventEmitter, Event

# Function to create or update configuration file
def create_or_update_config(base_dir=None, config_data=None):
    """
    Create or update the configuration file in the _AI-Setup directory.

    Args:
        base_dir: The base directory where _AI-Setup exists or will be created
        config_data: Dictionary of configuration data to write (will be merged with existing)

    Returns:
        Tuple of (path to config file, config data dictionary)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Define the _AI-Setup directory and config file path
    ai_setup_dir = os.path.join(base_dir, "_AI-Setup")
    config_file = os.path.join(ai_setup_dir, "config.json")

    # Ensure _AI-Setup directory exists
    if not os.path.exists(ai_setup_dir):
        os.makedirs(ai_setup_dir)
        logger.info(f"Created _AI-Setup directory at: {ai_setup_dir}")

    # Default configuration
    default_config = {
        "version": VERSION,
        "project_root": base_dir,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "default_work_manager": os.path.relpath(base_dir, base_dir),  # Default is the current directory (relative to project root)
        "work_managers": [
            {
                "name": os.path.basename(base_dir) or "main",
                "path": os.path.relpath(base_dir, base_dir),  # Relative to project root
                "work_efforts_dir": os.path.join("_AI-Setup", "work_efforts"),
                "use_manager": True,
                "manager_script": os.path.join("_AI-Setup", "work_efforts", "scripts", "work_effort_manager.py"),
                "runner_script": os.path.join("_AI-Setup", "work_efforts", "scripts", "run_work_effort_manager.py"),
                "auto_start": True
            }
        ],
        "default_settings": {
            "assignee": "AI Assistant",
            "priority": "medium",
            "due_date": "+7d"  # 7 days from now
        }
    }

    # Read existing config if it exists
    existing_config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
                logger.info(f"Read existing config from: {config_file}")
        except json.JSONDecodeError:
            logger.warning(f"Config file exists but is not valid JSON: {config_file}")
        except Exception as e:
            logger.warning(f"Error reading config file: {str(e)}")

    # Merge configurations (existing and defaults, updated with new data)
    # Start with defaults
    merged_config = default_config.copy()

    # Update with existing config (preserving user settings)
    def deep_update(original, update):
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                deep_update(original[key], value)
            else:
                original[key] = value

    if existing_config:
        deep_update(merged_config, existing_config)

    # Now update with any new config_data provided
    if config_data:
        merged_config["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deep_update(merged_config, config_data)

    # Write the updated config
    try:
        with open(config_file, 'w') as f:
            json.dump(merged_config, f, indent=2, sort_keys=False)
            logger.info(f"Wrote config to: {config_file}")
    except Exception as e:
        logger.error(f"Error writing config file: {str(e)}")
        return None, None

    return config_file, merged_config

# Function to find the nearest config.json
def find_nearest_config(start_dir=None):
    """
    Find the nearest _AI-Setup/config.json by walking up the directory tree

    Args:
        start_dir: Directory to start searching from (default: current directory)

    Returns:
        (config_file_path, config_data) or (None, None) if not found
    """
    if start_dir is None:
        start_dir = os.getcwd()

    # Convert to absolute path
    start_dir = os.path.abspath(start_dir)
    original_start = start_dir

    # First, try to find a .code-conductor project manifest file by walking up the directory tree
    current_dir = start_dir
    while current_dir:
        manifest_file = os.path.join(current_dir, ".code-conductor")
        if os.path.exists(manifest_file) and os.path.isfile(manifest_file):
            try:
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                    logger.info(f"Found project manifest file at: {manifest_file}")

                    # If the manifest has a setup_path, use it to find the config.json
                    if "setup_path" in manifest_data and os.path.exists(manifest_data["setup_path"]):
                        config_file = os.path.join(manifest_data["setup_path"], "config.json")
                        if os.path.exists(config_file):
                            try:
                                with open(config_file, 'r') as f:
                                    config_data = json.load(f)
                                    logger.info(f"Found config file via manifest at: {config_file}")
                                    return config_file, config_data
                            except Exception as e:
                                logger.warning(f"Error reading config file referenced in manifest: {str(e)}")
            except Exception as e:
                logger.warning(f"Error reading manifest file: {str(e)}")

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # We've reached the root
            break
        current_dir = parent_dir

    # If no manifest file found or it didn't lead to a valid config, fall back to the original behavior
    # Walk up the directory tree looking for _AI-Setup/config.json
    while start_dir:
        config_file = os.path.join(start_dir, "_AI-Setup", "config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    logger.info(f"Found config file at: {config_file}")
                    return config_file, config_data
            except json.JSONDecodeError:
                logger.warning(f"Found config file but it's not valid JSON: {config_file}")
            except Exception as e:
                logger.warning(f"Error reading config file {config_file}: {str(e)}")

        # Move up one directory
        parent_dir = os.path.dirname(start_dir)
        if parent_dir == start_dir:  # We've reached the root
            break
        start_dir = parent_dir

    logger.info(f"No config file found in or above: {original_start}")
    return None, None

# Function to add a new work effort manager
def add_work_manager(target_dir=None, manager_name=None):
    """
    Add a new work effort manager to the project configuration.

    Args:
        target_dir: Directory where the work effort manager will be installed
        manager_name: Name of the work manager (defaults to directory name)

    Returns:
        Tuple of (success boolean, message string)
    """
    if target_dir is None:
        target_dir = os.getcwd()

    # Make sure target_dir exists
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            logger.info(f"Created target directory: {target_dir}")
        except Exception as e:
            return False, f"Could not create target directory: {str(e)}"

    # Find the project root config
    config_file, config_data = find_nearest_config()
    if not config_file:
        return False, "No project configuration found. Run 'code-conductor setup' first in your project root."

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(config_file))

    # Calculate relative path from project root to target directory
    try:
        rel_path = os.path.relpath(target_dir, project_root)
    except ValueError:
        # Target is on a different drive or outside the project
        return False, "Target directory must be within the project."

    # Use directory name if manager_name not provided
    if not manager_name:
        manager_name = os.path.basename(target_dir)

    # Check if a manager with this name or path already exists
    for manager in config_data.get("work_managers", []):
        if manager.get("name") == manager_name:
            return False, f"Work manager with name '{manager_name}' already exists."
        if manager.get("path") == rel_path:
            return False, f"Work manager already exists at '{rel_path}'."

    # Create the work_efforts structure in the target directory
    work_efforts_dir = os.path.join(target_dir, "work_efforts")
    if not os.path.exists(work_efforts_dir):
        os.makedirs(work_efforts_dir)

    # Create subdirectories
    for subdir in ["active", "completed", "archived", "templates", "scripts"]:
        subdir_path = os.path.join(work_efforts_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

    # Copy necessary scripts
    setup_work_efforts_structure(target_dir, create_dirs=True, in_ai_setup=False)

    # Define the new work manager
    new_manager = {
        "name": manager_name,
        "path": rel_path,
        "work_efforts_dir": "work_efforts",
        "use_manager": True,
        "manager_script": os.path.join("work_efforts", "scripts", "work_effort_manager.py"),
        "runner_script": os.path.join("work_efforts", "scripts", "run_work_effort_manager.py"),
        "auto_start": True
    }

    # Add to configuration
    if "work_managers" not in config_data:
        config_data["work_managers"] = []

    config_data["work_managers"].append(new_manager)

    # Update the config file
    create_or_update_config(project_root, config_data)

    return True, f"Work manager '{manager_name}' added at '{rel_path}'."

# Function to find work effort manager directory
def find_work_effort_manager(manager_name=None):
    """
    Find a work effort manager directory based on name or current location.

    Args:
        manager_name: Name of the work manager to find, or None to use default

    Returns:
        (work_efforts_dir, manager_info) or (None, None) if not found
    """
    # Find the project config
    config_file, config_data = find_nearest_config()
    if not config_file or not config_data:
        logger.warning("No project configuration found.")
        return None, None

    # Get the project root directory
    project_root = config_data.get("project_root")
    if not project_root:
        project_root = os.path.dirname(os.path.dirname(config_file))

    # If no manager name specified, use the default or try to find the most appropriate
    if not manager_name:
        # Check for default manager
        default_manager_path = config_data.get("default_work_manager")
        if default_manager_path:
            for manager in config_data.get("work_managers", []):
                if manager.get("path") == default_manager_path:
                    manager_path = os.path.join(project_root, manager.get("path", ""))
                    work_efforts_dir = os.path.join(manager_path, manager.get("work_efforts_dir", "work_efforts"))
                    return work_efforts_dir, manager

        # Try to find a manager for the current directory
        current_dir = os.getcwd()
        try:
            rel_path = os.path.relpath(current_dir, project_root)

            # Look for an exact match first
            for manager in config_data.get("work_managers", []):
                if manager.get("path") == rel_path:
                    manager_path = os.path.join(project_root, manager.get("path", ""))
                    work_efforts_dir = os.path.join(manager_path, manager.get("work_efforts_dir", "work_efforts"))
                    return work_efforts_dir, manager

            # If no exact match, look for the closest parent directory with a manager
            while rel_path and rel_path != '.':
                for manager in config_data.get("work_managers", []):
                    if manager.get("path") == rel_path:
                        manager_path = os.path.join(project_root, manager.get("path", ""))
                        work_efforts_dir = os.path.join(manager_path, manager.get("work_efforts_dir", "work_efforts"))
                        return work_efforts_dir, manager
                rel_path = os.path.dirname(rel_path)

            # If still not found, use the first manager (usually the main one)
            if config_data.get("work_managers"):
                manager = config_data["work_managers"][0]
                manager_path = os.path.join(project_root, manager.get("path", ""))
                work_efforts_dir = os.path.join(manager_path, manager.get("work_efforts_dir", "work_efforts"))
                return work_efforts_dir, manager

        except ValueError:
            # Current directory is not within the project
            logger.warning("Current directory is not within the project.")
    else:
        # Find manager by name
        for manager in config_data.get("work_managers", []):
            if manager.get("name") == manager_name:
                manager_path = os.path.join(project_root, manager.get("path", ""))
                work_efforts_dir = os.path.join(manager_path, manager.get("work_efforts_dir", "work_efforts"))
                return work_efforts_dir, manager

    return None, None

# Function to find the work_efforts directory based on configuration
def find_work_efforts_directory(manager_name=None, verbose=False):
    """
    Locate the work_efforts directory for a specific manager or the most appropriate one.

    Args:
        manager_name: Name of the work manager to use, or None to use default/closest
        verbose: Whether to print verbose output about the search process

    Returns:
        Tuple of (work_efforts_dir, manager_info) or (None, None) if not found
    """
    # Try to find the work manager directory
    work_efforts_dir, manager_info = find_work_effort_manager(manager_name)

    if work_efforts_dir and os.path.exists(work_efforts_dir):
        if verbose:
            print(f"Found work efforts directory in manager: {work_efforts_dir}")
        return work_efforts_dir, manager_info

    # Fallback: try to find _AI-Setup/work_efforts in the current directory
    current_dir = os.getcwd()
    ai_setup_dir = os.path.join(current_dir, "_AI-Setup")

    if verbose:
        print(f"Looking for work efforts in current directory: {current_dir}")

    if os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir):
        ai_work_efforts = os.path.join(ai_setup_dir, "work_efforts")
        if os.path.exists(ai_work_efforts) and os.path.isdir(ai_work_efforts):
            if verbose:
                print(f"Found work efforts directory in _AI-Setup: {ai_work_efforts}")
            return ai_work_efforts, {"path": ".", "work_efforts_dir": os.path.join("_AI-Setup", "work_efforts")}
        elif verbose:
            print(f"_AI-Setup exists but work_efforts directory not found at: {ai_work_efforts}")
    elif verbose:
        print(f"_AI-Setup directory not found at: {ai_setup_dir}")

    # Not found
    if verbose:
        print("No work efforts directory found.")
    return None, None

# Re-import the necessary AI setup modules
try:
    from code_conductor.utils.directory_scanner import select_directories, is_ai_setup_installed, create_ai_setup, install_ai_setup
    from code_conductor.utils.thought_process import generate_content_with_ollama, get_available_ollama_models
except ImportError:
    print("Warning: Required modules not found. Some functionality will be limited.")

    # Fallback directory scanner functions if import fails
    def select_directories(base_dir=None):
        """Fallback directory selector if import fails"""
        if base_dir is None:
            base_dir = os.getcwd()

        print(f"\nScanning for directories in: {base_dir}")
        # Get directories and ensure they are unique
        all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]
        dirs = sorted(set(all_dirs))

        if len(dirs) != len(all_dirs):
            print(f"Note: Removed {len(all_dirs) - len(dirs)} duplicate directory entries")

        if not dirs:
            print("No directories found.")
            return []

        print("\nAvailable directories:")
        for i, d in enumerate(dirs):
            print(f"{i+1}. {d}")

        selections = input("\nEnter directory numbers separated by space (e.g., '1 3 4') or 'all': ")

        if selections.lower() == 'all':
            return [os.path.join(base_dir, d) for d in dirs]

        try:
            selected_indexes = [int(i)-1 for i in selections.split()]
            return [os.path.join(base_dir, dirs[i]) for i in selected_indexes if 0 <= i < len(dirs)]
        except:
            print("Invalid selection. Please provide valid numbers.")
            return []

    def is_ai_setup_installed(directory):
        return os.path.exists(os.path.join(directory, "_AI-Setup"))

    def create_ai_setup(root_dir=None):
        """Create the _AI-setup folder structure with all necessary files."""
        if root_dir is None:
            root_dir = os.getcwd()

        # Define the AI setup folder
        setup_folder = os.path.join(root_dir, "_AI-Setup")

        # Create _AI-Setup folder
        if not os.path.exists(setup_folder):
            os.makedirs(setup_folder)
            print(f"✅ Created AI-Setup in: {root_dir}")
        else:
            print(f"ℹ️ AI-Setup folder already exists at: {setup_folder}")

        # Create all other files, but only if they don't already exist
        # 1. Create INSTRUCTIONS.md if it doesn't exist
        instructions_file = os.path.join(setup_folder, "INSTRUCTIONS.md")
        if not os.path.exists(instructions_file):
            with open(instructions_file, "w") as f:
                f.write("""# AI-Setup Instructions

This directory contains setup files for AI-assisted development.

## Usage

This setup enables your AI assistants to better understand your project structure
and provide more contextual help and recommendations.

### Commands

The AI-Setup package provides two main commands:

1. `code-conductor` - Main command for setting up AI assistance and basic work efforts
   - `code-conductor setup` - Set up AI assistance in the current directory
   - `code-conductor new-work-effort` - Create a new work effort
   - `code-conductor list` - List all work efforts

2. `cc-work-e` - Enhanced work effort creator with AI content generation capabilities
   - `cc-work-e -i` - Create a work effort interactively
   - `cc-work-e --use-ai --description "Your description"` - Use AI to generate content
   - `cc-work-e --help` - Show help information

No action is required from you - the AI tools will automatically utilize these files.
""")

        # 2. Create AI-setup-validation-instructions.md if it doesn't exist
        validation_file = os.path.join(setup_folder, "AI-setup-validation-instructions.md")
        if not os.path.exists(validation_file):
            with open(validation_file, "w") as f:
                f.write("""# AI-Setup Validation Instructions

This file contains instructions for validating the presence and operation of _AI-Setup configured
environments. It serves as a stable identifier that AI tools can recognize to confirm that a directory
contains AI-friendly configurations.

## For AI Assistants

If your AI assistant can read this file, it should:

1. Recognize that _AI-Setup is properly configured
2. Look for structure-specific information in the accompanying files
3. Use this structure to provide more contextually-relevant assistance

## For Developers

You don't need to modify this file. Its presence signals to AI tools that this directory has
been properly configured with the AI-Setup toolkit.
""")

        # Set up the work_efforts directory within _AI-Setup
        work_efforts_dir, template_path, active_dir, _, _ = setup_work_efforts_structure(root_dir, in_ai_setup=True)
        create_template_if_missing(template_path)

        return setup_folder

    def install_ai_setup(target_dirs):
        """Install AI-Setup in target directories."""
        print("\n📦 Starting AI-Setup installation in multiple directories")

        if not target_dirs or len(target_dirs) == 0:
            print("❌ No directories selected for installation")
            return

        print(f"🔍 Selected directories: {len(target_dirs)}")

        # Create a temporary _AI-Setup in the current directory
        temp_dir = os.getcwd()
        print(f"ℹ️ Creating temporary AI-Setup in: {temp_dir}")
        setup_folder = create_ai_setup(temp_dir)

        # Process each target directory
        success_count = 0
        skipped_count = 0
        failed_count = 0

        print("\n🔄 Processing target directories:")

        # Copy to selected directories
        for directory in target_dirs:
            print(f"\n📂 Processing: {directory}")

            # Skip if directory doesn't exist
            if not os.path.exists(directory) or not os.path.isdir(directory):
                print(f"❌ Directory not found: {directory}")
                failed_count += 1
                continue

            # Skip if already installed
            if is_ai_setup_installed(directory):
                print(f"⚠️ AI-Setup already installed in: {directory}")
                print(f"  No changes will be made to this directory")
                skipped_count += 1
                continue

            # Create _AI-Setup in target directory
            target_setup = os.path.join(directory, "_AI-Setup")
            if not os.path.exists(target_setup):
                os.makedirs(target_setup)
                print(f"✅ Created AI-Setup directory in: {directory}")

            # Track how many files were copied
            copied_files = 0
            existing_files = 0

            # Copy all files from temporary _AI-Setup to target
            for item in os.listdir(setup_folder):
                source = os.path.join(setup_folder, item)
                target = os.path.join(target_setup, item)
                if os.path.isfile(source):
                    if not os.path.exists(target):
                        shutil.copy2(source, target)
                        copied_files += 1
                    else:
                        existing_files += 1
                elif os.path.isdir(source):
                    # Handle directories by recursively copying their contents
                    if not os.path.exists(target):
                        shutil.copytree(source, target)
                        print(f"  ✅ Copied directory: {item}")
                    else:
                        print(f"  ⚠️ Directory already exists: {item}")

            print(f"  ✅ Copied {copied_files} new files to {directory}")
            if existing_files > 0:
                print(f"  ⚠️ Skipped {existing_files} existing files")

            print(f"✅ Successfully installed AI-Setup in: {directory}")
            success_count += 1

        # Clean up temporary _AI-Setup if it was created for this operation
        if os.path.dirname(setup_folder) == temp_dir:
            print(f"\n🧹 Cleaning up temporary AI-Setup in: {temp_dir}")
            shutil.rmtree(setup_folder)

        # Print summary
        print("\n📊 Installation Summary:")
        print(f"  ✅ Successfully installed in {success_count} directories")
        print(f"  ⚠️ Skipped {skipped_count} directories (already installed)")
        print(f"  ❌ Failed for {failed_count} directories")

        if success_count > 0:
            print("\n✅ AI-Setup installation completed")
        else:
            print("\n⚠️ AI-Setup installation completed with no successful installations")

    # Fallback for the thought process simulator
    async def generate_content_with_ollama(description, model="phi3"):
        print("⚠️ Content generation not available: utils.thought_process module not found")
        return None

    def get_available_ollama_models():
        return ["phi3", "llama3", "mistral"]  # Default fallbacks


def setup_work_efforts_structure(base_dir=None, create_dirs=True, in_ai_setup=False):
    """
    Set up the work_efforts directory structure in the specified directory
    If no directory is specified, use the current directory
    If create_dirs is False, just return the paths without creating directories
    If in_ai_setup is True, create within the _AI-Setup folder

    Returns a tuple of (work_efforts_dir, template_path, active_dir, completed_dir, archived_path)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Define the work_efforts directory and its subdirectories
    if in_ai_setup:
        # Create inside _AI-Setup folder
        ai_setup_dir = os.path.join(base_dir, "_AI-Setup")
        if not os.path.exists(ai_setup_dir):
            if create_dirs:
                os.makedirs(ai_setup_dir)
                print(f"Created _AI-Setup directory: {ai_setup_dir}")
            else:
                print(f"Warning: _AI-Setup directory does not exist at {ai_setup_dir}")

        work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
    else:
        # Create at the root level (original behavior)
        work_efforts_dir = os.path.join(base_dir, "work_efforts")

    templates_dir = os.path.join(work_efforts_dir, "templates")
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")
    scripts_dir = os.path.join(work_efforts_dir, "scripts")

    if create_dirs:
        # Create all directories, but check if they exist first
        for directory in [work_efforts_dir, templates_dir, active_dir, completed_dir, archived_dir, scripts_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            else:
                # Directory already exists, no need to create it
                pass

        # Create a README in the work_efforts directory, but only if it doesn't exist
        readme_path = os.path.join(work_efforts_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write("""# Work Efforts

This directory contains structured documentation for tracking tasks, features, and bug fixes.

## Organization

- **active/**: Current work efforts being actively worked on
- **completed/**: Completed work efforts
- **archived/**: Archived work efforts (no longer relevant)
- **templates/**: Templates for creating new work efforts
- **scripts/**: Scripts for managing work efforts

## Usage

Create a new work effort:
```bash
code-conductor new-work-effort
# or
cc-work-e
```

List existing work efforts:
```bash
code-conductor list
```
""")
            print(f"Created README at: {readme_path}")

        # Create __init__.py files in the scripts and work_efforts directories, but only if they don't exist
        scripts_init_path = os.path.join(scripts_dir, "__init__.py")
        if not os.path.exists(scripts_init_path):
            with open(scripts_init_path, "w") as f:
                f.write("# Work Efforts Scripts\n")
            print(f"Created __init__.py at: {scripts_init_path}")

        work_efforts_init_path = os.path.join(work_efforts_dir, "__init__.py")
        if not os.path.exists(work_efforts_init_path):
            with open(work_efforts_init_path, "w") as f:
                f.write("# Work Efforts Module\n")
            print(f"Created __init__.py at: {work_efforts_init_path}")

        # Copy required scripts, but preserve existing ones
        scripts_to_copy = [
            "run_work_effort_manager.py",
            "work_effort_manager.py",
            "ai_work_effort_creator.py",
            "new_work_effort.py"
        ]

        # Define possible script source locations
        script_source_dirs = [
            # Try the current package's scripts directory (most likely location)
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "work_efforts", "scripts"),
            # Try the current working directory + work_efforts/scripts
            os.path.join(os.getcwd(), "work_efforts", "scripts"),
            # Try direct parent + work_efforts/scripts (for installed packages)
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work_efforts", "scripts"),
            # Try from absolute path (in case path is totally different)
            "/Users/ctavolazzi/Code/code_conductor/work_efforts/scripts"
        ]

        for script in scripts_to_copy:
            target_path = os.path.join(scripts_dir, script)

            # Skip if target already exists
            if os.path.exists(target_path):
                continue

            # Try all possible source locations
            script_found = False
            for source_dir in script_source_dirs:
                source_path = os.path.join(source_dir, script)
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"✅ Copied script: {script} to {scripts_dir}")
                        script_found = True
                        break  # Found and copied successfully, stop trying other paths
                    except Exception as e:
                        print(f"⚠️ Could not copy script {script} from {source_path}: {str(e)}")

            if not script_found:
                print(f"❌ Error: Could not locate required script: {script}")
                print(f"This may affect the functionality of the work effort manager")

    template_path = os.path.join(templates_dir, "work-effort-template.md")

    return work_efforts_dir, template_path, active_dir, completed_dir, archived_dir

def create_template_if_missing(template_path):
    """Copy the main template to the work efforts template directory if it doesn't exist"""
    if not os.path.exists(template_path):
        # First check if we have a template in the project root
        source_template = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "templates", "work-effort-template.md")

        if os.path.exists(source_template):
            # Copy the template from the project
            shutil.copy2(source_template, template_path)
            print(f"Created template file at: {template_path}")
        else:
            # Create a default template if source not found
            template_content = """---
title: "{{title}}"
status: "{{status}}" # options: active, paused, completed
priority: "{{priority}}" # options: low, medium, high, critical
assignee: "{{assignee}}"
created: "{{created}}" # YYYY-MM-DD HH:mm
last_updated: "{{last_updated}}" # YYYY-MM-DD HH:mm
due_date: "{{due_date}}" # YYYY-MM-DD
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# {{title}}

## 🚩 Objectives
- Clearly define goals for this work effort.

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references.

## 🐞 Issues Encountered
- Document issues and obstacles clearly.

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes.

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
            # Ensure the directory exists
            os.makedirs(os.path.dirname(template_path), exist_ok=True)

            # Write the template
            with open(template_path, "w") as f:
                f.write(template_content)
            print(f"Created template file at: {template_path}")

def create_directory_reference(command=None):
    """
    Create a local reference file in the current directory that points back to the project manifest.
    This creates a breadcrumb trail throughout the project to help trace back to the root.

    Args:
        command: The command that was executed
    """
    try:
        current_dir = os.getcwd()

        # First check if we're in a project by finding the config
        config_file, _ = find_nearest_config()
        if not config_file:
            logger.debug("Not creating directory reference - not in a project")
            return

        # Get the project root by finding the manifest file
        project_root = None
        manifest_file = None

        # Walk up the directory tree looking for .code-conductor
        search_dir = current_dir
        while search_dir:
            potential_manifest = os.path.join(search_dir, ".code-conductor")
            if os.path.exists(potential_manifest) and os.path.isfile(potential_manifest):
                manifest_file = potential_manifest
                project_root = search_dir
                break

            # Move up one directory
            parent_dir = os.path.dirname(search_dir)
            if parent_dir == search_dir:  # We've reached the root
                break
            search_dir = parent_dir

        if not manifest_file or not project_root:
            logger.debug("Could not find project manifest file")
            return

        # Don't create reference in the project root itself
        if os.path.normpath(current_dir) == os.path.normpath(project_root):
            logger.debug("Not creating reference in project root directory")
            return

        # Create the reference file
        reference_file = os.path.join(current_dir, ".code-conductor-ref")

        # Read existing references if the file exists
        existing_references = []
        if os.path.exists(reference_file):
            try:
                with open(reference_file, 'r') as f:
                    existing_references = json.load(f)
                    if not isinstance(existing_references, list):
                        existing_references = []
            except Exception as e:
                logger.warning(f"Error reading existing reference file: {str(e)}")
                existing_references = []

        # Create the new reference entry
        now = datetime.now()
        reference_data = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "command": command or "unknown",
            "current_directory": current_dir,
            "project_root": project_root,
            "relative_path": os.path.relpath(current_dir, project_root),
            "manifest_file": manifest_file
        }

        # Add to existing references (newest first)
        existing_references.insert(0, reference_data)

        # Limit to 10 most recent references
        if len(existing_references) > 10:
            existing_references = existing_references[:10]

        # Write the reference file
        with open(reference_file, 'w') as f:
            json.dump(existing_references, f, indent=2)

        logger.debug(f"Created directory reference at: {reference_file}")
    except Exception as e:
        logger.warning(f"Error creating directory reference: {str(e)}")

async def main():
    """Main function"""
    args = parse_arguments()

    # Create directory reference file for tracing
    command = args.command if hasattr(args, 'command') else None
    create_directory_reference(command)

    # Load configuration if available
    config = load_config()

    # Set up the Python path for the work effort manager
    setup_work_effort_manager_path()

    # If there's a config with work_managers.auto_start set to true, and the manager script is specified,
    # start the WorkEffortManager in the background
    if (args.command in ['new-work-effort', 'work_effort'] or args.interactive) and "work_managers" in config and \
       config["work_managers"] and \
       config["work_managers"][0].get("use_manager", False) and \
       config["work_managers"][0].get("auto_start", False) and \
       config["work_managers"][0].get("runner_script"):
        try:
            import subprocess
            runner_script = config["work_managers"][0].get("runner_script")
            subprocess.Popen([sys.executable, runner_script, "--no-auto-start"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             start_new_session=True)
            print("Started WorkEffortManager in the background.")
        except Exception as e:
            # Ensure the error message is properly encoded as a string
            error_msg = str(e)
            print(f"Warning: Could not start WorkEffortManager: {error_msg}")

    # Handle version flag
    if args.version:
        print(f"Code Conductor version {VERSION}")
        return 0

    # If run with no args, automatically check for existing components and set up as needed
    if not args.command and not args.interactive:
        print("\n🤖 AI-Setup and Work Effort Tracker")
        print("==============================")
        # Skip the confirmation prompt and directly check for components
        await setup_ai_in_current_dir()
        return 0

    # Check for commands
    if args.command:
        if args.command.lower() in ['-h', '--help', 'help']:
            print("\nCode Conductor - AI Development Environment Setup Tool")
            print(f"Version: {VERSION}")
            print("\nCommands:")
            print("  code-conductor setup                 - Set up AI assistance in the current directory")
            print("  code-conductor new-work-manager   - Create a new work effort manager in a directory")
            print("  code-conductor set-default        - Set the default work effort manager")
            print("  code-conductor new-work-effort    - Create a new work effort in _AI-Setup/work_efforts")
            print("  code-conductor work_effort        - Same as new-work-effort")
            print("  code-conductor work_effort -i     - Create a new work effort interactively")
            print("  code-conductor list               - List existing work efforts")
            print("  code-conductor list-managers      - List all work effort managers in the project")
            print("  code-conductor update-status      - Update the status of a work effort")
            print("  code-conductor select             - Select directories to set up AI assistance")
            print("  code-conductor find-root          - Show the project root and path back to it")
            print("  code-conductor help               - Show this help text")
            print("  code-conductor version            - Show the version number")
            print("\nOptions for new-work-effort command:")
            print("  --title TEXT                      - Title of the work effort (default: Untitled)")
            print("  --assignee TEXT                   - Assignee of the work effort (default: self)")
            print("  --priority [low|medium|high|critical] - Priority of the work effort (default: medium)")
            print("  --due-date YYYY-MM-DD             - Due date of the work effort (default: today)")
            print("  --use-ai                          - Use AI to generate content (requires --description)")
            print("  --description TEXT                - Description to use for AI content generation")
            print("  --model TEXT                      - Ollama model to use for AI content (default: phi3)")
            print("  --timeout SECONDS                 - Timeout for AI content generation (default: 30)")
            print("  --manager TEXT                    - Name of the work effort manager to use")
            print("  -y, --yes                         - Non-interactive mode (use defaults for all prompts)")
            print("\nShorthand Commands:")
            print("  cc-work-e                         - Quick create work effort (same as new-work-effort)")
            print("  cc-work-e -i                      - Create a work effort with interactive prompt")
            print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
            print("  cc-work-e --manager NAME          - Use a specific work effort manager")
            print("  cc-new \"Title\"                    - Simple command to create a new work effort")
            print("  cc-new \"Title\" -p high -a \"Name\"  - Create with priority and assignee")
            print("  cc-index                          - Index and categorize work efforts")
            print("  cc-trace                          - Trace work effort relationships")
            print("\nFor all available options, run: code-conductor help")
            return 0

        # Current directory check
        current_dir = os.getcwd()

        if args.command.lower() == 'new-work-manager':
            # Get target directory from args or use current directory
            target_dir = args.target_dir if hasattr(args, 'target_dir') and args.target_dir else current_dir

            # Get manager name from args or generate from directory name
            manager_name = args.manager_name if hasattr(args, 'manager_name') and args.manager_name else None

            success, message = add_work_manager(target_dir, manager_name)
            if success:
                print(f"✅ {message}")
                print("\nYou can now create work efforts in this directory with:")
                print(f"  code-conductor new-work-effort --manager {manager_name or os.path.basename(target_dir)}")
                print("  OR")
                print(f"  cc-work-e --manager {manager_name or os.path.basename(target_dir)}")
                return 0
            else:
                print(f"❌ {message}")
                return 1

        elif args.command.lower() == 'set-default':
            # Get manager name from args
            if not hasattr(args, 'manager_name') or not args.manager_name:
                print("❌ You must specify a manager name with --manager-name")
                return 1

            # Find the project config
            config_file, config_data = find_nearest_config()
            if not config_file:
                print("❌ No project configuration found. Run 'code-conductor setup' first.")
                return 1

            # Find the manager by name
            manager_found = False
            for manager in config_data.get("work_managers", []):
                if manager.get("name") == args.manager_name:
                    config_data["default_work_manager"] = manager.get("path")
                    manager_found = True
                    break

            if not manager_found:
                print(f"❌ Work effort manager '{args.manager_name}' not found.")
                return 1

            # Update the config
            project_root = os.path.dirname(os.path.dirname(config_file))
            create_or_update_config(project_root, config_data)

            print(f"✅ Default work effort manager set to '{args.manager_name}'")
            return 0

        elif args.command.lower() == 'list-managers':
            # Find the project config
            config_file, config_data = find_nearest_config()
            if not config_file or not config_data or not config_data.get("work_managers"):
                print("❌ No work effort managers found. Run 'code-conductor setup' first.")
                return 1

            # Get the project root directory
            project_root = config_data.get("project_root")
            if not project_root:
                project_root = os.path.dirname(os.path.dirname(config_file))

            # Get the default manager path
            default_manager_path = config_data.get("default_work_manager")

            # List all managers
            print("\n📋 Work Effort Managers:")
            print("========================")

            for manager in config_data.get("work_managers", []):
                name = manager.get("name", "Unnamed")
                path = manager.get("path", "Unknown")
                work_efforts_dir = manager.get("work_efforts_dir", "work_efforts")
                is_default = path == default_manager_path

                print(f"- {name} {'(DEFAULT)' if is_default else ''}")
                print(f"  Path: {os.path.join(project_root, path)}")
                print(f"  Work Efforts: {os.path.join(project_root, path, work_efforts_dir)}")
                print()

            return 0

        elif args.command.lower() in ['work_effort', 'new-work-effort', 'create']:
            # Check for work_efforts directory using the appropriate manager
            manager_name = args.manager if hasattr(args, 'manager') and args.manager else None

            # Use verbose mode when searching for work efforts
            verbose = not args.quiet if hasattr(args, 'quiet') else True
            work_efforts_dir, manager_info = find_work_efforts_directory(manager_name, verbose=verbose)

            if not work_efforts_dir:
                current_dir = os.getcwd()
                potential_location = os.path.join(current_dir, "_AI-Setup", "work_efforts")

                print(f"\n📋 Work Effort Management")
                print("======================")
                print(f"❌ No work effort folder found in the current directory: {current_dir}")

                if manager_name:
                    print(f"⚠️ Manager '{manager_name}' not found")

                # Automatically set up without asking
                print(f"Creating work effort folder at: {potential_location}")
                await setup_ai_in_current_dir()
                # After setup, try to find the directory again
                work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                if not work_efforts_dir:
                    print("❌ Setup failed to create work efforts directory")
                    return 1

            # Determine the directories to use based on manager_info
            template_dir = os.path.join(work_efforts_dir, "templates")
            active_dir = os.path.join(work_efforts_dir, "active")

            # Ensure directories exist
            for directory in [template_dir, active_dir]:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            # Find or create template
            template_path = os.path.join(template_dir, "work-effort-template.md")
            create_template_if_missing(template_path)

            # Run in appropriate mode based on interactive flag
            if args.interactive:
                # Run in interactive mode if -i/--interactive flag was set
                await interactive_mode(template_path, active_dir, manager_info)
            else:
                # Run in non-interactive mode by default
                work_effort_path = await non_interactive_mode(args, template_path, active_dir, manager_info)
                if work_effort_path:
                    print(f"✅ Work effort created successfully at: {work_effort_path}")
                else:
                    print("❌ Failed to create work effort")
                    return 1

            return 0

        elif args.command.lower() == 'list':
            # Get work efforts directory from appropriate manager
            manager_name = args.manager if hasattr(args, 'manager') and args.manager else None

            # Use verbose mode when searching for work efforts
            verbose = not args.quiet if hasattr(args, 'quiet') else True
            work_efforts_dir, manager_info = find_work_efforts_directory(manager_name, verbose=verbose)

            if not work_efforts_dir:
                current_dir = os.getcwd()
                print(f"\n📋 Work Effort Management")
                print("======================")
                print(f"❌ No work effort folder found in the current directory: {current_dir}")

                if manager_name:
                    print(f"⚠️ Manager '{manager_name}' not found")

                # Automatically set up without asking
                print(f"Setting up work efforts in current directory")
                await setup_ai_in_current_dir()
                work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                if not work_efforts_dir:
                    print("❌ Setup failed to create work efforts directory")
                    return 1

            # If a manager was specified, mention it
            if manager_name and manager_info:
                print(f"\n📋 Work Efforts in '{manager_info.get('name', manager_name)}' Manager at {work_efforts_dir}:")
            else:
                print(f"\n📋 Work Efforts at {work_efforts_dir}:")

            list_work_efforts(work_efforts_dir)
            return 0

        elif args.command.lower() == 'select':
            return await setup_selected_directories()

        elif args.command.lower() == 'setup':
            return await setup_ai_in_current_dir()

        elif args.command.lower() == 'find-root':
            # Find the project root using the manifest file
            current_dir = os.getcwd()
            project_root = None
            manifest_file = None

            # Check if there's a local reference file
            local_ref_file = os.path.join(current_dir, ".code-conductor-ref")
            if os.path.exists(local_ref_file):
                try:
                    with open(local_ref_file, 'r') as f:
                        reference_data = json.load(f)
                        if reference_data and isinstance(reference_data, list) and len(reference_data) > 0:
                            # Use the most recent reference
                            latest_ref = reference_data[0]
                            project_root = latest_ref.get("project_root")
                            manifest_file = latest_ref.get("manifest_file")
                            relative_path = latest_ref.get("relative_path")

                            print(f"\n📍 Project Information from Local Reference:")
                            print(f"  Project Root: {project_root}")
                            print(f"  Current Directory: {current_dir}")
                            print(f"  Relative Path: {relative_path}")
                            print(f"  Manifest File: {manifest_file}")
                            print(f"  Last Command: {latest_ref.get('command')}")
                            print(f"  Timestamp: {latest_ref.get('timestamp')}")

                            # Show directory traversal command
                            if project_root:
                                print(f"\n🔙 To return to project root, run:")
                                print(f"  cd {project_root}")

                            return 0
                except Exception as e:
                    print(f"⚠️ Error reading local reference file: {str(e)}")

            # If we don't have a local reference or it failed, try finding the project root
            search_dir = current_dir
            while search_dir:
                potential_manifest = os.path.join(search_dir, ".code-conductor")
                if os.path.exists(potential_manifest) and os.path.isfile(potential_manifest):
                    manifest_file = potential_manifest
                    project_root = search_dir
                    break

                # Move up one directory
                parent_dir = os.path.dirname(search_dir)
                if parent_dir == search_dir:  # We've reached the root
                    break
                search_dir = parent_dir

            if project_root:
                relative_path = os.path.relpath(current_dir, project_root)
                print(f"\n📍 Project Information:")
                print(f"  Project Root: {project_root}")
                print(f"  Current Directory: {current_dir}")
                print(f"  Relative Path: {relative_path}")
                print(f"  Manifest File: {manifest_file}")

                # Show directory traversal command
                print(f"\n🔙 To return to project root, run:")
                print(f"  cd {project_root}")

                return 0
            else:
                print(f"❌ Could not find project root. Are you in a Code Conductor project?")
                print(f"   Try running 'code-conductor setup' to initialize a project.")
                return 1

        elif args.command.lower() == 'update-status':
            # Get required arguments
            work_effort_name = getattr(args, 'work_effort', None)
            new_status = getattr(args, 'new_status', None)
            old_status = getattr(args, 'old_status', 'active')

            # Validate inputs
            if not work_effort_name:
                print("❌ Error: Work effort name is required")
                print("Usage: code-conductor update-status --work-effort <name> --new-status <status> [--old-status <status>]")
                return 1

            if not new_status:
                print("❌ Error: New status is required")
                print("Usage: code-conductor update-status --work-effort <name> --new-status <status> [--old-status <status>]")
                return 1

            if new_status not in ['active', 'completed', 'archived', 'paused']:
                print(f"❌ Error: Invalid status: {new_status}")
                print("Valid statuses: active, completed, archived, paused")
                return 1

            # Get work efforts directory using appropriate manager
            manager_name = getattr(args, 'manager', None)
            work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)

            if not work_efforts_dir:
                print(f"❌ Error: Work efforts directory not found")
                if manager_name:
                    print(f"⚠️ Manager '{manager_name}' not found")
                return 1

            # Find the work effort
            old_dir = os.path.join(work_efforts_dir, old_status)
            matched_files = []

            if os.path.exists(old_dir):
                # Look for files directly in the status directory
                for filename in os.listdir(old_dir):
                    if filename.endswith('.md') and work_effort_name.lower() in filename.lower():
                        matched_files.append(os.path.join(old_dir, filename))

                # Also check subdirectories
                for root, dirs, files in os.walk(old_dir):
                    if root == old_dir:
                        continue  # Skip the top directory as we've already processed it
                    for filename in files:
                        if filename.endswith('.md') and work_effort_name.lower() in filename.lower():
                            matched_files.append(os.path.join(root, filename))

            if not matched_files:
                print(f"❌ Error: No work effort found matching '{work_effort_name}' with status '{old_status}'")
                return 1

            if len(matched_files) > 1:
                print(f"⚠️ Multiple work efforts found matching '{work_effort_name}':")
                for i, file_path in enumerate(matched_files):
                    print(f"  {i+1}. {os.path.basename(file_path)}")

                # Ask user to select one
                selection = input("Please select a work effort by number (or 'q' to quit): ")
                if selection.lower() == 'q':
                    return 0

                try:
                    index = int(selection) - 1
                    if index < 0 or index >= len(matched_files):
                        print("❌ Invalid selection.")
                        return 1
                    selected_path = matched_files[index]
                except ValueError:
                    print("❌ Invalid selection. Please enter a number.")
                    return 1
            else:
                selected_path = matched_files[0]

            # Get just the filename
            filename = os.path.basename(selected_path)

            print(f"Updating status of '{filename}' from '{old_status}' to '{new_status}'...")

            # Try to update using WorkEffortManager if available
            try:
                # Determine the current directory
                current_dir = os.getcwd()

                # Check if we can import the WorkEffortManager
                # Assuming _AI-Setup is in the sys.path
                sys.path.append(os.path.join(current_dir, "_AI-Setup"))

                try:
                    from work_efforts.scripts.work_effort_manager import WorkEffortManager

                    # Initialize the WorkEffortManager
                    manager = WorkEffortManager(project_dir=current_dir)

                    # Update the status
                    success = manager.update_work_effort_status(filename, new_status, old_status)

                    if success:
                        print(f"✅ Work effort status updated successfully")
                        new_dir = os.path.join(work_efforts_dir, new_status)
                        new_path = os.path.join(new_dir, filename)
                        print(f"New location: {new_path}")
                        return 0
                    else:
                        print("❌ Failed to update work effort status using WorkEffortManager")
                except ImportError:
                    print("⚠️ WorkEffortManager not available, using fallback method...")
            except Exception as e:
                print(f"⚠️ Error with WorkEffortManager: {str(e)}")
                print("Using fallback method...")

            # Fallback method: Direct file manipulation
            try:
                # Read the content
                with open(selected_path, 'r') as f:
                    content = f.read()

                # Update the status in the content
                status_pattern = r'status: "(active|completed|archived|paused)"'
                replacement = f'status: "{new_status}"'

                if re.search(status_pattern, content):
                    updated_content = re.sub(status_pattern, replacement, content)
                else:
                    print(f"❌ Status field not found in work effort document")
                    return 1

                # Update the last_updated timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated_content = re.sub(r'last_updated: "[^"]+"', f'last_updated: "{timestamp}"', updated_content)

                # Determine the target directory
                new_dir = os.path.join(work_efforts_dir, new_status)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

                # Write to the new location
                new_path = os.path.join(new_dir, filename)
                with open(new_path, 'w') as f:
                    f.write(updated_content)

                # Remove the old file if it's different
                if new_path != selected_path:
                    os.remove(selected_path)

                print(f"✅ Work effort status updated successfully")
                print(f"New location: {new_path}")
                return 0
            except Exception as e:
                print(f"❌ Error updating work effort status: {str(e)}")
                return 1

        else:
            print(f"Unknown command: {args.command}")
            print("Run 'code-conductor help' for usage information")
            return 1

    # Interactive mode without a specific command
    if args.interactive:
        # Check for work_efforts directory using appropriate manager
        manager_name = args.manager if hasattr(args, 'manager') and args.manager else None
        work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)

        if not work_efforts_dir:
            print(f"⚠️ Work efforts directory not found")
            if manager_name:
                print(f"⚠️ Manager '{manager_name}' not found")

            # Setup automatically since we need the directories
            print("\nSetting up work efforts directory first...")
            await setup_ai_in_current_dir()
            # After setup, try to find the directory again
            work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
            if not work_efforts_dir:
                print("❌ Setup failed to create work efforts directory")
                return 1

        # Determine the directories to use
        template_dir = os.path.join(work_efforts_dir, "templates")
        active_dir = os.path.join(work_efforts_dir, "active")

        # Ensure directories exist
        for directory in [template_dir, active_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Find or create template
        template_path = os.path.join(template_dir, "work-effort-template.md")
        create_template_if_missing(template_path)

        # Since interactive flag was specified, always run in interactive mode
        await interactive_mode(template_path, active_dir, manager_info)
        return 0

    # If in interactive mode and no command provided, check if components exist
    if args.interactive and not args.command:
        # Check if _AI-Setup/work_efforts exists
        current_dir = os.getcwd()
        work_efforts_dir = os.path.join(current_dir, "_AI-Setup", "work_efforts")
        if not os.path.exists(work_efforts_dir):
            print(f"\n❓ Work efforts directory not found: {work_efforts_dir}")
            print("Setting up interactively...")
            # Run in interactive mode since that was specifically requested
            # The setup function itself doesn't have interactive vs non-interactive mode anymore
            # So just call the standard setup function
            return await setup_ai_in_current_dir()
        else:
            print(f"\n✅ Work efforts directory found: {work_efforts_dir}")
            # Continue with interactive work effort creation

def main_entry():
    """Entry point for console_scripts"""
    return asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())

def print_version():
    """Print the version number."""
    print(f"Code Conductor version {VERSION}")

def show_instructions():
    """Show usage instructions."""
    print("\nUsage Instructions:")
    print("  code-conductor setup                 - Set up AI assistance in the current directory")
    print("  code-conductor new-work-effort       - Create a new work effort in _AI-Setup/work_efforts")
    print("  code-conductor work_effort -i        - Create a new work effort interactively")
    print("  code-conductor list                  - List existing work efforts")
    print("  code-conductor update-status         - Update the status of a work effort")
    print("  code-conductor select                - Select directories to set up AI assistance")
    print("  code-conductor find-root             - Show the project root and path back to it")
    print("\nEnhanced Work Effort Creator:")
    print("  cc-work-e                            - Quick create work effort in _AI-Setup/work_efforts")
    print("  cc-work-e -i                         - Create a work effort with interactive prompt")
    print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
    print("  cc-work-e --manager NAME             - Use a specific work effort manager")
    print("  cc-new \"Title\"                       - Simple command to create a new work effort")
    print("  cc-new \"Title\" -p high -a \"Name\"     - Create with priority and assignee")
    print("  cc-index                             - Index and categorize work efforts")
    print("  cc-trace                             - Trace work effort relationships")
    print("\nFor all available options, run: code-conductor help")

async def create_work_effort(args):
    """Create a new work effort."""
    try:
        # Get the default manager path
        default_manager_path = config_data.get("default_work_manager")

        # Ensure directories exist
        for directory in [template_dir, active_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Find or create template
        template_path = os.path.join(template_dir, "work-effort-template.md")
        create_template_if_missing(template_path)

        # Create WorkEffortManager instance
        manager = WorkEffortManager(
            project_dir=os.getcwd(),
            config=config_data
        )

        # Run in appropriate mode based on interactive flag
        if args.interactive:
            # Run in interactive mode if -i/--interactive flag was set
            await interactive_mode(template_path, active_dir, manager)
        else:
            # Run in non-interactive mode by default
            work_effort_path = await non_interactive_mode(args, template_path, active_dir, manager)
            if work_effort_path:
                print(f"✅ Work effort created successfully at: {work_effort_path}")
            else:
                print("❌ Failed to create work effort")
                return 1

        return 0

    except Exception as e:
        logger.error(f"Error creating work effort: {e}")
        return 1

async def interactive_mode(template_path, active_dir, manager):
    """Run in interactive mode."""
    try:
        # Get user input
        title = input("\nEnter work effort title: ").strip()
        if not title:
            print("❌ Title is required")
            return None

        description = input("Enter description (optional): ").strip()
        assignee = input("Enter assignee (optional): ").strip()
        priority = input("Enter priority (high/medium/low, optional): ").strip()
        due_date = input("Enter due date (YYYY-MM-DD, optional): ").strip()

        # Create work effort
        work_effort_path = manager.create_work_effort(
            title=title,
            description=description,
            assignee=assignee if assignee else None,
            priority=priority if priority else None,
            due_date=due_date if due_date else None
        )

        if work_effort_path:
            print(f"✅ Work effort created successfully at: {work_effort_path}")
            return work_effort_path
        else:
            print("❌ Failed to create work effort")
            return None

    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        return None

async def non_interactive_mode(args, template_path, active_dir, manager):
    """Run in non-interactive mode."""
    try:
        # Create work effort
        work_effort_path = manager.create_work_effort(
            title=args.title,
            description=args.description or "",
            assignee=args.assignee,
            priority=args.priority,
            due_date=args.due_date,
            use_ai=args.use_ai
        )

        if work_effort_path:
            return work_effort_path
        else:
            print("❌ Failed to create work effort")
            return None

    except Exception as e:
        logger.error(f"Error in non-interactive mode: {e}")
        return None