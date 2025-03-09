#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to instantiate and run the WorkEffortManager.

This script creates an instance of the WorkEffortManager class and starts its event loop.
It can be used to centralize operations across the project that the user is working in.

Usage:
    python run_work_effort_manager.py [options]

Options:
    --project-dir DIR     Specify the project directory (default: current directory)
    --config FILE         Specify a configuration file
    --config-json JSON    Specify configuration as JSON string
    --json-data FILE      Create a work effort from a JSON file
    --json-string STRING  Create a work effort from a JSON string
    --list-active         List all active work efforts
    --list-recent DAYS    List work efforts created in the last N days
    --list-overdue        List overdue work efforts
    --list-by-assignee    List work efforts by assignee
    --assignee NAME       Assignee name for filtering
    --priority LEVEL      Priority level for filtering (low, medium, high, critical)
    --sort-by FIELD       Sort results by field (created, due_date, priority, title)
    --limit NUM           Limit number of results
    --no-auto-start       Don't start the event loop automatically
    --verbose             Enable verbose logging

Version: 0.4.2
"""

import os
import sys
import json
import argparse
import logging
from work_effort_manager import WorkEffortManager
from datetime import datetime

def load_config_from_ai_setup():
    """
    Load the configuration from the .AI-Setup/config.json file if it exists.
    Returns a dictionary with the configuration or None if the file doesn't exist.
    """
    # First try current directory
    config_path = os.path.join(os.getcwd(), ".AI-Setup", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load config.json from current directory: {e}")

    # Try parent directory if not found
    parent_dir = os.path.dirname(os.getcwd())
    config_path = os.path.join(parent_dir, ".AI-Setup", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load config.json from parent directory: {e}")

    return None

def load_config(config_file):
    """
    Load configuration from a JSON file.

    Args:
        config_file: Path to the configuration file

    Returns:
        Dictionary with configuration or None if there was an error
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.info(f"Loaded configuration from {config_file}")
        return config
    except Exception as e:
        logging.error(f"Error loading configuration from {config_file}: {e}")
        return None

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the WorkEffortManager to handle centralized operations"
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=None,
        help="Project directory (default: current directory)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--config-json",
        type=str,
        default=None,
        help="Configuration as JSON string",
    )
    parser.add_argument(
        "--json-data",
        type=str,
        default=None,
        help="Path to JSON file to create a work effort",
    )
    parser.add_argument(
        "--json-string",
        type=str,
        default=None,
        help="JSON string to create a work effort",
    )
    parser.add_argument(
        "--list-active",
        action="store_true",
        help="List all active work efforts",
    )
    parser.add_argument(
        "--list-recent",
        type=int,
        metavar="DAYS",
        help="List work efforts created in the last N days",
    )
    parser.add_argument(
        "--list-overdue",
        action="store_true",
        help="List overdue work efforts",
    )
    parser.add_argument(
        "--list-by-assignee",
        action="store_true",
        help="List work efforts by assignee",
    )
    parser.add_argument(
        "--assignee",
        type=str,
        help="Assignee name for filtering",
    )
    parser.add_argument(
        "--priority",
        type=str,
        choices=["low", "medium", "high", "critical"],
        help="Priority level for filtering",
    )
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=["created", "due_date", "priority", "title", "last_modified"],
        help="Sort results by field",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of results",
    )
    parser.add_argument(
        "--no-auto-start",
        action="store_true",
        help="Don't start the event loop automatically",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()

def setup_logging(verbose=False):
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def example_event_handler(data):
    """Example event handler function."""
    print(f"Event received: {data}")

def display_work_efforts(work_efforts, title):
    """Display a list of work efforts in a formatted table."""
    if not work_efforts:
        print(f"\n{title}: No work efforts found")
        return

    print(f"\n{title} ({len(work_efforts)} found):")
    print("-" * 100)
    print(f"{'TITLE':<30} {'ASSIGNEE':<15} {'PRIORITY':<10} {'DUE DATE':<12} {'STATUS':<10} {'CREATED':<20}")
    print("-" * 100)

    for we in work_efforts:
        metadata = we.get("metadata", {})
        print(f"{metadata.get('title', 'Unknown'):<30} "
              f"{metadata.get('assignee', 'Unassigned'):<15} "
              f"{metadata.get('priority', 'None'):<10} "
              f"{metadata.get('due_date', 'None'):<12} "
              f"{metadata.get('status', 'None'):<10} "
              f"{metadata.get('created', 'Unknown'):<20}")

    print("-" * 100)

def main():
    """Main function to run the manager."""
    args = parse_args()
    setup_logging(args.verbose)

    # Load configuration from different sources in priority order:
    # 1. Command line config file
    # 2. Command line config JSON
    # 3. .AI-Setup/config.json
    config = None

    if args.config:
        config = load_config(args.config)
    elif args.config_json:
        try:
            config = json.loads(args.config_json)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config JSON: {e}")
            sys.exit(1)
    else:
        config = load_config_from_ai_setup()

    # If config is not None and has a work_efforts section, use it
    work_efforts_config = None
    if config and "work_efforts" in config:
        work_efforts_config = config["work_efforts"]

    # Set up project directory
    project_dir = args.project_dir
    if not project_dir and work_efforts_config and "project_dir" in work_efforts_config:
        project_dir = work_efforts_config["project_dir"]

    # Create the manager
    manager = WorkEffortManager(
        project_dir=project_dir,
        config=work_efforts_config
    )

    # Register example event handler
    manager.register_handler("file_created", example_event_handler)

    # Handle specific operations
    if args.json_data:
        try:
            with open(args.json_data, 'r') as f:
                result = manager.create_work_effort_from_json(f)
                if result:
                    print(f"Created work effort: {result}")
                else:
                    print("Failed to create work effort from JSON data.")
        except Exception as e:
            logging.error(f"Error creating work effort from JSON file: {e}")

    elif args.json_string:
        result = manager.create_work_effort_from_json(args.json_string)
        if result:
            print(f"Created work effort: {result}")
        else:
            print("Failed to create work effort from JSON string.")

    elif args.list_active or args.list_recent or args.list_overdue or args.list_by_assignee:
        filters = {}
        if args.assignee:
            filters['assignee'] = args.assignee
        if args.priority:
            filters['priority'] = args.priority
        if args.sort_by:
            filters['sort_by'] = args.sort_by
        if args.limit:
            filters['limit'] = args.limit

        if args.list_active:
            display_work_efforts(manager.get_active_work_efforts(**filters),
                                "Active Work Efforts")
        elif args.list_recent:
            days = int(args.list_recent) if args.list_recent else 7
            display_work_efforts(manager.get_recent_work_efforts(days, **filters),
                                f"Work Efforts from the Last {days} Days")
        elif args.list_overdue:
            display_work_efforts(manager.get_overdue_work_efforts(**filters),
                                "Overdue Work Efforts")
        elif args.list_by_assignee and args.assignee:
            display_work_efforts(manager.get_work_efforts_by_assignee(args.assignee, **filters),
                                f"Work Efforts Assigned to {args.assignee}")

    # Start the manager if not in no-auto-start mode and no specific operation was requested
    elif not args.no_auto_start:
        manager.start()

if __name__ == "__main__":
    main()