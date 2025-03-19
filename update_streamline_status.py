#!/usr/bin/env python3
"""
Update Status Script

This script updates the status of the Streamline Work Effort Creation and Tracing System to "completed".
"""

import os
import sys
import datetime
from pathlib import Path

# Try different import paths
try:
    from src.code_conductor.workflow.workflow_runner import WorkflowRunner
except ImportError:
    try:
        # Add the project root to the path
        sys.path.insert(0, str(Path(__file__).parent))
        from src.code_conductor.workflow.workflow_runner import WorkflowRunner
    except ImportError:
        print("Error: Could not import WorkflowRunner.")
        print("Make sure you're running this script from the project root.")
        sys.exit(1)

def main():
    """Update the status of the Streamline Work Effort Creation and Tracing System to completed."""
    print("Updating status of 'Streamline Work Effort Creation and Tracing System' work effort...\n")

    # Create a workflow runner instance
    runner = WorkflowRunner(interactive=False)

    # Set the work effort path
    work_effort_filename = "202503171451_streamline_work_effort_creation_and_tracing_system.md"
    active_dir = os.path.join(os.getcwd(), "work_efforts", "active")
    work_effort_path = os.path.join(active_dir, work_effort_filename)

    # Update runner's work effort path
    runner.work_effort_path = work_effort_path

    # Check if the file exists
    if not os.path.exists(work_effort_path):
        print(f"Error: Work effort file not found at {work_effort_path}")
        return 1

    # Update the status to completed
    print(f"Changing status to 'completed'...")
    success = runner.update_work_effort_status("completed")

    if success:
        # Get the current timestamp for logging
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"✅ Work effort status updated successfully at {now}")
        print(f"New location: {runner.work_effort_path}")
        print(f"Status: {runner.status}")

        # Add to devlog
        print(f"Updating devlog with completion information...")
        try:
            with open("work_efforts/devlog.md", "a") as f:
                f.write(f"\n## {now} - Streamline Work Effort Completion\n\n")
                f.write("Successfully completed the 'Streamline Work Effort Creation and Tracing System' work effort.\n")
                f.write("All tasks have been completed, comprehensive tests have been added, and the system has been verified to work reliably.\n\n")
            print("✅ Devlog updated successfully")
        except Exception as e:
            print(f"Warning: Could not update devlog: {e}")
    else:
        print(f"❌ Failed to update work effort status")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())