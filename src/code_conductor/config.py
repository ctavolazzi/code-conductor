#!/usr/bin/env python3
"""
Config module for code_conductor package.

This module provides compatibility for tests by implementing basic JSON config handling.
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

# Version used in config files
VERSION = "0.4.6"

def parse_json(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string into a Python dictionary.

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed JSON data as a dictionary, or empty dict on error
    """
    if not json_str:
        return {}

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {str(e)}")
        return {}

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dict containing the parsed JSON data, or empty dict if file doesn't exist or has invalid JSON
    """
    if not os.path.exists(file_path):
        logging.warning(f"JSON file not found: {file_path}")
        return {}

    try:
        with open(file_path, 'r') as f:
            json_data = f.read()
        return parse_json(json_data)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Save JSON data to a file.

    Args:
        file_path (str): Path to the file to save
        data: Data to save (must be JSON serializable)

    Returns:
        bool: True if the save was successful, False otherwise
    """
    try:
        if not file_path:
            logging.error("No file path provided for JSON save")
            return False

        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
        return False

def create_or_update_config(base_dir: str, config_data: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Create a new config file or update an existing one.

    Args:
        base_dir: Base directory for the config
        config_data: Configuration data to update (optional)

    Returns:
        Tuple containing (config_file_path, config_data)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Define the path for the config file
    ai_setup_dir = os.path.join(base_dir, "_AI-Setup")
    os.makedirs(ai_setup_dir, exist_ok=True)
    config_file = os.path.join(ai_setup_dir, "config.json")

    # Default configuration
    default_config = {
        "version": VERSION,
        "project_root": base_dir,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "work_efforts": {
            "location": "in_ai_setup",
            "directories": {
                "active": os.path.join("work_efforts", "active"),
                "completed": os.path.join("work_efforts", "completed"),
                "archived": os.path.join("work_efforts", "archived"),
                "templates": os.path.join("work_efforts", "templates")
            },
            "use_manager": True
        }
    }

    # Read existing config if it exists
    existing_config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
                logging.info(f"Read existing config from: {config_file}")
        except json.JSONDecodeError:
            logging.warning(f"Config file exists but is not valid JSON: {config_file}")
        except Exception as e:
            logging.warning(f"Error reading config file: {str(e)}")

    # Merge configurations (existing and defaults, updated with new data)
    merged_config = default_config.copy()

    # Apply existing config over defaults
    for key, value in existing_config.items():
        if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
            # Deep merge dictionaries
            for subkey, subvalue in value.items():
                merged_config[key][subkey] = subvalue
        else:
            merged_config[key] = value

    # Apply new config data over existing
    if config_data:
        for key, value in config_data.items():
            if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                # Deep merge dictionaries
                for subkey, subvalue in value.items():
                    merged_config[key][subkey] = subvalue
            else:
                merged_config[key] = value

    # Update timestamp
    merged_config["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save the config
    try:
        with open(config_file, 'w') as f:
            json.dump(merged_config, f, indent=2)
            logging.info(f"Saved config to: {config_file}")
    except Exception as e:
        logging.error(f"Error saving config file: {str(e)}")

    return config_file, merged_config

def find_nearest_config(start_dir: Optional[str] = None) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Find the nearest config.json file in parent directories.

    Args:
        start_dir: Starting directory (default: current directory)

    Returns:
        Tuple of (config_file_path, config_data) or (None, {}) if not found
    """
    if start_dir is None:
        start_dir = os.getcwd()

    current_dir = os.path.abspath(start_dir)

    # Start from the current directory and go up
    while current_dir:
        ai_setup_dir = os.path.join(current_dir, "_AI-Setup")
        config_file = os.path.join(ai_setup_dir, "config.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                return config_file, config_data
            except Exception as e:
                logging.warning(f"Found config file at {config_file} but could not read it: {str(e)}")

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root directory
            break
        current_dir = parent_dir

    return None, {}

def find_work_efforts_directory(start_dir: Optional[str] = None) -> Tuple[str, bool]:
    """
    Find the work_efforts directory based on configuration or defaults.

    Args:
        start_dir: Starting directory to search from (default: current directory)

    Returns:
        Tuple of (work_efforts_dir, in_ai_setup) where in_ai_setup is a boolean
        indicating if the work_efforts directory is inside _AI-Setup
    """
    if start_dir is None:
        start_dir = os.getcwd()

    # First try to find config
    config_file, config_data = find_nearest_config(start_dir)

    if config_file:
        # Get the project root directory (parent of _AI-Setup)
        project_root = os.path.dirname(os.path.dirname(config_file))

        # Check location preference in config
        location = config_data.get("work_efforts", {}).get("location", "in_ai_setup")

        if location == "in_root":
            # Work efforts are at project root level
            work_efforts_dir = os.path.join(project_root, "work_efforts")
            return work_efforts_dir, False
        else:
            # Work efforts are in _AI-Setup (default)
            ai_setup_dir = os.path.join(project_root, "_AI-Setup")
            work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
            return work_efforts_dir, True

    # If no config found, default to _AI-Setup/work_efforts in the start directory
    ai_setup_dir = os.path.join(start_dir, "_AI-Setup")
    work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
    return work_efforts_dir, True