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
   - `code-conductor work` - Create a new work effort
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

This file contains instructions for validating the presence and operation of .AI-Setup configured
environments. It serves as a stable identifier that AI tools can recognize to confirm that a directory
contains AI-friendly configurations.

## For AI Assistants

If your AI assistant can read this file, it should:

1. Recognize that .AI-Setup is properly configured
2. Look for structure-specific information in the accompanying files
3. Use this structure to provide more contextually-relevant assistance

## For Developers

You don't need to modify this file. Its presence signals to AI tools that this directory has
been properly configured with the AI-Setup toolkit.
""")

        # Set up the work_efforts directory within .AI-Setup
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

        # Create a temporary .AI-Setup in the current directory
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

            # Create .AI-Setup in target directory
            target_setup = os.path.join(directory, ".AI-Setup")
            if not os.path.exists(target_setup):
                os.makedirs(target_setup)
                print(f"✅ Created AI-Setup directory in: {directory}")

            # Track how many files were copied
            copied_files = 0
            existing_files = 0

            # Copy all files from temporary .AI-Setup to target
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

        # Clean up temporary .AI-Setup if it was created for this operation
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
    If in_ai_setup is True, create within the .AI-Setup folder

    Returns a tuple of (work_efforts_dir, template_path, active_dir, completed_dir, archived_path)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Define the work_efforts directory and its subdirectories
    if in_ai_setup:
        # Create inside .AI-Setup folder
        ai_setup_dir = os.path.join(base_dir, ".AI-Setup")
        if not os.path.exists(ai_setup_dir):
            if create_dirs:
                os.makedirs(ai_setup_dir)
                print(f"Created .AI-Setup directory: {ai_setup_dir}")
            else:
                print(f"Warning: .AI-Setup directory does not exist at {ai_setup_dir}")

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
code-conductor work
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
    else:
        # Template already exists, no need to create it
        pass

    return template_path

def validate_priority(priority):
    """Validate that priority is one of the allowed values"""
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority.lower() not in valid_priorities:
        print(f"Warning: '{priority}' is not a recognized priority level. Using 'medium' instead.")
        return "medium"
    return priority.lower()

def validate_date(date_str):
    """Validate the date format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Warning: Invalid date format. Using today's date ({today}) instead.")
        return today

def load_config():
    """
    Load the configuration from the .AI-Setup/config.json file if it exists.
    Returns a dictionary with the configuration or an empty dict if the file doesn't exist.
    """
    config_path = os.path.join(os.getcwd(), ".AI-Setup", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    return {}

def setup_work_effort_manager_path():
    """
    Set up the Python path to include the work_efforts/scripts directory
    so that the work_effort_manager module can be imported properly.
    """
    try:
        # Add the work_efforts/scripts directory to the Python path
        scripts_dir = os.path.join(os.getcwd(), "work_efforts", "scripts")
        if os.path.exists(scripts_dir) and scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
            return True
        return False
    except Exception as e:
        print(f"Warning: Could not set up WorkEffortManager path: {e}")
        return False

def create_work_effort(title, assignee, priority, due_date, template_path, target_dir, content=None, create_in_root=False):
    """
    Create a new work effort file

    If create_in_root is True, create the file in the parent directory of target_dir
    If content is provided, use it to populate the objectives, tasks, and notes
    """
    # Check if the work_managers field exists in config
    config = load_config()
    use_manager = "work_managers" in config and config["work_managers"]

    try:
        # Set up the Python path for the work effort manager and import it directly
        # This ensures we use the centralized implementation
        setup_work_effort_manager_path()

        try:
            from work_effort_manager import WorkEffortManager

            # Initialize a standalone manager
            base_dir = os.path.dirname(target_dir) if create_in_root else target_dir
            manager = WorkEffortManager(project_dir=os.path.dirname(base_dir))

            # Create the work effort using the manager
            work_effort_path = manager.create_work_effort(
                title=title,
                assignee=assignee,
                priority=priority,
                due_date=due_date,
                content=content or {}
            )

            if work_effort_path:
                print(f"🚀 New work effort created at: {work_effort_path}")
                return work_effort_path
            else:
                # Fall back to the direct implementation if manager fails
                print("WorkEffortManager failed, falling back to direct implementation.")
        except ImportError:
            print("Could not import WorkEffortManager, using direct implementation.")

        # Fall back to the direct implementation if WorkEffortManager can't be imported
        # This is the legacy path and should rarely be used
        # Validate inputs
        priority = validate_priority(priority)
        due_date = validate_date(due_date)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        filename_timestamp = datetime.now().strftime("%Y%m%d%H%M")

        # Generate a safe filename
        safe_title = ''.join(c if c.isalnum() or c == ' ' else '_' for c in title)
        safe_title_slug = safe_title.lower().replace(' ', '_')

        # Create a folder for the work effort
        folder_name = f"{filename_timestamp}_{safe_title_slug}"
        md_filename = f"{filename_timestamp}_{safe_title_slug}.md"

        # Determine the target folder path
        folder_path = os.path.join(target_dir, folder_name) if not create_in_root else os.path.join(os.path.dirname(target_dir), folder_name)
        file_path = os.path.join(folder_path, md_filename)

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Read template file
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        # Replace template variables
        filled_content = template_content.replace("{{title}}", title)
        filled_content = filled_content.replace("{{status}}", "active")
        filled_content = filled_content.replace("{{priority}}", priority)
        filled_content = filled_content.replace("{{assignee}}", assignee)
        filled_content = filled_content.replace("{{created}}", timestamp)
        filled_content = filled_content.replace("{{last_updated}}", timestamp)
        filled_content = filled_content.replace("{{due_date}}", due_date)

        # If AI-generated content is provided, replace the placeholders
        if content and isinstance(content, dict):
            if "objectives" in content:
                filled_content = filled_content.replace("- Clearly define goals for this work effort.", content["objectives"])
            if "tasks" in content:
                filled_content = filled_content.replace("- [ ] Task 1\n- [ ] Task 2", content["tasks"])
            if "notes" in content:
                filled_content = filled_content.replace("- Context, links to relevant code, designs, references.", content["notes"])

        # Write new file
        with open(file_path, "w") as new_file:
            new_file.write(filled_content)

        print(f"🚀 New work effort created at: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error creating work effort: {str(e)}")
        return None

async def setup_selected_directories():
    """Use the interactive directory scanner to select and set up directories"""
    current_dir = os.getcwd()
    print(f"\n📍 Current directory: {current_dir}")
    print("Select directories to set up with AI-Setup:")

    # Use the interactive directory scanner
    selected_dirs = select_directories(current_dir)

    if not selected_dirs:
        print("No directories selected for setup.")
        return 1

    # Set up work efforts in each selected directory
    for directory in selected_dirs:
        dir_name = os.path.basename(directory)
        print(f"\n🔄 Setting up {dir_name}...")

        # Create work efforts structure
        work_efforts_dir, template_path, active_dir, _, _ = setup_work_efforts_structure(directory)
        create_template_if_missing(template_path)

        # Create default work effort
        create_work_effort(
            title="Getting Started",
            assignee="self",
            priority="medium",
            due_date=datetime.now().strftime("%Y-%m-%d"),
            template_path=template_path,
            target_dir=active_dir
        )

        # Install AI-Setup in the directory
        install_ai_setup([directory])

    print("\n✅ Setup completed for all selected directories")
    return 0

async def setup_ai_in_current_dir():
    """Set up AI and work efforts in the current directory"""
    current_dir = os.getcwd()
    print(f"\n📍 Checking current directory: {current_dir}")

    # Check if .AI-Setup already exists
    ai_setup_dir = os.path.join(current_dir, ".AI-Setup")
    ai_setup_exists = os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir)

    # Check if config.json exists
    config_file = os.path.join(ai_setup_dir, "config.json") if ai_setup_exists else None
    config_exists = config_file and os.path.exists(config_file) and os.path.isfile(config_file)

    # Check if work_efforts already exists inside .AI-Setup
    ai_setup_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts") if ai_setup_exists else None
    ai_setup_work_efforts_exists = ai_setup_work_efforts_dir and os.path.exists(ai_setup_work_efforts_dir) and os.path.isdir(ai_setup_work_efforts_dir)

    # Check if scripts directory exists and has required files
    scripts_dir = os.path.join(ai_setup_work_efforts_dir, "scripts") if ai_setup_work_efforts_exists else None
    scripts_exist = False
    all_scripts_present = False
    missing_scripts = []

    if scripts_dir and os.path.exists(scripts_dir):
        required_scripts = ["work_effort_manager.py", "run_work_effort_manager.py",
                           "ai_work_effort_creator.py", "new_work_effort.py"]
        existing_scripts = [script for script in required_scripts
                           if os.path.exists(os.path.join(scripts_dir, script))]
        scripts_exist = len(existing_scripts) > 0
        all_scripts_present = len(existing_scripts) == len(required_scripts)
        missing_scripts = [script for script in required_scripts if script not in existing_scripts]

    # Print status of existing components
    print("\n🔍 Checking for existing components:")
    print(f"- .AI-Setup folder: {'✅ Exists' if ai_setup_exists else '❌ Not found'}")
    if ai_setup_exists:
        print(f"- Configuration file: {'✅ Exists' if config_exists else '❌ Not found'}")
        print(f"- .AI-Setup/work_efforts folder: {'✅ Exists' if ai_setup_work_efforts_exists else '❌ Not found'}")
        if ai_setup_work_efforts_exists:
            if scripts_exist:
                if all_scripts_present:
                    print(f"- Required scripts: ✅ All present")
                else:
                    print(f"- Required scripts: ⚠️ Partially present ({len(existing_scripts)}/{len(required_scripts)})")
                    for script in missing_scripts:
                        print(f"  - ❌ Missing: {script}")
            else:
                print(f"- Required scripts: ❌ None found")

    # If all exist and all scripts are present, inform the user and exit
    if ai_setup_exists and config_exists and ai_setup_work_efforts_exists and all_scripts_present:
        print("\n✅ AI-Setup is already completely installed in this directory")
        print("\nNo changes will be made to existing components.")
        print("\nYou can use the following commands:")
        print("  code-conductor work      - Create a new work effort in .AI-Setup/work_efforts")
        print("  cc-work-e                - Shorthand to create a work effort")
        print("  code-conductor list      - List existing work efforts")
        print("  code-conductor list-managers      - List all work effort managers in the project")
        print("  code-conductor update-status      - Update the status of a work effort")
        print("  code-conductor select             - Select directories to set up AI assistance")
        print("  code-conductor help               - Show this help text")
        print("  code-conductor version            - Show the version number")
        print("\nOptions for work_effort/work command:")
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
        print("\nShorthand Command:")
        print("  cc-work-e                            - Quick create work effort in .AI-Setup/work_efforts")
        print("  cc-work-e -i                         - Create a work effort with interactive prompt")
        print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
        print("  cc-work-e --manager NAME             - Use a specific work effort manager")
        print("\nFor more information, visit: https://github.com/ctavolazzi/code-conductor")
        return 0

    # Report what will be installed and what will be preserved
    print("\n📦 Installation plan:")

    if ai_setup_exists:
        print(f"- ⚠️ Existing .AI-Setup folder will be preserved at: {ai_setup_dir}")
        if not config_exists:
            print(f"- 🆕 Will create configuration file at: {os.path.join(ai_setup_dir, 'config.json')}")
        if ai_setup_work_efforts_exists:
            print(f"- ⚠️ Existing .AI-Setup/work_efforts folder will be preserved")
            if scripts_exist and not all_scripts_present:
                print(f"- 🆕 Will install {len(missing_scripts)} missing work effort manager scripts:")
                for script in missing_scripts:
                    print(f"  - {script}")
            elif not scripts_exist:
                print(f"- 🆕 Will install all required work effort manager scripts")
        else:
            print(f"- 🆕 Will create work_efforts folder inside .AI-Setup")
    else:
        print(f"- 🆕 Will create .AI-Setup folder at: {ai_setup_dir}")
        print(f"- 🆕 Will create configuration file")
        print(f"- 🆕 Will create work_efforts folder and install required scripts")

    # Get confirmation before proceeding
    confirmation = input("\nProceed with installation? (y/n): ")
    if confirmation.lower() not in ['y', 'yes']:
        print("\n❌ Setup cancelled by user")
        return 1

    print("\n📦 Installing components...")

    # Create or update the config file first
    config_file, config_data = create_or_update_config(current_dir)
    if config_file:
        print(f"✅ Configuration file created/updated at: {config_file}")
    else:
        print(f"⚠️ Failed to create/update configuration file")

    # Create the AI-Setup folder if needed (though create_or_update_config should have done this)
    if not ai_setup_exists:
        try:
            # AI-Setup folder should already be created by create_or_update_config
            if not os.path.exists(ai_setup_dir):
                os.makedirs(ai_setup_dir)
            print(f"✅ AI-Setup folder created at: {ai_setup_dir}")

            # Ensure the work_efforts folder was created inside .AI-Setup
            ai_setup_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
            if not os.path.exists(ai_setup_work_efforts_dir):
                _, template_path, active_dir, _, _ = setup_work_efforts_structure(current_dir, in_ai_setup=True)
                create_template_if_missing(template_path)

                # Create a default work effort in the active directory
                file_path = create_work_effort(
                    title="Getting Started",
                    assignee="self",
                    priority="medium",
                    due_date=datetime.now().strftime("%Y-%m-%d"),
                    template_path=template_path,
                    target_dir=active_dir
                )

                print(f"✅ Work efforts directory created inside .AI-Setup folder")
                if file_path:
                    print(f"✅ Default work effort created at: {file_path}")
        except Exception as e:
            print(f"⚠️ AI setup encountered an issue: {str(e)}")
    else:
        print(f"⚠️ Using existing AI-Setup folder at: {ai_setup_dir}")
        print(f"  No changes made to existing files in this directory")

        # If .AI-Setup exists but doesn't have work_efforts, create it
        if not ai_setup_work_efforts_exists:
            _, template_path, active_dir, _, _ = setup_work_efforts_structure(current_dir, in_ai_setup=True)
            create_template_if_missing(template_path)

            # Create a default work effort in the active directory
            file_path = create_work_effort(
                title="Getting Started",
                assignee="self",
                priority="medium",
                due_date=datetime.now().strftime("%Y-%m-%d"),
                template_path=template_path,
                target_dir=active_dir
            )

            print(f"✅ Work efforts directory created inside .AI-Setup folder")
            if file_path:
                print(f"✅ Default work effort created at: {file_path}")
        else:
            print(f"⚠️ Using existing .AI-Setup/work_efforts directory")

            # If scripts are missing or partially present, run setup_work_efforts_structure
            # to copy the missing scripts
            if not all_scripts_present:
                print(f"Installing missing work effort manager scripts...")
                # Just run setup_work_efforts_structure again - it will skip existing files
                # but try to copy missing scripts
                setup_work_efforts_structure(current_dir, in_ai_setup=True)

                # Check if scripts were successfully copied
                scripts_dir = os.path.join(ai_setup_work_efforts_dir, "scripts")
                if not os.path.exists(scripts_dir):
                    os.makedirs(scripts_dir)
                    print(f"✅ Created scripts directory at: {scripts_dir}")

                # Create the __init__.py file if it's missing
                init_path = os.path.join(scripts_dir, "__init__.py")
                if not os.path.exists(init_path):
                    with open(init_path, "w") as f:
                        f.write("# Work Efforts Scripts\n")
                    print(f"✅ Created __init__.py at: {init_path}")

                # Verify which scripts were successfully installed
                required_scripts = ["work_effort_manager.py", "run_work_effort_manager.py",
                                   "ai_work_effort_creator.py", "new_work_effort.py"]
                installed_scripts = [script for script in required_scripts
                                    if os.path.exists(os.path.join(scripts_dir, script))]

                if len(installed_scripts) == len(required_scripts):
                    print(f"✅ All work effort manager scripts were successfully installed")
                else:
                    print(f"⚠️ Installed {len(installed_scripts)}/{len(required_scripts)} scripts")
                    missing_after = [script for script in required_scripts if script not in installed_scripts]
                    for script in missing_after:
                        print(f"  - ❌ Still missing: {script}")
            else:
                print(f"  No changes needed to scripts directory - all scripts are present")

    print(f"\n✅ Setup completed in: {current_dir}")
    print(f"  Configuration file: {config_file}")
    print("\nYou can now use the following commands:")
    print("  code-conductor work      - Create a new work effort in .AI-Setup/work_efforts")
    print("  cc-work-e                - Shorthand to create a work effort")
    print("  code-conductor list      - List existing work efforts")
    print("  code-conductor list-managers      - List all work effort managers in the project")
    print("  code-conductor update-status      - Update the status of a work effort")
    print("  code-conductor select             - Select directories to set up AI assistance")
    print("\nEnhanced Work Effort Creator:")
    print("  cc-work-e                            - Quick create work effort in .AI-Setup/work_efforts")
    print("  cc-work-e -i                         - Create a work effort with interactive prompt")
    print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
    print("\nFor all available options, run: code-conductor help")

    return 0

async def interactive_mode(template_path, active_dir, manager_info=None):
    """Get user input with defaults to create a work effort"""
    print("\n📝 Create a New Work Effort")
    print("=========================")

    # If using a specific manager, mention it
    if manager_info:
        print(f"Creating in manager: {manager_info.get('name', 'Default')}")

    print("A work effort is a task or project you want to track with objectives, tasks, and notes.")
    print("You can create a new work effort by filling in the details below.")
    print("Press Enter to accept the default values shown in brackets.\n")

    # Get user input with defaults
    title_input = input("Title (name of your work effort) [Untitled]: ")
    title = title_input if title_input.strip() else "Untitled"

    assignee_input = input("Assignee (who is responsible) [self]: ")
    assignee = assignee_input if assignee_input.strip() else "self"

    print("\nPriority levels:")
    print("  low      - Can be done when time permits")
    print("  medium   - Important but not urgent")
    print("  high     - Urgent and should be done soon")
    print("  critical - Requires immediate attention")
    priority_input = input("Priority [medium]: ")
    priority = priority_input if priority_input.strip() else "medium"

    # Validate priority input
    while priority.lower() not in ["low", "medium", "high", "critical"]:
        print("Invalid priority. Please choose from: low, medium, high, critical")
        priority_input = input("Priority [medium]: ")
        priority = priority_input if priority_input.strip() else "medium"

    # Default to today's date
    today = datetime.now().strftime("%Y-%m-%d")
    due_date_input = input(f"Due date (YYYY-MM-DD) [{today}]: ")
    due_date = due_date_input if due_date_input.strip() else today

    # Validate date format
    while not validate_date(due_date):
        print("Invalid date format. Please use YYYY-MM-DD format.")
        due_date_input = input(f"Due date (YYYY-MM-DD) [{today}]: ")
        due_date = due_date_input if due_date_input.strip() else today

    # Ask about using AI to generate content
    use_ai_input = input("Use AI to generate content (y/n)? [n]: ")
    use_ai = use_ai_input.lower() == 'y'

    content = None
    if use_ai:
        description_input = input("Enter a description of the work effort: ")
        if description_input.strip():
            print("Generating content with AI...")
            try:
                model_input = input("Which Ollama model would you like to use? [phi3]: ")
                model = model_input.strip() if model_input.strip() else "phi3"

                content = await generate_content_with_ollama(description_input, model)
            except Exception as e:
                print(f"Error generating content: {str(e)}")
                print("Continuing without AI-generated content.")

    # Create the work effort file
    create_work_effort(title, assignee, priority, due_date, template_path, active_dir, content)

async def non_interactive_mode(args, template_path, active_dir, manager_info=None):
    """Create a work effort without user interaction using command-line arguments"""
    # If using a specific manager, mention it if verbose
    if manager_info:
        print(f"Creating in manager: {manager_info.get('name', 'Default')}")

    # Use provided arguments or defaults
    title = args.title if args.title else "Untitled"
    assignee = args.assignee if args.assignee else "self"
    priority = args.priority if args.priority else "medium"

    # Default to today's date if not provided
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = args.due_date if args.due_date else today

    # Validate inputs
    if priority.lower() not in ["low", "medium", "high", "critical"]:
        print(f"Invalid priority: {priority}. Using default: medium")
        priority = "medium"

    if not validate_date(due_date):
        print(f"Invalid date format: {due_date}. Using today's date: {today}")
        due_date = today

    # Generate content with AI if requested
    content = None
    if args.use_ai and args.description:
        print("Generating content with AI...")
        try:
            model = args.model if args.model else "phi3"
            timeout = args.timeout if args.timeout else 30
            content = await generate_content_with_ollama(args.description, model)
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            print("Continuing without AI-generated content.")

    # Create the work effort file
    return create_work_effort(title, assignee, priority, due_date, template_path, active_dir, content)

def list_work_efforts(work_efforts_dir):
    """List all work efforts in the work_efforts directory"""
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")

    print("\n📋 Work Efforts:")

    # Check if work_efforts directory exists
    if not os.path.exists(work_efforts_dir):
        print("❌ Work efforts directory not found. Run 'python cli.py' to set up.")
        return

    # List active work efforts
    print("\nActive Work Efforts:")
    if os.path.exists(active_dir):
        # First, check for direct .md files
        active_files = [f for f in os.listdir(active_dir) if f.endswith(".md")]

        # Second, check for work effort folders (containing .md files)
        active_folders = [d for d in os.listdir(active_dir) if os.path.isdir(os.path.join(active_dir, d))]

        if active_files or active_folders:
            # List direct .md files
            for file in sorted(active_files):
                print(f"  - {file}")

            # List .md files within folders
            for folder in sorted(active_folders):
                folder_path = os.path.join(active_dir, folder)
                folder_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
                for file in sorted(folder_files):
                    print(f"  - {folder}/{file}")
        else:
            print("  No active work efforts found.")
    else:
        print("  Active directory not found.")

    # List completed work efforts
    print("\nCompleted Work Efforts:")
    if os.path.exists(completed_dir):
        # First, check for direct .md files
        completed_files = [f for f in os.listdir(completed_dir) if f.endswith(".md")]

        # Second, check for work effort folders (containing .md files)
        completed_folders = [d for d in os.listdir(completed_dir) if os.path.isdir(os.path.join(completed_dir, d))]

        if completed_files or completed_folders:
            # List direct .md files
            for file in sorted(completed_files):
                print(f"  - {file}")

            # List .md files within folders
            for folder in sorted(completed_folders):
                folder_path = os.path.join(completed_dir, folder)
                folder_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
                for file in sorted(folder_files):
                    print(f"  - {folder}/{file}")
        else:
            print("  No completed work efforts found.")
    else:
        print("  Completed directory not found.")

    # List archived work efforts
    print("\nArchived Work Efforts:")
    if os.path.exists(archived_dir):
        # First, check for direct .md files
        archived_files = [f for f in os.listdir(archived_dir) if f.endswith(".md")]

        # Second, check for work effort folders (containing .md files)
        archived_folders = [d for d in os.listdir(archived_dir) if os.path.isdir(os.path.join(archived_dir, d))]

        if archived_files or archived_folders:
            # List direct .md files
            for file in sorted(archived_files):
                print(f"  - {file}")

            # List .md files within folders
            for folder in sorted(archived_folders):
                folder_path = os.path.join(archived_dir, folder)
                folder_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
                for file in sorted(folder_files):
                    print(f"  - {folder}/{file}")
        else:
            print("  No archived work efforts found.")
    else:
        print("  Archived directory not found.")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Code Conductor - AI Development Environment Setup Tool")
    parser.add_argument("-v", "--version", action="store_true", help="Show version number")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("-y", "--yes", action="store_true", help="Answer yes to all prompts (non-interactive mode)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress verbose output about directory searching")

    # Work effort options
    parser.add_argument("--title", help="Title of the work effort (default: Untitled)")
    parser.add_argument("--assignee", help="Assignee of the work effort (default: self)")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"],
                       help="Priority of the work effort (low, medium, high, critical)")
    parser.add_argument("--due-date", help="Due date of the work effort (YYYY-MM-DD)")

    # AI content generation options
    parser.add_argument("--use-ai", action="store_true", help="Use AI to generate content")
    parser.add_argument("--description", help="Description to use for AI content generation")
    parser.add_argument("--model", help="Ollama model to use for AI content (default: phi3)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Timeout in seconds for AI content generation (default: 30)")

    # Work effort manager options
    parser.add_argument("--manager", help="Name of the work effort manager to use")
    parser.add_argument("--manager-name", help="Name for a new work effort manager")
    parser.add_argument("--target-dir", help="Target directory for a new work effort manager")

    # Command argument
    parser.add_argument("command", nargs="?",
                       help="Command to run (setup, new-work-manager, set-default, work, list, list-managers, select)")

    return parser.parse_args()

async def main():
    """Main function"""
    args = parse_arguments()

    # Load configuration if available
    config = load_config()

    # Set up the Python path for the work effort manager
    setup_work_effort_manager_path()

    # If there's a config with work_managers.auto_start set to true, and the manager script is specified,
    # start the WorkEffortManager in the background
    if (args.command == "work" or args.interactive) and "work_managers" in config and \
       config["work_managers"] and \
       config["work_managers"][0].get("use_manager", False) and \
       config["work_managers"][0].get("auto_start", False) and \
       config["work_managers"][0].get("runner_script"):
        try:
            import subprocess
            runner_script = config["work_managers"][0].get("runner_script")
            subprocess.Popen(["python", runner_script, "--no-auto-start"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             start_new_session=True)
            print("Started WorkEffortManager in the background.")
        except Exception as e:
            print(f"Warning: Could not start WorkEffortManager: {e}")

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
            print("  code-conductor setup              - Set up AI assistance in the current directory")
            print("  code-conductor new-work-manager   - Create a new work effort manager in a directory")
            print("  code-conductor set-default        - Set the default work effort manager")
            print("  code-conductor work_effort        - Create a new work effort in .AI-Setup/work_efforts")
            print("  code-conductor work               - Shorthand for work_effort")
            print("  code-conductor work_effort -i     - Create a new work effort interactively")
            print("  code-conductor list               - List existing work efforts")
            print("  code-conductor list-managers      - List all work effort managers in the project")
            print("  code-conductor update-status      - Update the status of a work effort")
            print("  code-conductor select             - Select directories to set up AI assistance")
            print("  code-conductor help               - Show this help text")
            print("  code-conductor version            - Show the version number")
            print("\nOptions for work_effort/work command:")
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
            print("\nShorthand Command:")
            print("  cc-work-e                            - Quick create work effort in .AI-Setup/work_efforts")
            print("  cc-work-e -i                         - Create a work effort with interactive prompt")
            print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
            print("  cc-work-e --manager NAME             - Use a specific work effort manager")
            print("\nFor more information, visit: https://github.com/ctavolazzi/code-conductor")
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
                print(f"  code-conductor work --manager {manager_name or os.path.basename(target_dir)}")
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

        elif args.command.lower() in ['work_effort', 'work', 'create']:
            # Check for work_efforts directory using the appropriate manager
            manager_name = args.manager if hasattr(args, 'manager') and args.manager else None

            # Use verbose mode when searching for work efforts
            verbose = not args.quiet if hasattr(args, 'quiet') else True
            work_efforts_dir, manager_info = find_work_efforts_directory(manager_name, verbose=verbose)

            if not work_efforts_dir:
                current_dir = os.getcwd()
                potential_location = os.path.join(current_dir, ".AI-Setup", "work_efforts")

                print(f"\n📋 Work Effort Management")
                print("======================")
                print(f"❌ No work effort folder found in the current directory: {current_dir}")

                if manager_name:
                    print(f"⚠️ Manager '{manager_name}' not found")

                # If in non-interactive mode, automatically set up
                if args.yes:
                    print(f"Creating work effort folder at: {potential_location}")
                    await setup_ai_in_current_dir()
                    # After setup, try to find the directory again
                    work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                    if not work_efforts_dir:
                        print("❌ Setup failed to create work efforts directory")
                        return 1
                else:
                    print(f"Work effort folder destination: {potential_location}")
                    setup_first = input("Would you like me to create one? (y/n): ")
                    if setup_first.lower() == 'y':
                        await setup_ai_in_current_dir()
                        # After setup, try to find the directory again
                        work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                        if not work_efforts_dir:
                            print("❌ Setup failed to create work efforts directory")
                            return 1
                    else:
                        return 1
            else:
                print(f"✅ Found work efforts directory at: {work_efforts_dir}")

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

            # Run in appropriate mode based on args
            if args.yes:
                # Run in non-interactive mode
                work_effort_path = await non_interactive_mode(args, template_path, active_dir, manager_info)
                if work_effort_path:
                    print(f"✅ Work effort created successfully at: {work_effort_path}")
                else:
                    print("❌ Failed to create work effort")
                    return 1
            else:
                # Run in interactive mode
                await interactive_mode(template_path, active_dir, manager_info)

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

                setup_first = input("Would you like me to create a work effort folder? (y/n): ")
                if setup_first.lower() == 'y':
                    await setup_ai_in_current_dir()
                    work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                    if not work_efforts_dir:
                        print("❌ Setup failed to create work efforts directory")
                        return 1
                else:
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

            setup_first = input("Would you like to set up work efforts in the current directory? (y/n): ")
            if setup_first.lower() == 'y':
                await setup_ai_in_current_dir()
                # After setup, try to find the directory again
                work_efforts_dir, manager_info = find_work_efforts_directory(manager_name)
                if not work_efforts_dir:
                    print("❌ Setup failed to create work efforts directory")
                    return 1
            else:
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

        # Run in appropriate mode based on args
        if args.yes:
            # Run in non-interactive mode
            work_effort_path = await non_interactive_mode(args, template_path, active_dir, manager_info)
            if work_effort_path:
                print(f"✅ Work effort created successfully at: {work_effort_path}")
            else:
                print("❌ Failed to create work effort")
            return 1
        else:
            # Run in interactive mode
            await interactive_mode(template_path, active_dir, manager_info)

        return 0

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
    print("  code-conductor work                  - Create a new work effort in .AI-Setup/work_efforts")
    print("  code-conductor work_effort -i        - Create a new work effort interactively")
    print("  code-conductor list                  - List existing work efforts")
    print("  code-conductor update-status         - Update the status of a work effort")
    print("  code-conductor select                - Select directories to set up AI assistance")
    print("\nEnhanced Work Effort Creator:")
    print("  cc-work-e                            - Quick create work effort in .AI-Setup/work_efforts")
    print("  cc-work-e -i                         - Create a work effort with interactive prompt")
    print("  cc-work-e --use-ai --description TEXT - Generate content with AI")
    print("\nFor all available options, run: code-conductor help")