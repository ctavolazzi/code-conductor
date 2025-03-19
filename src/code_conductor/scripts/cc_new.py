#!/usr/bin/env python3
"""
cc-new - A clean, simple command for creating work efforts

This is a streamlined interface to the WorkEffortManager that focuses on just
one thing: creating work efforts correctly and reliably.

Usage:
  cc-new "Title of Work Effort" [OPTIONS]

Examples:
  cc-new "New Feature Implementation"
  cc-new "Bug Fix" -p high -a "Developer Name"
  cc-new "Documentation Update" --due-date 2023-12-31
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

# Import the correct WorkEffortManager and setup functions
try:
    # Direct import if installed as a package
    from code_conductor.core.work_effort.manager import WorkEffortManager
except ImportError:
    try:
        # Try importing from src directory
        from src.code_conductor.core.work_effort.manager import WorkEffortManager
    except ImportError:
        print("Error: Could not import WorkEffortManager. Make sure code_conductor is installed.")
        sys.exit(1)

def parse_arguments():
    """Parse command-line arguments with clear, simple options."""
    parser = argparse.ArgumentParser(
        description="Create a new work effort with minimal fuss",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cc-new "New Feature Implementation"
  cc-new "Bug Fix" -p high -a "Developer Name"
  cc-new "Documentation Update" --due-date 2023-12-31
"""
    )

    # Required argument - title
    parser.add_argument(
        "title",
        help="Title of the work effort (required)"
    )

    # Optional arguments with short and long forms
    parser.add_argument(
        "-a", "--assignee",
        default="unassigned",
        help="Person assigned to the work (default: unassigned)"
    )
    parser.add_argument(
        "-p", "--priority",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Priority level (default: medium)"
    )
    parser.add_argument(
        "-d", "--due-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Due date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    return parser.parse_args()

def find_project_root(start_dir, verbose=False):
    """Find the project root by looking for .code-conductor file or _AI-Setup directory."""
    current = os.path.abspath(start_dir)

    # Keep going up until we find the root or hit the system root
    while current != os.path.dirname(current):  # Check if we've reached the system root
        # Check for .code-conductor file
        code_conductor_file = os.path.join(current, ".code-conductor")
        ai_setup_dir = os.path.join(current, "_AI-Setup")

        if os.path.exists(code_conductor_file) or os.path.exists(ai_setup_dir):
            if verbose:
                print(f"Found project root at: {current}")
            return current

        # Move up one directory
        current = os.path.dirname(current)

    # If we get here, use the starting directory
    if verbose:
        print(f"No project root found, using current directory: {start_dir}")
    return start_dir

def create_work_effort_in_current_dir(manager, title, assignee, priority, due_date, verbose=False):
    """
    Create a work effort in a work_efforts folder in the current directory.

    This function:
    1. Creates a work_efforts folder in the current directory if it doesn't exist
    2. Creates the necessary subdirectories (active, completed, archived)
    3. Creates the work effort in the work_efforts/active directory
    """
    # Get current directory
    current_dir = os.getcwd()

    # Create work_efforts directory structure in current directory
    work_efforts_dir = os.path.join(current_dir, "work_efforts")
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")

    # Create the directories if they don't exist
    os.makedirs(active_dir, exist_ok=True)
    os.makedirs(completed_dir, exist_ok=True)
    os.makedirs(archived_dir, exist_ok=True)

    if verbose:
        print(f"Created work_efforts directory structure in current directory")

    # Store original directories
    original_active_dir = manager.active_dir
    original_completed_dir = manager.completed_dir
    original_archived_dir = manager.archived_dir

    try:
        # Set the directories to use our local work_efforts structure
        manager.active_dir = active_dir
        manager.completed_dir = completed_dir
        manager.archived_dir = archived_dir

        # Create the work effort
        if verbose:
            print(f"Creating work effort in: {active_dir}")

        work_effort_path = manager.create_work_effort(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date,
            use_sequential_numbering=True  # Always use sequential numbering
        )

        return work_effort_path
    finally:
        # Restore original directories
        manager.active_dir = original_active_dir
        manager.completed_dir = original_completed_dir
        manager.archived_dir = original_archived_dir

def main():
    """Main function with clean workflow for creating a work effort."""
    args = parse_arguments()

    # Get current directory
    current_dir = os.getcwd()

    # Find the project root for central tracking
    project_root = find_project_root(current_dir, verbose=args.verbose)

    # Show summary if verbose
    if args.verbose:
        print(f"Creating new work effort:")
        print(f"  Title:     {args.title}")
        print(f"  Assignee:  {args.assignee}")
        print(f"  Priority:  {args.priority}")
        print(f"  Due Date:  {args.due_date}")
        print(f"  Location:  {current_dir}/work_efforts")
        print(f"  Format:    Sequential numbering")

    # Create the WorkEffortManager with the project root
    manager = WorkEffortManager(project_dir=project_root)

    # Create the work effort in the work_efforts directory in the current directory
    work_effort_path = create_work_effort_in_current_dir(
        manager=manager,
        title=args.title,
        assignee=args.assignee,
        priority=args.priority,
        due_date=args.due_date,
        verbose=args.verbose
    )

    # Handle success or failure clearly
    if work_effort_path:
        rel_path = os.path.relpath(work_effort_path, current_dir)
        print(f"✅ Work effort created: {rel_path}")
        return 0
    else:
        print("❌ Failed to create work effort")
        print("   ▶ Run 'code-conductor setup' if this is the first work effort in the project")
        return 1

if __name__ == "__main__":
    sys.exit(main())