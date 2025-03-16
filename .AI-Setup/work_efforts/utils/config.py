#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort configuration utilities.

This module provides utilities for working with configuration data.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, IO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEfforts.Utils")

def parse_json(json_str: str) -> Dict:
    """
    Parse a JSON string.

    Args:
        json_str: The JSON string to parse

    Returns:
        Dictionary parsed from the JSON
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return {}

def load_json_file(file_path: str) -> Dict:
    """
    Load JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary of JSON data
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON in {file_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Save JSON data to a file.

    Args:
        data: Dictionary of JSON data
        file_path: Path to save the JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the JSON data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON data to {file_path}")

        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False

def get_config_path(project_dir: str) -> str:
    """
    Get the path to the config file.

    Args:
        project_dir: The project directory

    Returns:
        The path to the config file
    """
    return os.path.join(project_dir, "work_efforts", "config.json")

def load_config(project_dir: str) -> Dict:
    """
    Load the configuration for a project.

    Args:
        project_dir: The project directory

    Returns:
        The configuration dictionary
    """
    config_path = get_config_path(project_dir)

    if not os.path.exists(config_path):
        # Create a default config
        default_config = {
            "version": "0.4.5",
            "work_efforts_dir": os.path.join(project_dir, "work_efforts"),
            "default_status": "active",
            "default_priority": "medium",
            "default_assignee": "self",
            "check_interval": 1.0
        }

        # Save the default config
        save_json_file(default_config, config_path)

        logger.info(f"Created default config at {config_path}")

        return default_config

    # Load the config
    config = load_json_file(config_path)

    # Ensure required keys are present
    default_keys = {
        "version": "0.4.5",
        "work_efforts_dir": os.path.join(project_dir, "work_efforts"),
        "default_status": "active",
        "default_priority": "medium",
        "default_assignee": "self",
        "check_interval": 1.0
    }

    # Add any missing keys
    for key, value in default_keys.items():
        if key not in config:
            config[key] = value

    return config

def save_config(config: Dict, project_dir: str) -> bool:
    """
    Save the configuration for a project.

    Args:
        config: The configuration dictionary
        project_dir: The project directory

    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path(project_dir)
    return save_json_file(config, config_path)

def get_config(project_dir: str, key: str, default: Any = None) -> Any:
    """
    Get a specific value from the configuration.

    Args:
        project_dir: The project directory
        key: The key to get
        default: The default value if the key is not found

    Returns:
        The value for the key, or the default if not found
    """
    config = load_config(project_dir)
    return config.get(key, default)

def set_config(project_dir: str, key: str, value: Any) -> bool:
    """
    Set a specific value in the configuration.

    Args:
        project_dir: The project directory
        key: The key to set
        value: The value to set

    Returns:
        True if successful, False otherwise
    """
    config = load_config(project_dir)
    config[key] = value
    return save_config(config, project_dir)

def merge_config(project_dir: str, new_config: Dict) -> Dict:
    """
    Merge a new configuration with the existing configuration.

    Args:
        project_dir: The project directory
        new_config: The new configuration to merge

    Returns:
        The merged configuration
    """
    config = load_config(project_dir)
    config.update(new_config)
    save_config(config, project_dir)
    return config