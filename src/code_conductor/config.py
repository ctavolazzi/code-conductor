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

    # First check if there's an existing config file in the base directory
    config_file = os.path.join(base_dir, "config.json")
    if os.path.exists(config_file):
        logging.info(f"Found existing config file at: {config_file}")
    else:
        # If no config file exists, create it in _AI-Setup directory
        if os.path.basename(base_dir) == "_AI-Setup":
            ai_setup_dir = base_dir
        else:
            ai_setup_dir = os.path.join(base_dir, "_AI-Setup")

        os.makedirs(ai_setup_dir, exist_ok=True)
        config_file = os.path.join(ai_setup_dir, "config.json")

    # Default configuration
    default_config = {
        "version": VERSION,
        "project_root": os.path.dirname(os.path.dirname(config_file)),  # Use parent of config file's directory as project root
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
            logging.info(f"Wrote config to: {config_file}")
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

    # First try to find a .code-conductor manifest file
    while current_dir:
        manifest_file = os.path.join(current_dir, ".code-conductor")
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                    logging.info(f"Found project manifest file at: {manifest_file}")

                    # If the manifest has a setup_path, use it to find the config.json
                    if "setup_path" in manifest_data:
                        setup_path = os.path.join(current_dir, manifest_data["setup_path"])
                        config_file = os.path.join(setup_path, "config.json")
                        if os.path.exists(config_file):
                            try:
                                with open(config_file, 'r') as f:
                                    config_data = json.load(f)
                                    logging.info(f"Found config file via manifest at: {config_file}")
                                    return config_file, config_data
                            except Exception as e:
                                logging.warning(f"Error reading config file referenced in manifest: {str(e)}")
            except Exception as e:
                logging.warning(f"Error reading manifest file: {str(e)}")

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root directory
            break
        current_dir = parent_dir

    # If no manifest found or it didn't lead to a valid config, fall back to looking for _AI-Setup/config.json
    current_dir = os.path.abspath(start_dir)
    while current_dir:
        ai_setup_dir = os.path.join(current_dir, "_AI-Setup")
        config_file = os.path.join(ai_setup_dir, "config.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    logging.info(f"Found config file at: {config_file}")
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

class Config:
    """
    Configuration class for the code conductor.
    This class provides a simple interface for managing configuration data.
    """
    def __init__(self, project_dir=None):
        """
        Initialize a new configuration object.

        Args:
            project_dir: The project directory (default: current directory)
        """
        self.project_dir = project_dir or os.getcwd()
        self.config_file, self.config_data = find_nearest_config(self.project_dir)

        if not self.config_file:
            # Create a new config file if none exists
            self.config_file, self.config_data = create_or_update_config(self.project_dir)

    def get(self, key, default=None):
        """
        Get a configuration value.

        Args:
            key: The key to get
            default: The default value to return if the key doesn't exist

        Returns:
            The value for the given key, or the default
        """
        return self.config_data.get(key, default)

    def set(self, key, value):
        """
        Set a configuration value.

        Args:
            key: The key to set
            value: The value to set

        Returns:
            True if the value was set, False otherwise
        """
        self.config_data[key] = value
        return save_json_file(self.config_file, self.config_data)

    def get_work_efforts_dir(self):
        """
        Get the work efforts directory.

        Returns:
            The path to the work efforts directory
        """
        work_efforts_dir, _ = find_work_efforts_directory(self.project_dir)
        return work_efforts_dir