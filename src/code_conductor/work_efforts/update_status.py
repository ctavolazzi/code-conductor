#!/usr/bin/env python3
"""
Update Status Script

This script updates the status of the Enhanced Workflow Runner work effort to "completed".
"""

import os
import sys
from src.code_conductor.workflow.workflow_runner import WorkflowRunner, ACTIVE_DIR

def main():
    """Update the status of the Enhanced Workflow Runner work effort."""
    print("Updating status of Enhanced Workflow Runner work effort...\n")

    # Create a workflow runner instance
    runner = WorkflowRunner(interactive=False)

    # Set the work effort path
    work_effort_filename = "202503160751_enhanced_workflow_runner.md"
    runner.work_effort_path = os.path.join(ACTIVE_DIR, work_effort_filename)

    # Check if the file exists
    if not os.path.exists(runner.work_effort_path):
        print(f"Error: Work effort file not found at {runner.work_effort_path}")
        return 1

    # Update the status to completed
    print(f"Changing status to 'completed'...")
    success = runner.update_work_effort_status("completed")

    if success:
        print(f"✅ Work effort status updated successfully")
        print(f"New location: {runner.work_effort_path}")
        print(f"Status: {runner.status}")
    else:
        print(f"❌ Failed to update work effort status")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())