#!/usr/bin/env python3
"""
Work Effort Completion Automation

This script automates the process of completing a work effort, including:
1. Verifying all tasks in the checklist are completed
2. Updating the status to 'completed'
3. Moving it to the completed directory
4. Updating the devlog with completion information
5. Running any tests if specified
"""

import os
import sys
import json
import re
import argparse
import datetime
import subprocess
from pathlib import Path

# Try different import paths for WorkflowRunner
try:
    from src.code_conductor.workflow.workflow_runner import WorkflowRunner
except ImportError:
    try:
        # Add the project root to the path
        sys.path.insert(0, str(Path(__file__).parent))
        from src.code_conductor.workflow.workflow_runner import WorkflowRunner
    except ImportError:
        print("Warning: Could not import WorkflowRunner. Will use shell commands instead.")
        WorkflowRunner = None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automate work effort completion process",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python complete_work_effort.py --filename 0008_comprehensive_work_effort_usage_documentation.md
  python complete_work_effort.py --id 8
  python complete_work_effort.py --title "Comprehensive Work Effort Usage Documentation"
  python complete_work_effort.py --list
"""
    )

    # Arguments for identifying the work effort
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--filename", help="The filename of the work effort to complete")
    group.add_argument("--id", help="The ID number of the work effort to complete (e.g., 8 for 0008_...)")
    group.add_argument("--title", help="The title of the work effort to complete")
    group.add_argument("--list", action="store_true", help="List all active work efforts")

    # Additional options
    parser.add_argument("--run-tests", action="store_true", help="Run associated tests before completion")
    parser.add_argument("--no-confirmation", action="store_true", help="Complete without asking for confirmation")
    parser.add_argument("--update-devlog", action="store_true", help="Update the devlog with completion information")
    parser.add_argument("--force", action="store_true", help="Force completion even if tasks are incomplete")
    parser.add_argument("--ai-assist", action="store_true", help="Use AI to attempt to complete remaining tasks")

    return parser.parse_args()

def find_work_effort(args):
    """Find the work effort based on the provided identifier."""
    # Run the list_active_work_efforts.py script to get JSON data
    try:
        if not os.path.exists('list_active_work_efforts.py'):
            print("Error: list_active_work_efforts.py script not found!")
            return None

        subprocess.run(['python', 'list_active_work_efforts.py'], check=True, stdout=subprocess.PIPE)

        # Load the generated JSON file
        with open('active_work_efforts.json', 'r') as f:
            data = json.load(f)

        work_efforts = data.get('active_work_efforts', [])

        # If --list was specified, just print the work efforts and exit
        if args.list:
            print("Active Work Efforts:")
            print("--------------------")
            for i, we in enumerate(work_efforts):
                print(f"{i+1}. [{we['priority']}] {we['title']} ({we['filename']})")
            sys.exit(0)

        # Find the work effort based on the specified identifier
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
        return None

    except Exception as e:
        print(f"Error finding work effort: {e}")
        return None

def check_tasks_completion(work_effort_path):
    """
    Check if all tasks in the work effort are completed.
    Returns a tuple of (all_completed, total_tasks, completed_tasks, incomplete_tasks)
    Where incomplete_tasks is a list of task descriptions that are not completed.
    """
    try:
        with open(work_effort_path, 'r') as f:
            content = f.read()

        # Different task formats to check
        task_patterns = [
            r'- \[([ xX])\]\s+(.*?)(?=\n|$)',  # - [ ] Task or - [x] Task
            r'- \[([ xX])\]\s+(.*?)(?=\n|$)',  # - [ ] Task or - [X] Task
            r'\* \[([ xX])\]\s+(.*?)(?=\n|$)',  # * [ ] Task or * [x] Task
            r'- \[([✓ ])\]\s+(.*?)(?=\n|$)',   # - [✓] Task or - [ ] Task
            r'\[([✓ ])\]\s+(.*?)(?=\n|$)',     # [✓] Task or [ ] Task
            r'- \[([✅ ])\]\s+(.*?)(?=\n|$)',   # - [✅] Task or - [ ] Task
            r'- \[([ ✅])\]\s+(.*?)(?=\n|$)'    # - [ ] Task or - [✅] Task
        ]

        tasks = []
        for pattern in task_patterns:
            tasks.extend(re.findall(pattern, content))

        if not tasks:
            # Check if there are markdown task list items (- [x] format)
            tasks = re.findall(r'[-\*] \[([ xX✓✅])\]\s+(.*?)(?=\n|$)', content)

        if not tasks:
            # Also check for alternate checklist format like "✅ Task" or "- Task (completed)"
            alt_tasks1 = re.findall(r'[✅✓]\s+(.*?)(?=\n|$)', content)
            alt_tasks2 = re.findall(r'- (.*?) \(completed\)(?=\n|$)', content)
            tasks = [('x', task) for task in alt_tasks1] + [('x', task) for task in alt_tasks2]

        incomplete_tasks = []
        completed_count = 0

        for status, description in tasks:
            if status.strip().lower() in ['x', 'X', '✓', '✅']:
                completed_count += 1
            else:
                incomplete_tasks.append(description.strip())

        all_completed = len(incomplete_tasks) == 0 and len(tasks) > 0

        return (all_completed, len(tasks), completed_count, incomplete_tasks)

    except Exception as e:
        print(f"Error checking task completion: {e}")
        return (False, 0, 0, ["Error: Could not check tasks"])

def extract_task_sections(work_effort_path):
    """
    Extract sections that contain task lists from the work effort.
    Returns a dictionary mapping section headers to lists of tasks.
    """
    try:
        with open(work_effort_path, 'r') as f:
            content = f.read()

        # Split by markdown headers
        sections = re.split(r'^(#+\s+.*?)$', content, flags=re.MULTILINE)

        result = {}
        current_section = "General"

        for i, section in enumerate(sections):
            if i % 2 == 1:  # This is a header
                current_section = section.strip()
            else:  # This is content
                # Look for task patterns
                tasks = re.findall(r'[-\*] \[([ xX✓✅])\]\s+(.*?)(?=\n|$)', section)
                if tasks:
                    result[current_section] = [
                        {
                            "description": task[1].strip(),
                            "completed": task[0].strip().lower() in ['x', 'X', '✓', '✅']
                        }
                        for task in tasks
                    ]

        return result

    except Exception as e:
        print(f"Error extracting task sections: {e}")
        return {}

def display_task_status(work_effort_path):
    """Display the status of tasks in the work effort."""
    all_completed, total, completed, incomplete = check_tasks_completion(work_effort_path)

    if total == 0:
        print("No tasks found in the work effort.")
        return True

    print(f"Task Status: {completed}/{total} completed")

    if not all_completed:
        print("\nIncomplete Tasks:")
        for i, task in enumerate(incomplete):
            print(f"{i+1}. {task}")

        # Also display by section for more context
        sections = extract_task_sections(work_effort_path)
        if sections:
            print("\nTasks by Section:")
            for section, tasks in sections.items():
                incomplete_in_section = [t for t in tasks if not t["completed"]]
                if incomplete_in_section:
                    print(f"\n{section}:")
                    for task in incomplete_in_section:
                        print(f"  [ ] {task['description']}")

    return all_completed

def try_complete_tasks_with_ai(work_effort):
    """
    Attempt to complete remaining tasks in the work effort using AI capabilities.
    This is a placeholder for implementing task automation.
    """
    work_effort_path = work_effort['path']
    print(f"AI-assisted task completion for: {work_effort['title']}")

    # Extract task sections
    sections = extract_task_sections(work_effort_path)

    # Identify incomplete tasks
    for section, tasks in sections.items():
        incomplete = [t for t in tasks if not t["completed"]]
        if incomplete:
            print(f"\nSection: {section}")
            for task in incomplete:
                print(f"Attempting to complete: {task['description']}")
                # Here you would add logic to:
                # 1. Parse the task to determine what needs to be done
                # 2. Use appropriate CLI tools to complete the task
                # 3. Update the work effort file to mark the task as completed

                # For now, just simulate a process
                print(f"  ⚙️ Analyzing task requirements...")
                print(f"  ⚙️ Determining necessary actions...")
                print(f"  ⚙️ This is a placeholder for actual task execution")
                print(f"  ❓ Task completion would require human assistance")

    # Re-check completion status
    return check_tasks_completion(work_effort_path)[0]

def update_work_effort_tasks(work_effort_path, tasks_to_complete):
    """
    Update the work effort file to mark specified tasks as completed.
    tasks_to_complete: List of task descriptions to mark as completed.
    """
    try:
        with open(work_effort_path, 'r') as f:
            content = f.readlines()

        updated_content = []
        for line in content:
            updated_line = line
            for task in tasks_to_complete:
                # Match task description and update the checkbox
                if task in line:
                    # Update various checkbox formats
                    updated_line = re.sub(r'- \[ \]', r'- [x]', line)
                    updated_line = re.sub(r'\* \[ \]', r'* [x]', updated_line)
                    # Add more substitutions for other formats if needed

            updated_content.append(updated_line)

        with open(work_effort_path, 'w') as f:
            f.writelines(updated_content)

        print(f"Updated {len(tasks_to_complete)} tasks in {work_effort_path}")
        return True

    except Exception as e:
        print(f"Error updating tasks: {e}")
        return False

def run_tests(work_effort):
    """Run tests associated with the work effort if they exist."""
    filename = work_effort['filename']
    base_name = os.path.splitext(filename)[0]

    # Look for test files that might be associated with this work effort
    potential_test_files = [
        f"tests/test_{base_name}.py",
        f"tests/test_{base_name.lower()}.py",
        f"tests/test_{base_name.replace('-', '_')}.py"
    ]

    # Also look for test files with the ID
    if base_name.startswith('0'):
        id_match = re.match(r'0*(\d+)_.*', base_name)
        if id_match:
            id_num = id_match.group(1)
            potential_test_files.append(f"tests/test_{id_num}.py")

    for test_file in potential_test_files:
        if os.path.exists(test_file):
            print(f"Found test file: {test_file}")
            print(f"Running tests...")
            result = subprocess.run(['python', '-m', 'unittest', test_file], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Tests passed successfully!")
                print(result.stdout)
                return True
            else:
                print("❌ Tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False

    print("No specific test files found for this work effort.")
    return True  # Return True if no tests were found (shouldn't block completion)

def complete_with_workflow_runner(work_effort):
    """Complete the work effort using the WorkflowRunner."""
    if WorkflowRunner is None:
        return False

    try:
        runner = WorkflowRunner(interactive=False)
        work_effort_path = work_effort['path']

        # Set the work effort path
        runner.work_effort_path = work_effort_path

        # Check if the file exists
        if not os.path.exists(work_effort_path):
            print(f"Error: Work effort file not found at {work_effort_path}")
            return False

        # Update the status to completed
        print(f"Changing status to 'completed'...")
        success = runner.update_work_effort_status("completed")

        if success:
            # Get the current timestamp for logging
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            print(f"✅ Work effort status updated successfully at {now}")
            print(f"New location: {runner.work_effort_path}")
            print(f"Status: {runner.status}")
            return True
        else:
            print(f"❌ Failed to update work effort status")
            return False
    except Exception as e:
        print(f"Error using WorkflowRunner: {e}")
        return False

def complete_with_shell_commands(work_effort):
    """Complete the work effort using shell commands."""
    try:
        # Create a simple shell script to complete the work effort
        script_name = "temp_complete_work_effort.py"
        work_effort_path = work_effort['path']

        # Generate a script similar to the one we used earlier
        with open(script_name, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
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
    # Create a workflow runner instance
    runner = WorkflowRunner(interactive=False)

    # Set the work effort path
    work_effort_path = "{work_effort_path}"
    runner.work_effort_path = work_effort_path

    # Check if the file exists
    if not os.path.exists(work_effort_path):
        print(f"Error: Work effort file not found at {{work_effort_path}}")
        return 1

    # Update the status to completed
    print(f"Changing status to 'completed'...")
    success = runner.update_work_effort_status("completed")

    if success:
        # Get the current timestamp for logging
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"✅ Work effort status updated successfully at {{now}}")
        print(f"New location: {{runner.work_effort_path}}")
        print(f"Status: {{runner.status}}")
        return 0
    else:
        print(f"❌ Failed to update work effort status")
        return 1

if __name__ == "__main__":
    sys.exit(main())
""")

        # Make the script executable
        os.chmod(script_name, 0o755)

        # Run the script
        result = subprocess.run(['python', script_name], capture_output=True, text=True)

        # Output the result
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Clean up the temporary script
        os.remove(script_name)

        return result.returncode == 0

    except Exception as e:
        print(f"Error using shell commands: {e}")
        return False

def update_devlog(work_effort):
    """Update the devlog with completion information."""
    try:
        # Get the current timestamp
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Prepare the devlog entry
        devlog_entry = f"\n## {now} - {work_effort['title']} Completion\n\n"
        devlog_entry += f"Successfully completed the '{work_effort['title']}' work effort.\n"
        devlog_entry += f"All tasks have been completed and the work effort has been moved to the completed directory.\n\n"

        # Write to the devlog
        with open("work_efforts/devlog.md", "a") as f:
            f.write(devlog_entry)

        print("✅ Devlog updated successfully")
        return True
    except Exception as e:
        print(f"Warning: Could not update devlog: {e}")
        return False

def main():
    """Main function to automate work effort completion."""
    args = parse_arguments()

    # Find the work effort to complete
    work_effort = find_work_effort(args)
    if not work_effort:
        return 1

    # Display work effort information
    print(f"Found work effort: {work_effort['title']}")
    print(f"  Path: {work_effort['path']}")
    print(f"  Status: {work_effort['status']}")
    print(f"  Priority: {work_effort['priority']}")
    print(f"  Assignee: {work_effort['assignee']}")

    # Check if all tasks are completed
    print("\nVerifying task completion:")
    work_effort_path = work_effort['path']
    tasks_completed = display_task_status(work_effort_path)

    if not tasks_completed:
        if args.ai_assist:
            print("\nAttempting AI-assisted task completion...")
            tasks_completed = try_complete_tasks_with_ai(work_effort)
            if tasks_completed:
                print("✅ All tasks have been completed with AI assistance!")
            else:
                print("❌ Some tasks could not be completed automatically.")

        if not tasks_completed and not args.force:
            print("\n❌ Not all tasks are completed in this work effort.")
            if not args.no_confirmation:
                choice = input("Would you like to continue anyway? (y/n): ")
                if choice.lower() != 'y':
                    print("Operation cancelled. Please complete all tasks first.")
                    return 0
            else:
                print("Use --force to complete anyway or --ai-assist to attempt task completion.")
                return 1

    # Run tests if requested
    if args.run_tests:
        if not run_tests(work_effort):
            print("Tests failed. Aborting completion process.")
            return 1

    # Ask for confirmation unless --no-confirmation flag is set
    if not args.no_confirmation and (tasks_completed or args.force):
        confirm = input("\nDo you want to complete this work effort? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return 0

    # Try to complete the work effort using WorkflowRunner first
    success = complete_with_workflow_runner(work_effort)

    # If that fails, try using shell commands
    if not success:
        print("Trying alternative method...")
        success = complete_with_shell_commands(work_effort)

    # Update the devlog if requested and if the completion was successful
    if success and args.update_devlog:
        update_devlog(work_effort)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())