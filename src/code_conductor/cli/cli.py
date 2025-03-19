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
from datetime import datetime, timedelta
import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

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
from ..core.work_effort.validator import WorkEffortValidator
from ..core.work_effort.manager import WorkEffortManager
from ..core.work_effort.counter import WorkEffortCounter
from ..core.work_effort.template import WorkEffortTemplate
from ..core.work_effort.event_emitter import EventEmitter
from ..core.work_effort.parser import WorkEffortParser
from ..core.work_effort.formatter import WorkEffortFormatter
from ..core.work_effort.tracer import WorkEffortTracer
from ..core.work_effort.indexer import WorkEffortIndexer
from ..core.work_effort.manager_info import WorkEffortManagerInfo
from ..core.work_effort.manager_config import WorkEffortManagerConfig
from ..core.work_effort.manager_factory import WorkEffortManagerFactory
from ..core.work_effort.manager_registry import WorkEffortManagerRegistry
from ..core.work_effort.manager_loader import WorkEffortManagerLoader
from ..core.work_effort.manager_validator import WorkEffortManagerValidator
from ..core.work_effort.manager_parser import WorkEffortManagerParser
from ..core.work_effort.manager_formatter import WorkEffortManagerFormatter
from ..core.work_effort.manager_tracer import WorkEffortManagerTracer
from ..core.work_effort.manager_indexer import WorkEffortManagerIndexer

def validate_title(title: str) -> str:
    """
    Validate a work effort title.

    Args:
        title: The title to validate

    Returns:
        str: The validated title

    Raises:
        ValueError: If the title is invalid
    """
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string")
    if len(title) < 3 or len(title) > 100:
        raise ValueError("Title must be between 3 and 100 characters")
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_\- ]*$', title):
        raise ValueError("Title must start with a letter or number and contain only letters, numbers, underscores, hyphens, and spaces")
    return title

def validate_date(date_str: str) -> str:
    """
    Validate a date string.

    Args:
        date_str: The date string to validate (YYYY-MM-DD)

    Returns:
        str: The validated date string

    Raises:
        ValueError: If the date string is invalid
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date must be a non-empty string")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")

def validate_priority(priority: str) -> str:
    """
    Validate a priority value.

    Args:
        priority: The priority to validate

    Returns:
        str: The validated priority

    Raises:
        ValueError: If the priority is invalid
    """
    if not priority or not isinstance(priority, str):
        raise ValueError("Priority must be a non-empty string")
    priority = priority.lower()
    if priority not in ["high", "medium", "low"]:
        raise ValueError("Priority must be one of: high, medium, low")
    return priority

def print_version():
    """Print the current version of Code Conductor."""
    print(f"Code Conductor version {VERSION}")

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

    # Get the project root directory (parent of _AI-Setup)
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

    # Update the config file in the _AI-Setup directory
    ai_setup_dir = os.path.dirname(config_file)
    create_or_update_config(ai_setup_dir, config_data)

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
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/code_conductor/scripts"),
            # Try the current working directory + work_efforts/scripts
            os.path.join(os.getcwd(), "src/code_conductor/scripts"),
            # Try direct parent + work_efforts/scripts (for installed packages)
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src/code_conductor/scripts"),
            # Try from absolute path (in case path is totally different)
            "/Users/ctavolazzi/Code/code_conductor/src/code_conductor/scripts"
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

def setup_work_effort_manager_path():
    """Set up the Python path for the work effort manager."""
    try:
        # Get the directory containing the work effort manager
        manager_dir = os.path.dirname(os.path.abspath(__file__))
        manager_dir = os.path.join(manager_dir, '..', 'work_efforts')

        # Add the manager directory to the Python path
        if manager_dir not in sys.path:
            sys.path.insert(0, manager_dir)

        logger.debug(f"Added work effort manager path: {manager_dir}")
    except Exception as e:
        logger.warning(f"Error setting up work effort manager path: {str(e)}")

async def setup_ai_in_current_dir():
    """Set up AI components in the current directory."""
    try:
        # Create _AI-Setup directory if it doesn't exist
        ai_setup_dir = os.path.join(os.getcwd(), '_AI-Setup')
        os.makedirs(ai_setup_dir, exist_ok=True)

        # Create work_efforts directory if it doesn't exist
        work_efforts_dir = os.path.join(ai_setup_dir, 'work_efforts')
        os.makedirs(work_efforts_dir, exist_ok=True)

        # Create subdirectories for different work effort statuses
        for status in ['active', 'completed', 'archived', 'paused']:
            os.makedirs(os.path.join(work_efforts_dir, status), exist_ok=True)

        # Create counter file if it doesn't exist
        counter_file = os.path.join(ai_setup_dir, 'counter.json')
        if not os.path.exists(counter_file):
            with open(counter_file, 'w') as f:
                json.dump({'counter': 0}, f)

        # Create config file if it doesn't exist
        config_file = os.path.join(ai_setup_dir, 'config.json')
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump({
                    'work_managers': [],
                    'default_manager': None,
                    'settings': {
                        'use_sequential_numbering': True,
                        'auto_start': False
                    }
                }, f, indent=2)

        logger.debug(f"Set up AI components in: {ai_setup_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error setting up AI components: {str(e)}")
        return 1

async def setup_selected_directories():
    """Set up selected directories for work effort management."""
    try:
        # Get the current directory
        current_dir = os.getcwd()

        # Create work_efforts directory if it doesn't exist
        work_efforts_dir = os.path.join(current_dir, 'work_efforts')
        os.makedirs(work_efforts_dir, exist_ok=True)

        # Create subdirectories for different work effort statuses
        for status in ['active', 'completed', 'archived', 'paused']:
            os.makedirs(os.path.join(work_efforts_dir, status), exist_ok=True)

        # Create counter file if it doesn't exist
        counter_file = os.path.join(work_efforts_dir, 'counter.json')
        if not os.path.exists(counter_file):
            with open(counter_file, 'w') as f:
                json.dump({'counter': 0}, f)

        logger.debug(f"Set up selected directories in: {work_efforts_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error setting up selected directories: {str(e)}")
        return 1

def set_default_manager(args: argparse.Namespace) -> int:
    """Set the default work effort manager.

    Args:
        args: Command line arguments.

    Returns:
        Exit code.
    """
    try:
        # Get manager name
        manager_name = args.manager_name
        if not manager_name:
            print("❌ Manager name is required")
            return 1

        # Find project config
        config_file, config_data = find_nearest_config()
        if not config_file or not config_data:
            print("No project configuration found.")
            return 1

        # Find manager by name
        found = False
        for manager in config_data.get("work_managers", []):
            if manager.get("name") == manager_name:
                config_data["default_work_manager"] = manager.get("path")
                found = True
                break

        if not found:
            print(f"❌ Manager not found: {manager_name}")
            return 1

        # Update config
        create_or_update_config(os.path.dirname(config_file), config_data)
        print(f"✅ Set default manager to: {manager_name}")
        return 0

    except Exception as e:
        logger.error(f"Error setting default manager: {str(e)}")
        return 1

def list_work_managers() -> None:
    """List all work effort managers in the project."""
    try:
        # Find project config
        config_file, config_data = find_nearest_config()
        if not config_file or not config_data:
            print("No project configuration found.")
            return

        # Get work managers
        work_managers = config_data.get("work_managers", [])
        if not work_managers:
            print("\nNo work managers found.")
            return

        # Get default manager
        default_manager = config_data.get("default_work_manager")

        # Display managers
        print("\nWork Effort Managers:")
        print("====================")
        for manager in work_managers:
            name = manager.get("name", "unnamed")
            path = manager.get("path", "unknown")
            is_default = path == default_manager
            status = "✓ default" if is_default else ""
            print(f"\n{name}")
            print(f"  Path: {path}")
            print(f"  Work Efforts Dir: {manager.get('work_efforts_dir', 'work_efforts')}")
            print(f"  Auto Start: {manager.get('auto_start', False)}")
            if status:
                print(f"  Status: {status}")

    except Exception as e:
        logger.error(f"Error listing work managers: {str(e)}")
        print("\nError listing work managers. Please check the logs for details.")

async def create_work_effort(args: argparse.Namespace, manager: WorkEffortManager) -> int:
    """Create a new work effort.

    Args:
        args: Command line arguments.
        manager: Work effort manager instance.

    Returns:
        Exit code.
    """
    try:
        # Get work effort details
        title = args.title
        assignee = args.assignee or "self"
        priority = args.priority or "medium"
        due_date = args.due_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        description = args.description

        # Interactive mode
        if args.interactive and not args.yes:
            print("\nCreate New Work Effort")
            print("=====================")

            # Get title
            if not title:
                title = input("Title: ")
            else:
                print(f"Title: {title}")

            # Get assignee
            assignee = input(f"Assignee [{assignee}]: ") or assignee

            # Get priority
            priority_options = ["low", "medium", "high", "critical"]
            while True:
                priority_input = input(f"Priority ({', '.join(priority_options)}) [{priority}]: ") or priority
                if priority_input.lower() in priority_options:
                    priority = priority_input.lower()
                    break
                print("Invalid priority. Please choose from:", ", ".join(priority_options))

            # Get due date
            while True:
                due_date_input = input(f"Due Date (YYYY-MM-DD) [{due_date}]: ") or due_date
                try:
                    datetime.strptime(due_date_input, "%Y-%m-%d")
                    due_date = due_date_input
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD")

            # Get description
            if not description:
                description = input("Description (optional): ")

        # Validate required fields
        if not title:
            print("❌ Title is required")
            return 1

        # Create work effort
        print(f"\nCreating work effort with title: {title}, assignee: {assignee}, priority: {priority}, due date: {due_date}")

        # Generate AI content if requested
        ai_content = None
        if args.use_ai and args.description:
            try:
                ai_content = await generate_content_with_ollama(args.description, args.model)
                if ai_content:
                    print("✅ Generated AI content")
                    description = ai_content
            except Exception as e:
                logger.warning(f"Failed to generate AI content: {str(e)}")
                print("⚠️ Failed to generate AI content, proceeding with default template")

        # Create the work effort
        work_effort_id = manager.create_work_effort(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date,
            description=description
        )

        if work_effort_id:
            print("✅ Work effort created successfully")
            return 0
        else:
            print("❌ Failed to create work effort")
            print("   ▶ Run 'code-conductor setup' if this is the first work effort in the project")
            return 1

    except Exception as e:
        logger.error(f"Error creating work effort: {str(e)}")
        return 1

async def select_work_effort(args: argparse.Namespace, manager: WorkEffortManager) -> int:
    """Select a work effort to work on.

    Args:
        args: Command line arguments.
        manager: Work effort manager instance.

    Returns:
        Exit code.
    """
    try:
        # Get list of work efforts
        work_efforts = manager.list_work_efforts()
        if not work_efforts:
            print("No work efforts found.")
            return 1

        # Display work efforts
        print("\nAvailable Work Efforts:")
        print("======================")
        for i, work_effort in enumerate(work_efforts, 1):
            title = work_effort.get("title", "Untitled")
            status = work_effort.get("status", "unknown")
            assignee = work_effort.get("assignee", "unassigned")
            print(f"{i}. {title} ({status}) - {assignee}")

        # Get selection
        if args.interactive:
            try:
                selection = input("\nSelect a work effort (number): ")
                index = int(selection) - 1
                if 0 <= index < len(work_efforts):
                    selected = work_efforts[index]
                    print(f"\nSelected: {selected.get('title', 'Untitled')}")
                    return 0
                else:
                    print("Invalid selection.")
                    return 1
            except ValueError:
                print("Invalid input. Please enter a number.")
                return 1
        else:
            # Non-interactive mode requires work effort title
            title = args.title
            if not title:
                print("Please provide a work effort title with --title in non-interactive mode.")
                return 1

            # Find work effort by title
            for work_effort in work_efforts:
                if work_effort.get("title") == title:
                    print(f"\nSelected: {title}")
                    return 0

            print(f"Work effort not found: {title}")
            return 1

    except Exception as e:
        logger.error(f"Error selecting work effort: {str(e)}")
        return 1

async def setup_project(project_root: str) -> int:
    """Set up a new Code Conductor project.

    Args:
        project_root: The root directory of the project.

    Returns:
        Exit code.
    """
    try:
        # Create _AI-Setup directory
        ai_setup_dir = os.path.join(project_root, "_AI-Setup")
        os.makedirs(ai_setup_dir, exist_ok=True)
        print(f"✅ Created _AI-Setup directory at: {ai_setup_dir}")

        # Create work_efforts directory and structure
        work_efforts_dir, template_path, active_dir, completed_dir, archived_dir = setup_work_efforts_structure(project_root, create_dirs=True, in_ai_setup=True)
        print(f"✅ Created work efforts structure in: {work_efforts_dir}")

        # Create initial configuration
        config_file, config_data = create_or_update_config(project_root)
        if not config_file:
            print("❌ Failed to create configuration file")
            return 1
        print(f"✅ Created configuration at: {config_file}")

        # Create project manifest
        manifest_file = os.path.join(project_root, ".code-conductor")
        manifest_data = {
            "version": VERSION,
            "setup_path": "_AI-Setup",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Remove existing manifest file if it's a directory
        if os.path.exists(manifest_file):
            if os.path.isdir(manifest_file):
                shutil.rmtree(manifest_file)
            else:
                os.remove(manifest_file)

        # Create new manifest file
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f, indent=2)
        print(f"✅ Created project manifest at: {manifest_file}")

        print("\n✅ Project setup complete!")
        return 0

    except Exception as e:
        logger.error(f"Error setting up project: {str(e)}")
        return 1

async def main() -> int:
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Show version if requested
        if args.version:
            print(f"Code Conductor v{VERSION}")
            return 0

        # Get project root
        project_root = find_project_root()
        if not project_root:
            print("❌ Could not find project root. Run 'code-conductor setup' first.")
            return 1

        # Get work efforts directory
        work_efforts_dir = find_work_efforts_dir()
        if not work_efforts_dir:
            print("❌ Could not find work efforts directory. Run 'code-conductor setup' first.")
            return 1

        # Create manager instance
        manager = WorkEffortManager(project_dir=project_root)

        # Handle commands
        if args.command == "setup":
            return await setup_project(project_root)

        elif args.command == "new-work-effort":
            return await create_work_effort(args, manager)

        elif args.command == "new-work-manager":
            return await create_work_manager(args)

        elif args.command == "list-managers":
            list_work_managers()
            return 0

        elif args.command == "set-default":
            return set_default_manager(args)

        elif args.command == "update-status":
            return await update_work_effort_status(args, manager)

        elif args.command == "list":
            list_work_efforts(work_efforts_dir)
            return 0

        elif args.command == "select":
            return await select_work_effort(args, manager)

        elif args.command == "find-root":
            print(f"Project root: {project_root}")
            return 0

        elif args.command == "cc-index":
            # Index all work efforts
            manager.index_all_work_efforts()
            print("✅ Indexed all work efforts")
            return 0

        else:
            print("❌ Unknown command.")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1

async def update_work_effort_status(args, manager):
    """Update the status of a work effort.

    Args:
        args: Command line arguments.
        manager: WorkEffortManager instance.

    Returns:
        Exit code.
    """
    try:
        # Get work effort title/ID
        work_effort_title = args.work_effort
        if not work_effort_title:
            print("❌ No work effort specified.")
            return 1

        # Get new status
        new_status = args.new_status
        if not new_status:
            print("❌ No new status specified.")
            return 1

        # Get all work efforts
        work_efforts = manager.list_work_efforts()

        # Find work effort by title
        matching_efforts = [w for w in work_efforts if work_effort_title.lower() in w.get("metadata", {}).get("title", "").lower()]

        if not matching_efforts:
            print(f"❌ No work effort found with title containing '{work_effort_title}'")
            return 1

        # Get the work effort to update
        work_effort = None
        if len(matching_efforts) > 1:
            if args.interactive:
                print("\nMultiple matching work efforts found:")
                for i, effort in enumerate(matching_efforts, 1):
                    print(f"{i}. {effort.get('metadata', {}).get('title')} (ID: {effort.get('id')})")

                while True:
                    try:
                        selection = input("\nSelect work effort (number): ")
                        index = int(selection) - 1
                        if 0 <= index < len(matching_efforts):
                            work_effort = matching_efforts[index]
                            break
                        else:
                            print("❌ Invalid selection. Please try again.")
                    except ValueError:
                        print("❌ Invalid input. Please enter a number.")
            else:
                # In non-interactive mode, use the first match
                work_effort = matching_efforts[0]
        else:
            work_effort = matching_efforts[0]

        # Update work effort status
        if work_effort:
            if manager.update_status(work_effort.get("id"), new_status):
                print(f"✅ Updated work effort status to: {new_status}")
                return 0
            else:
                print("❌ Failed to update work effort status.")
                return 1
        else:
            print("❌ No work effort selected.")
            return 1

    except Exception as e:
        logger.error(f"Error updating work effort status: {str(e)}")
        return 1

def list_work_efforts(work_efforts_dir: str) -> None:
    """List all work efforts in the directory.

    Args:
        work_efforts_dir: The directory containing work efforts.
    """
    try:
        # Create manager instance
        manager = WorkEffortManager(os.path.dirname(work_efforts_dir))

        # Get work efforts
        work_efforts = manager.list_work_efforts()

        # Format output
        if not work_efforts:
            print("\nNo work efforts found.")
            return

        print("\nWork Efforts:")
        print("=============")

        for work_effort in work_efforts:
            metadata = work_effort.get("metadata", {})
            title = metadata.get("title", "Untitled")
            status = metadata.get("status", "unknown")
            assignee = metadata.get("assignee", "unassigned")
            priority = metadata.get("priority", "none")

            print(f"\n{title}")
            print(f"  Status: {status}")
            print(f"  Assignee: {assignee}")
            print(f"  Priority: {priority}")

    except Exception as e:
        logger.error(f"Error listing work efforts: {str(e)}")
        print("\nError listing work efforts. Please check the logs for details.")

def find_project_root() -> Optional[str]:
    """Find the root directory of the Code Conductor project.

    Returns:
        The project root directory if found, None otherwise.
    """
    try:
        current_dir = os.getcwd()

        # Look for _AI-Setup directory or work_efforts directory
        while current_dir != "/":
            if os.path.exists(os.path.join(current_dir, "_AI-Setup")) or \
               os.path.exists(os.path.join(current_dir, "work_efforts")):
                return current_dir

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                break

            current_dir = parent_dir

        return None

    except Exception as e:
        logger.error(f"Error finding project root: {str(e)}")
        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Code Conductor CLI")
    parser.add_argument("--version", action="store_true", help="Show version number")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("-y", "--yes", action="store_true", help="Non-interactive mode (use defaults)")
    parser.add_argument("--manager", help="Work effort manager to use")
    parser.add_argument("--title", help="Title for work effort")
    parser.add_argument("--assignee", help="Assignee for work effort")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], help="Priority for work effort")
    parser.add_argument("--due-date", help="Due date for work effort (YYYY-MM-DD)")
    parser.add_argument("--use-ai", action="store_true", help="Use AI for content generation")
    parser.add_argument("--description", help="Description for AI content generation")
    parser.add_argument("--model", help="Ollama model to use for AI content")
    parser.add_argument("--timeout", type=int, help="Timeout for AI content generation")
    parser.add_argument("--work-effort", help="Work effort to update")
    parser.add_argument("--new-status", choices=["active", "completed", "archived", "paused"], help="New status for work effort")
    parser.add_argument("--old-status", choices=["active", "completed", "archived", "paused"], help="Old status for work effort")
    parser.add_argument("--manager-name", help="Name for work effort manager")
    parser.add_argument("--target-dir", help="Target directory for work effort manager")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (minimal output)")
    parser.add_argument("command", nargs="?", help="Command to execute")
    return parser.parse_args()

def load_config() -> Dict:
    """Load configuration from the nearest config file."""
    config_file, config_data = find_nearest_config()
    if not config_file:
        return {}
    return config_data or {}

def main_entry():
    """Entry point for console_scripts"""
    return asyncio.run(main())

def find_work_efforts_dir(start_dir=None):
    """
    Find the work efforts directory by walking up the directory tree.

    Args:
        start_dir: Directory to start searching from (default: current directory)

    Returns:
        Path to the work efforts directory or None if not found
    """
    if start_dir is None:
        start_dir = os.getcwd()

    # Convert to absolute path
    start_dir = os.path.abspath(start_dir)

    # First try to find via config
    config_file, config_data = find_nearest_config(start_dir)
    if config_data and "work_managers" in config_data:
        # Get default manager if available
        default_manager = config_data.get("default_manager")
        if default_manager:
            for manager in config_data["work_managers"]:
                if manager.get("name") == default_manager:
                    work_efforts_dir = os.path.join(os.path.dirname(config_file), manager["work_efforts_dir"])
                    if os.path.exists(work_efforts_dir):
                        return work_efforts_dir

        # If no default manager or default manager not found, use first available manager
        for manager in config_data["work_managers"]:
            if "work_efforts_dir" in manager:
                work_efforts_dir = os.path.join(os.path.dirname(config_file), manager["work_efforts_dir"])
                if os.path.exists(work_efforts_dir):
                    return work_efforts_dir

    # Fall back to looking for _AI-Setup/work_efforts
    while start_dir:
        work_efforts_dir = os.path.join(start_dir, "_AI-Setup", "work_efforts")
        if os.path.exists(work_efforts_dir):
            return work_efforts_dir

        # Move up one directory
        parent_dir = os.path.dirname(start_dir)
        if parent_dir == start_dir:  # We've reached the root
            break
        start_dir = parent_dir

    return None

async def create_work_manager(args: argparse.Namespace) -> int:
    """Create a new work effort manager."""
    try:
        # Get project root
        project_root = find_project_root()
        if not project_root:
            logger.error("❌ Could not find project root")
            return 1

        # Get target directory
        target_dir = args.target_dir or os.path.join(project_root, "test_workspace")
        target_dir = os.path.abspath(target_dir)
        logger.info(f"Created target directory: {target_dir}")

        # Create manager
        manager = WorkEffortManager(project_dir=project_root, config={"work_efforts_dir": target_dir})
        manager.create_new_manager(args.manager_name, target_dir)
        logger.info(f"✅ Created work manager: {args.manager_name}")
        return 0
    except Exception as e:
        logger.error(f"Error creating work manager: {str(e)}")
        return 1

async def handle_work_effort(args: argparse.Namespace, manager: WorkEffortManager) -> int:
    """Handle work effort operations.

    Args:
        args: Command line arguments.
        manager: Work effort manager instance.

    Returns:
        Exit code.
    """
    try:
        # Get work effort details
        title = args.title
        assignee = args.assignee or "self"
        priority = args.priority or "medium"
        due_date = args.due_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        # Interactive mode
        if args.interactive and not args.yes:
            print("\nWork Effort Operations")
            print("=====================")

            # Get operation
            operations = ["create", "update", "delete", "list", "select"]
            print("\nAvailable operations:")
            for i, op in enumerate(operations, 1):
                print(f"{i}. {op}")

            while True:
                try:
                    op_input = input("\nSelect operation (number): ")
                    op_index = int(op_input) - 1
                    if 0 <= op_index < len(operations):
                        operation = operations[op_index]
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            # Handle operation
            if operation == "create":
                return await create_work_effort(args, manager)
            elif operation == "update":
                return await update_work_effort_status(args, manager)
            elif operation == "delete":
                # Get work effort to delete
                work_efforts = manager.list_work_efforts()
                if not work_efforts:
                    print("No work efforts found.")
                    return 1

                print("\nAvailable Work Efforts:")
                for i, we in enumerate(work_efforts, 1):
                    print(f"{i}. {we.get('title', 'Untitled')}")

                while True:
                    try:
                        we_input = input("\nSelect work effort to delete (number): ")
                        we_index = int(we_input) - 1
                        if 0 <= we_index < len(work_efforts):
                            selected = work_efforts[we_index]
                            confirm = input(f"\nAre you sure you want to delete '{selected.get('title')}'? [y/N]: ")
                            if confirm.lower() == 'y':
                                if manager.delete_work_effort(selected.get('id')):
                                    print("✅ Work effort deleted successfully")
                                    return 0
                                else:
                                    print("❌ Failed to delete work effort")
                                    return 1
                            else:
                                print("Operation cancelled.")
                                return 0
                        print("Invalid selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            elif operation == "list":
                list_work_efforts(manager.work_efforts_dir)
                return 0
            elif operation == "select":
                return await select_work_effort(args, manager)
        else:
            # Non-interactive mode requires title
            if not title:
                print("❌ Title is required in non-interactive mode")
                return 1

            # Default to create operation in non-interactive mode
            return await create_work_effort(args, manager)

    except Exception as e:
        logger.error(f"Error handling work effort: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main_entry())