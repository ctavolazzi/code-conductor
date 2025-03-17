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

def load_config(config_path):
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    if not config_path or not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return {}

def load_config_from_ai_setup(base_dir=None):
    """
    Load configuration from the _AI-Setup/config.json file.

    Args:
        base_dir: Base directory to look for _AI-Setup folder (default: current directory)

    Returns:
        tuple: (config_path, config_dict) - Path to the config file and the loaded configuration
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Look for _AI-Setup/config.json
    config_path = os.path.join(base_dir, "_AI-Setup", "config.json")
    config = {}

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logging.info(f"Found config file at: {config_path}")
        except Exception as e:
            logging.error(f"Error loading config from {config_path}: {str(e)}")

    return config_path, config

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
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose)

    # Load configuration from file if specified
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            print(f"Loaded configuration from {args.config}")
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")

    try:
        print("Initializing WorkEffortManager...")

        # Create the WorkEffortManager instance with JSON config support
        manager = WorkEffortManager(
            project_dir=args.project_dir,
            config=config,
            config_json=args.config_json,
            config_file=args.config,
            auto_start=False  # Don't auto-start, we'll check folders first
        )

        # Check if the required folders exist
        if not manager.has_required_folders():
            print("\n⚠️ Required folders not found!")
            print(f"Project directory: {manager.project_dir}")
            print(f"- Work efforts directory exists: {manager.has_work_efforts_dir}")
            print(f"- _AI-Setup directory exists: {manager.has_ai_setup_dir}")

            print("Directories:")
            print(f"- Work efforts directory: {manager.work_efforts_dir}")
            print(f"- Active work efforts: {manager.active_dir}")
            print(f"- _AI-Setup directory: {manager.ai_setup_dir}")
            return 1

        print("\n✅ Found required folders:")
        print(f"Project directory: {manager.project_dir}")
        print(f"- Work efforts directory exists: {manager.has_work_efforts_dir}")
        print(f"- _AI-Setup directory exists: {manager.has_ai_setup_dir}")

        print("Directories:")
        print(f"- Work efforts directory: {manager.work_efforts_dir}")
        print(f"- Active work efforts: {manager.active_dir}")
        print(f"- _AI-Setup directory: {manager.ai_setup_dir}")

        # Register example event handlers
        manager.register_handler("work_effort_created", example_event_handler)
        manager.register_handler("work_effort_updated", example_event_handler)
        manager.register_handler("work_effort_deleted", example_event_handler)

        # Process listing commands
        if args.list_active:
            # Get active work efforts
            work_efforts = manager.get_active_work_efforts(
                priority=args.priority,
                assignee=args.assignee,
                sort_by=args.sort_by or "title",
                limit=args.limit
            )
            display_work_efforts(work_efforts, "Active Work Efforts")
            return 0

        if args.list_recent is not None:
            # Get recent work efforts
            work_efforts = manager.get_recent_work_efforts(
                days=args.list_recent,
                priority=args.priority,
                assignee=args.assignee,
                sort_by=args.sort_by or "created",
                reverse=True,
                limit=args.limit
            )
            display_work_efforts(work_efforts, f"Work Efforts Created in the Last {args.list_recent} Days")
            return 0

        if args.list_overdue:
            # Get overdue work efforts
            work_efforts = manager.get_overdue_work_efforts(
                priority=args.priority,
                assignee=args.assignee,
                sort_by=args.sort_by or "due_date",
                limit=args.limit
            )
            display_work_efforts(work_efforts, "Overdue Work Efforts")
            return 0

        if args.list_by_assignee and args.assignee:
            # Get work efforts by assignee
            work_efforts = manager.get_work_efforts_by_assignee(
                assignee=args.assignee,
                priority=args.priority,
                sort_by=args.sort_by or "due_date",
                limit=args.limit
            )
            display_work_efforts(work_efforts, f"Work Efforts Assigned to {args.assignee}")
            return 0

        # Create a work effort from JSON if specified
        if args.json_data:
            print(f"\nCreating work effort from JSON file: {args.json_data}")
            try:
                with open(args.json_data, 'r') as f:
                    work_effort_path = manager.create_work_effort_from_json(f)

                if work_effort_path:
                    print(f"\n✅ Successfully created work effort from JSON file at: {work_effort_path}")
                else:
                    print("\n❌ Failed to create work effort from JSON file")
            except Exception as e:
                print(f"\n❌ Error creating work effort from JSON file: {str(e)}")

        # Create a work effort from JSON string if specified
        elif args.json_string:
            print("\nCreating work effort from JSON string")
            work_effort_path = manager.create_work_effort_from_json(args.json_string)

            if work_effort_path:
                print(f"\n✅ Successfully created work effort from JSON string at: {work_effort_path}")
            else:
                print("\n❌ Failed to create work effort from JSON string")

        # Create a sample work effort if no JSON specified
        else:
            print("\nCreating a sample work effort...")
            sample_json = json.dumps({
                "title": "Sample JSON Work Effort",
                "assignee": "user",
                "priority": "medium",
                "due_date": datetime.now().strftime("%Y-%m-%d"),
                "content": {
                    "objectives": ["Demonstrate JSON capabilities", "Show flexibility of the system"],
                    "tasks": ["Test JSON input", "Verify template generation", "Check event handling"],
                    "notes": ["Created using the JSON API", "This demonstrates the versatility of the system"]
                }
            })

            work_effort_path = manager.create_work_effort_from_json(sample_json)

            if work_effort_path:
                print(f"\n✅ Successfully created sample work effort at: {work_effort_path}")
            else:
                print("\n❌ Failed to create sample work effort")
                return 1

        # Start the manager if auto-start was not set
        if not args.no_auto_start:
            print("\nStarting WorkEffortManager event loop...")
            manager.start()

    except KeyboardInterrupt:
        print("\nWorkEffortManager terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())