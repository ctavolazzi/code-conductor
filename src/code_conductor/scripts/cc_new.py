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
import asyncio
from datetime import datetime
from pathlib import Path

# Import the correct WorkEffortManager and setup functions
try:
    # Direct import if installed as a package
    from code_conductor.manager import WorkEffortManager
    from code_conductor.cli.cli import find_nearest_config, setup_ai_in_current_dir
except ImportError:
    try:
        # Import from src if in development mode
        from src.code_conductor.manager import WorkEffortManager
        from src.code_conductor.cli.cli import find_nearest_config, setup_ai_in_current_dir
    except ImportError:
        try:
            # Try using path-based import as last resort
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from src.code_conductor.manager import WorkEffortManager
            from src.code_conductor.cli.cli import find_nearest_config, setup_ai_in_current_dir
        except ImportError:
            print("Error: Could not import required modules.")
            print("Make sure code_conductor is installed or you're in the correct directory.")
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
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run setup if needed before creating the work effort"
    )

    return parser.parse_args()

async def ensure_setup(verbose=False, force=False):
    """
    Ensure that the work effort system is set up in the current directory.

    Args:
        verbose: Whether to show detailed output
        force: Whether to force setup even if it appears to be set up

    Returns:
        True if setup exists or was successfully created, False otherwise
    """
    current_dir = os.getcwd()

    # Check if work_efforts directory exists
    work_efforts_dir = os.path.join(current_dir, "work_efforts")
    ai_setup_dir = os.path.join(current_dir, "_AI-Setup")

    has_work_efforts = os.path.exists(work_efforts_dir) and os.path.isdir(work_efforts_dir)
    has_ai_setup = os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir)

    # Check for config file
    config_file, _ = find_nearest_config()
    has_config = config_file is not None

    if has_work_efforts and has_ai_setup and has_config and not force:
        if verbose:
            print("✅ Work effort system already set up")
        return True

    # Setup needed
    if verbose:
        print("⚙️ Setting up work effort system...")

    try:
        # Run the setup process
        await setup_ai_in_current_dir()

        # Verify that setup worked
        work_efforts_dir = os.path.join(current_dir, "work_efforts")
        ai_setup_dir = os.path.join(current_dir, "_AI-Setup")

        has_work_efforts = os.path.exists(work_efforts_dir) and os.path.isdir(work_efforts_dir)
        has_ai_setup = os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir)

        if has_work_efforts and has_ai_setup:
            if verbose:
                print("✅ Work effort system set up successfully")
            return True
        else:
            if verbose:
                print("❌ Failed to set up work effort system")
            return False
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        return False

async def main_async():
    """Async main function with clean workflow for creating a work effort."""
    args = parse_arguments()

    # Ensure the work effort system is set up
    if args.setup:
        setup_successful = await ensure_setup(verbose=args.verbose, force=args.setup)
        if not setup_successful:
            print("❌ Failed to set up work effort system. Please run 'code-conductor setup' first.")
            return 1

    # Get current directory (where we'll create the work effort)
    current_dir = os.getcwd()

    # Show summary if verbose
    if args.verbose:
        print(f"Creating new work effort:")
        print(f"  Title:     {args.title}")
        print(f"  Assignee:  {args.assignee}")
        print(f"  Priority:  {args.priority}")
        print(f"  Due Date:  {args.due_date}")
        print(f"  Location:  {current_dir}")
        print(f"  Format:    Sequential numbering")

    # Create the WorkEffortManager instance with the current directory
    manager = WorkEffortManager(project_dir=current_dir)

    # Create the work effort with sequential numbering
    work_effort_path = manager.create_work_effort(
        title=args.title,
        assignee=args.assignee,
        priority=args.priority,
        due_date=args.due_date,
        use_sequential_numbering=True  # Always use sequential numbering
    )

    # Handle success or failure clearly
    if work_effort_path:
        rel_path = os.path.relpath(work_effort_path, current_dir)
        print(f"✅ Work effort created: {rel_path}")
        return 0
    else:
        print("❌ Failed to create work effort")
        print("   ▶ Make sure you've run 'code-conductor setup' in this directory first")
        return 1

def main():
    """Main entry point - runs the async main function."""
    return asyncio.run(main_async())

if __name__ == "__main__":
    sys.exit(main())