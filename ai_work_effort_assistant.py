#!/usr/bin/env python3
"""
AI Work Effort Assistant

This script orchestrates AI-assisted work through tasks in work efforts.
It follows a semi-autonomous workflow where it:
1. Lists active work efforts
2. Selects one to work on based on priority
3. Identifies incomplete tasks
4. Attempts to complete them
5. Updates the work effort
6. Repeats until all tasks are done, then completes the work effort
"""

import os
import sys
import json
import re
import argparse
import datetime
import subprocess
import time
import random
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Work Effort Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_work_effort_assistant.py --id 8
  python ai_work_effort_assistant.py --filename 0008_comprehensive_work_effort_usage_documentation.md
  python ai_work_effort_assistant.py --auto
"""
    )

    # Arguments for identifying the work effort
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--filename", help="The filename of the work effort to work on")
    group.add_argument("--id", help="The ID number of the work effort to work on (e.g., 8 for 0008_...)")
    group.add_argument("--title", help="The title of the work effort to work on")
    group.add_argument("--auto", action="store_true", help="Automatically select a high-priority work effort")
    group.add_argument("--list", action="store_true", help="List all active work efforts and exit")

    # Additional options
    parser.add_argument("--update-devlog", action="store_true", help="Update the devlog with progress information")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--complete-when-done", action="store_true", help="Complete the work effort if all tasks are done")

    return parser.parse_args()

def list_active_work_efforts():
    """List all active work efforts using the list_active_work_efforts.py script."""
    try:
        # Run the list_active_work_efforts.py script to generate JSON data
        subprocess.run(['python', 'list_active_work_efforts.py'],
                       check=True, stdout=subprocess.PIPE)

        # Load the generated JSON file
        with open('active_work_efforts.json', 'r') as f:
            data = json.load(f)

        return data.get('active_work_efforts', [])
    except Exception as e:
        print(f"Error listing work efforts: {e}")
        return []

def select_work_effort(args):
    """Select a work effort based on the provided arguments or automatically."""
    work_efforts = list_active_work_efforts()

    if args.list:
        print("Active Work Efforts:")
        print("--------------------")
        for i, we in enumerate(work_efforts):
            print(f"{i+1}. [{we['priority']}] {we['title']} ({we['filename']})")
        sys.exit(0)

    if args.auto:
        # Select a high-priority work effort
        # Sort by priority first
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        work_efforts.sort(key=lambda x: priority_order.get(x['priority'].lower(), 5))

        # Take the highest priority work effort
        if work_efforts:
            selected = work_efforts[0]
            print(f"Auto-selected work effort: {selected['title']} ({selected['filename']})")
            return selected
        else:
            print("No active work efforts found.")
            sys.exit(1)

    # Find based on provided identifier
    if args.filename:
        for we in work_efforts:
            if we['filename'] == args.filename:
                return we

    elif args.id:
        id_pattern = f"{int(args.id):04d}_"
        for we in work_efforts:
            if we['filename'].startswith(id_pattern):
                return we

    elif args.title:
        for we in work_efforts:
            if we['title'].lower() == args.title.lower():
                return we

    print(f"Error: Could not find a matching work effort!")
    sys.exit(1)

def extract_tasks_from_work_effort(work_effort_path):
    """Extract tasks from a work effort file."""
    try:
        with open(work_effort_path, 'r') as f:
            content = f.read()

        # Split by markdown headers to get sections
        sections = re.split(r'^(#+\s+.*?)$', content, flags=re.MULTILINE)

        tasks_by_section = {}
        current_section = "General"

        for i, section in enumerate(sections):
            if i % 2 == 1:  # This is a header
                current_section = section.strip()
            else:  # This is content
                # Look for task patterns
                tasks = re.findall(r'[-\*] \[([ xX✓✅])\]\s+(.*?)(?=\n|$)', section)
                if tasks:
                    tasks_by_section[current_section] = [
                        {
                            "description": task[1].strip(),
                            "completed": task[0].strip().lower() in ['x', 'X', '✓', '✅'],
                            "line": None  # We'll fill this in when needed
                        }
                        for task in tasks
                    ]

        # Get line numbers for tasks (useful for updating them later)
        lines = content.split('\n')
        for section, tasks in tasks_by_section.items():
            for task in tasks:
                for i, line in enumerate(lines):
                    if task['description'] in line and ('[ ]' in line or '[x]' in line or '[X]' in line or '[✓]' in line or '[✅]' in line):
                        task['line'] = i + 1
                        break

        return tasks_by_section

    except Exception as e:
        print(f"Error extracting tasks: {e}")
        return {}

def display_tasks(tasks_by_section):
    """Display tasks by section with their completion status."""
    print("\nTask Status by Section:")
    print("======================")

    total_tasks = 0
    completed_tasks = 0

    for section, tasks in tasks_by_section.items():
        if not tasks:
            continue

        # Count completed tasks in this section
        section_completed = sum(1 for t in tasks if t["completed"])
        section_total = len(tasks)

        print(f"\n{section} ({section_completed}/{section_total} completed):")

        for i, task in enumerate(tasks):
            status = "✅" if task["completed"] else "[ ]"
            print(f"  {status} {task['description']}")

        total_tasks += section_total
        completed_tasks += section_completed

    if total_tasks == 0:
        print("No tasks found in this work effort.")
    else:
        print(f"\nOverall: {completed_tasks}/{total_tasks} tasks completed ({int(completed_tasks/total_tasks*100)}%)")

    return completed_tasks, total_tasks

def update_task_in_work_effort(work_effort_path, task_description, completed=True, dry_run=False):
    """Update a specific task in the work effort file."""
    if dry_run:
        print(f"Would mark task as {'completed' if completed else 'incomplete'}: {task_description}")
        return True

    try:
        with open(work_effort_path, 'r') as f:
            lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            if task_description in line and ('[ ]' in line or '[x]' in line or '[X]' in line or '[✓]' in line or '[✅]' in line):
                if completed:
                    # Mark as completed
                    lines[i] = re.sub(r'\[ \]', '[x]', line)
                else:
                    # Mark as incomplete
                    lines[i] = re.sub(r'\[[xX✓✅]\]', '[ ]', line)
                updated = True
                break

        if updated:
            with open(work_effort_path, 'w') as f:
                f.writelines(lines)

            print(f"Updated task: {task_description}")
            return True
        else:
            print(f"Could not find task to update: {task_description}")
            return False

    except Exception as e:
        print(f"Error updating task: {e}")
        return False

def simulate_ai_task_work(task, verbose=False, dry_run=False):
    """Simulate AI working on a task (for demonstration purposes)."""
    print(f"\nWorking on task: {task['description']}")

    # Simulate thinking/processing
    if verbose:
        print("  🤔 Analyzing task requirements...")
        time.sleep(0.5)
        print("  📊 Assessing necessary actions...")
        time.sleep(0.5)
        print("  🔍 Searching for related files...")
        time.sleep(0.5)
        print("  📝 Generating implementation plan...")
        time.sleep(0.5)

    # Randomly determine if task can be completed (for demo purposes)
    # In a real implementation, this would be replaced with actual task execution
    success_probability = 0.8  # 80% chance of success
    success = random.random() < success_probability

    if success:
        # Simulate successful task execution
        print("  ✅ Task completed successfully!")
        return True
    else:
        # Simulate unsuccessful task execution
        print("  ❌ Unable to complete this task automatically.")
        print("  ❓ This task requires human intervention.")
        return False

def update_devlog_with_progress(work_effort, completed_tasks, total_tasks, dry_run=False):
    """Update the devlog with progress information."""
    if dry_run:
        print("Would update devlog with progress information")
        return

    try:
        # Get the current timestamp
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Prepare the devlog entry
        devlog_entry = f"\n## {now} - Progress on {work_effort['title']}\n\n"
        devlog_entry += f"AI assistant has made progress on the '{work_effort['title']}' work effort.\n"
        devlog_entry += f"Current status: {completed_tasks}/{total_tasks} tasks completed ({int(completed_tasks/total_tasks*100)}%).\n\n"

        # Write to the devlog
        with open("work_efforts/devlog.md", "a") as f:
            f.write(devlog_entry)

        print("✅ Devlog updated with progress information")
    except Exception as e:
        print(f"Warning: Could not update devlog: {e}")

def complete_work_effort(work_effort_path, update_devlog=False, dry_run=False):
    """Complete the work effort using the complete_work_effort.py script."""
    if dry_run:
        print(f"Would complete work effort: {work_effort_path}")
        return True

    try:
        cmd = ["python", "complete_work_effort.py", "--filename", os.path.basename(work_effort_path), "--no-confirmation"]

        if update_devlog:
            cmd.append("--update-devlog")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
            print("✅ Work effort completed successfully!")
            return True
        else:
            print(f"❌ Failed to complete work effort: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error completing work effort: {e}")
        return False

def main():
    """Main function to orchestrate AI work on tasks."""
    args = parse_arguments()

    # Select a work effort to work on
    work_effort = select_work_effort(args)

    print(f"\nSelected work effort: {work_effort['title']}")
    print(f"  Path: {work_effort['path']}")
    print(f"  Status: {work_effort['status']}")
    print(f"  Priority: {work_effort['priority']}")
    print(f"  Assignee: {work_effort['assignee']}")

    # Extract tasks from the work effort
    work_effort_path = work_effort['path']
    tasks_by_section = extract_tasks_from_work_effort(work_effort_path)

    # Display initial task status
    completed_tasks, total_tasks = display_tasks(tasks_by_section)

    # Exit if all tasks are already completed
    if completed_tasks == total_tasks and total_tasks > 0:
        print("\nAll tasks are already completed!")

        if args.complete_when_done:
            print("Proceeding to complete the work effort...")
            complete_work_effort(work_effort_path, args.update_devlog, args.dry_run)

        return 0

    # Find incomplete tasks
    incomplete_tasks = []
    for section, tasks in tasks_by_section.items():
        for task in tasks:
            if not task["completed"]:
                task["section"] = section
                incomplete_tasks.append(task)

    # Sort by section (tasks in the same section are likely related)
    incomplete_tasks.sort(key=lambda x: x["section"])

    # Work on incomplete tasks
    completed_by_ai = 0
    for task in incomplete_tasks:
        # Simulate AI working on the task
        if simulate_ai_task_work(task, args.verbose, args.dry_run):
            # Update the task in the work effort
            if update_task_in_work_effort(work_effort_path, task["description"], True, args.dry_run):
                completed_by_ai += 1

        # Short pause between tasks
        time.sleep(0.3)

    # Display updated task status
    print("\nUpdated Task Status:")
    if not args.dry_run:
        # Reload tasks to see updated status
        tasks_by_section = extract_tasks_from_work_effort(work_effort_path)

    completed_tasks, total_tasks = display_tasks(tasks_by_section)

    # Update devlog with progress if requested
    if args.update_devlog and completed_by_ai > 0:
        update_devlog_with_progress(work_effort, completed_tasks, total_tasks, args.dry_run)

    # Complete the work effort if all tasks are completed and requested
    if completed_tasks == total_tasks and args.complete_when_done:
        print("\nAll tasks are now completed! Proceeding to complete the work effort...")
        complete_work_effort(work_effort_path, args.update_devlog, args.dry_run)

    # Summary
    print(f"\nSummary:")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Tasks completed before: {completed_tasks - completed_by_ai}")
    print(f"  Tasks completed by AI: {completed_by_ai}")
    print(f"  Tasks remaining: {total_tasks - completed_tasks}")
    print(f"  Completion percentage: {int(completed_tasks/total_tasks*100)}%")

    return 0

if __name__ == "__main__":
    sys.exit(main())