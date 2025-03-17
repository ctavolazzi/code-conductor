#!/usr/bin/env python3
"""
A simple script to create a new work effort using the WorkEffortManager directly.

Usage:
  python work_effort_creator.py "Title of Work Effort" [OPTIONS]

Options:
  --assignee NAME     Person assigned to the work (default: unassigned)
  --priority LEVEL    Priority level (low, medium, high, critical) (default: medium)
  --due-date DATE     Due date in YYYY-MM-DD format (default: 2099-12-31)
  --location DIR      Directory to create the work effort in (default: auto-detect)
"""

import os
import sys
import argparse
from datetime import datetime

# Try to import the WorkEffortManager
try:
    from src.code_conductor.work_efforts.scripts.work_effort_manager import WorkEffortManager
except ImportError:
    try:
        # Second attempt if we're in the package directory
        from code_conductor.work_efforts.scripts.work_effort_manager import WorkEffortManager
    except ImportError:
        # Last attempt - direct import
        try:
            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
            from code_conductor.work_efforts.scripts.work_effort_manager import WorkEffortManager
        except ImportError:
            print("Error: Could not import WorkEffortManager. Make sure code_conductor is installed or in your PYTHONPATH.")
            sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create a new work effort using WorkEffortManager")

    parser.add_argument("title", help="Title of the work effort")
    parser.add_argument("--assignee", "-a", default="unassigned", help="Person assigned to the work")
    parser.add_argument("--priority", "-p", default="medium", choices=["low", "medium", "high", "critical"], help="Priority level")
    parser.add_argument("--due-date", "-d", default="2099-12-31", help="Due date in YYYY-MM-DD format")
    parser.add_argument("--location", "-l", help="Directory to create the work effort in")

    return parser.parse_args()

def main():
    """Main function to create a work effort."""
    args = parse_arguments()

    # Determine the project directory
    project_dir = args.location if args.location else os.getcwd()

    # Print info about what we're doing
    print(f"Creating new work effort:")
    print(f"  Title:     {args.title}")
    print(f"  Assignee:  {args.assignee}")
    print(f"  Priority:  {args.priority}")
    print(f"  Due Date:  {args.due_date}")
    print(f"  Location:  {project_dir}")

    # Create the work effort manager
    manager = WorkEffortManager(project_dir=project_dir)

    # Create the work effort
    work_effort_path = manager.create_work_effort(
        title=args.title,
        assignee=args.assignee,
        priority=args.priority,
        due_date=args.due_date
    )

    if work_effort_path:
        print(f"\n✅ Work effort created successfully at: {work_effort_path}")
        return 0
    else:
        print("\n❌ Failed to create work effort. Check logs for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())