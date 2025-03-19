#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Conductor Workflow Runner

This script guides users through the complete Code Conductor workflow process:
1. Create Work Effort Document
2. Add Context & Requirements
3. Create Script or Code
4. Execute & Test
5. Document Results
6. Refine Until Successful
7. Add Tests
8. Update All Documentation

Usage:
    python workflow_runner.py [--non-interactive] [--feature-name NAME]

Options:
    --non-interactive    Run in non-interactive mode with default values
    --feature-name NAME  Name of the feature to develop
"""

import os
import re
import sys
import argparse
import datetime
import subprocess

# Constants
WORK_EFFORTS_DIR = "_AI-Setup/work_efforts"
ACTIVE_DIR = f"{WORK_EFFORTS_DIR}/active"
COMPLETED_DIR = f"{WORK_EFFORTS_DIR}/completed"
ARCHIVED_DIR = f"{WORK_EFFORTS_DIR}/archived"
SCRIPTS_DIR = f"{WORK_EFFORTS_DIR}/scripts"
DEVLOG_PATH = f"{WORK_EFFORTS_DIR}/devlog.md"
CHANGELOG_PATH = "CHANGELOG.md"
TEMPLATE_PATH = f"{WORK_EFFORTS_DIR}/templates/work-effort-template.md"

# Template for devlog entries
DEVLOG_ENTRY_TEMPLATE = """## {date}

### {title}

{description}

**Work Effort**: [Link to Work Effort](active/{work_effort_filename})

---

"""

# Template for generated Python scripts
SCRIPT_TEMPLATE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{feature_name}

{description}

Usage:
    python {script_name}.py [options]

Options:
    --help    Show this help message
\"\"\"

import os
import sys
import argparse


def parse_args():
    \"\"\"Parse command line arguments.\"\"\"
    parser = argparse.ArgumentParser(description="{description}")
    # Add your arguments here
    return parser.parse_args()


def main():
    \"\"\"Main function.\"\"\"
    args = parse_args()
    print(f"Implementing {feature_name}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""

# Template for test scripts
TEST_TEMPLATE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Tests for {script_name}

This script tests the functionality of {script_name}.py

Usage:
    python test_{script_name}.py
\"\"\"

import os
import sys
import unittest

# Import the module to test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import {script_name}

class Test{class_name}(unittest.TestCase):
    \"\"\"Test the {feature_name} functionality.\"\"\"

    def test_basic_functionality(self):
        \"\"\"Test basic functionality.\"\"\"
        self.assertTrue(True)  # Placeholder assertion

if __name__ == "__main__":
    print(f"Running tests for {feature_name}...")
    unittest.main()
    print("Tests completed successfully!")
"""


class WorkflowRunner:
    """
    Guides users through the Code Conductor workflow process.
    """

    def __init__(self, interactive=True, work_efforts_dir=None, devlog_file=None, changelog_file=None):
        """
        Initialize the workflow runner.

        Args:
            interactive (bool): Whether to run in interactive mode
            work_efforts_dir (str): Path to the work efforts directory
            devlog_file (str): Path to the devlog file
            changelog_file (str): Path to the changelog file
        """
        self.interactive = interactive
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.time = datetime.datetime.now().strftime("%H:%M:%S")
        self.created = f"{self.date} {self.time}"

        # Initialize feature information
        self.feature_name = ""
        self.feature_title = ""
        self.feature_description = ""
        self.feature_priority = "medium"
        self.feature_tags = []
        self.assignee = "Unassigned"
        self.script_name = ""
        self.class_name = ""
        self.status = "active"

        # Set due date to 7 days from now
        due_date = datetime.datetime.now() + datetime.timedelta(days=7)
        self.due_date = due_date.strftime("%Y-%m-%d")
        self.last_updated = self.created

        # File paths
        self.work_effort_path = ""
        self.script_path = ""
        self.test_path = ""

        # Set up directories and paths
        self.work_efforts_dir = work_efforts_dir or WORK_EFFORTS_DIR
        self.active_dir = os.path.join(self.work_efforts_dir, "active")
        self.completed_dir = os.path.join(self.work_efforts_dir, "completed")
        self.archived_dir = os.path.join(self.work_efforts_dir, "archived")
        self.scripts_dir = os.path.join(self.work_efforts_dir, "scripts")
        self.devlog_path = devlog_file or DEVLOG_PATH
        self.changelog_path = changelog_file or CHANGELOG_PATH
        self.template_path = os.path.join(self.work_efforts_dir, "templates", "work-effort-template.md")

        # Ensure directories exist
        os.makedirs(self.active_dir, exist_ok=True)
        os.makedirs(self.scripts_dir, exist_ok=True)
        os.makedirs(self.completed_dir, exist_ok=True)
        os.makedirs(self.archived_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.template_path), exist_ok=True)

    def prompt(self, message, default=""):
        """
        Prompt the user for input.

        Args:
            message (str): The message to display
            default (str): Default value if running in non-interactive mode

        Returns:
            str: User input or default value
        """
        if not self.interactive:
            return default

        if default:
            response = input(f"{message} [{default}]: ").strip()
            return response if response else default
        else:
            return input(f"{message}: ").strip()

    def slugify(self, text):
        """
        Convert text to slug format (lowercase, spaces to underscores).

        Args:
            text (str): Text to slugify

        Returns:
            str: Slugified text
        """
        return re.sub(r'[^a-z0-9_]', '', text.lower().replace(' ', '_'))

    def get_template_content(self):
        """
        Get the content of the template file.
        If the template file doesn't exist, create a default one.

        Returns:
            str: The template content
        """
        if not os.path.exists(self.template_path):
            print(f"Template file not found at {self.template_path}, creating default template...")
            os.makedirs(os.path.dirname(self.template_path), exist_ok=True)

            # Default template content if the file doesn't exist
            default_template = """---
title: "{{title}}"
status: "{{status}}" # options: active, paused, completed
priority: "{{priority}}" # options: low, medium, high, critical
assignee: "{{assignee}}"
created: "{{created}}" # YYYY-MM-DD HH:mm
last_updated: "{{last_updated}}" # YYYY-MM-DD HH:mm
due_date: "{{due_date}}" # YYYY-MM-DD
tags: [{{tags}}]
---

# {{title}}

## 🚩 Objectives
- Clearly define goals for this work effort.

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references.

## 🐞 Issues Encountered
- Document issues and obstacles clearly.

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes.

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
            with open(self.template_path, 'w') as f:
                f.write(default_template)

            return default_template

        # Read the template file
        with open(self.template_path, 'r') as f:
            return f.read()

    def create_work_effort(self):
        """
        Step 1: Create a work effort document.
        """
        print("\n=== Step 1: Create Work Effort Document ===\n")

        # Get feature information
        if not self.feature_name:  # Only prompt if feature_name not already set
            self.feature_name = self.prompt("Feature name", "New Feature")
            self.feature_title = self.prompt("Feature title", self.feature_name)
            self.feature_description = self.prompt("Feature description", "A new feature for Code Conductor")
            self.feature_priority = self.prompt("Priority (low, medium, high, critical)", "medium")
            self.assignee = self.prompt("Assignee", "Unassigned")
            tags_input = self.prompt("Tags (comma-separated)", "feature, documentation")
            self.feature_tags = [tag.strip() for tag in tags_input.split(",")]

            # Generate derived properties from feature_name
            self.script_name = self.slugify(self.feature_name)
            self.class_name = ''.join(word.capitalize() for word in self.slugify(self.feature_name).split('_'))

        # Generate file name and paths
        work_effort_filename = f"{self.timestamp}_{self.script_name}.md"
        self.work_effort_path = os.path.join(self.active_dir, work_effort_filename)

        # Get template content
        template_content = self.get_template_content()

        # Create a dictionary of replacements
        replacements = {
            "{{title}}": self.feature_title,
            "{{status}}": self.status,
            "{{priority}}": self.feature_priority,
            "{{assignee}}": self.assignee,
            "{{created}}": self.created,
            "{{last_updated}}": self.last_updated,
            "{{due_date}}": self.due_date,
            "{{tags}}": ", ".join(self.feature_tags)
        }

        # Replace placeholders in the template
        content = template_content
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Write the work effort file
        with open(self.work_effort_path, 'w') as f:
            f.write(content)

        print(f"✅ Created work effort document: {self.work_effort_path}")

        # Update the devlog
        self.update_devlog(work_effort_filename)

        return work_effort_filename

    def update_devlog(self, work_effort_filename):
        """
        Update the devlog with a new entry.

        Args:
            work_effort_filename (str): The filename of the work effort
        """
        if os.path.exists(self.devlog_path):
            with open(self.devlog_path, 'r') as f:
                content = f.read()

            # Create new devlog entry
            new_entry = DEVLOG_ENTRY_TEMPLATE.format(
                date=self.date,
                title=self.feature_title,
                description=self.feature_description,
                work_effort_filename=work_effort_filename
            )

            # Add to the beginning of the devlog
            updated_content = "# Development Log\n\n" + new_entry + content[len("# Development Log"):]

            with open(self.devlog_path, 'w') as f:
                f.write(updated_content)

            print(f"✅ Updated devlog: {self.devlog_path}")
        else:
            print(f"⚠️ Devlog not found at {self.devlog_path}, skipping update")

    def create_script(self):
        """
        Step 3: Create script or code.
        """
        print("\n=== Step 3: Create Script or Code ===\n")

        # Generate script path in the scripts directory
        self.script_path = os.path.join(self.scripts_dir, f"{self.script_name}.py")

        # Create script content
        content = SCRIPT_TEMPLATE.format(
            feature_name=self.feature_name,
            description=self.feature_description,
            script_name=self.script_name
        )

        # Write the script file
        with open(self.script_path, 'w') as f:
            f.write(content)

        # Make the script executable
        os.chmod(self.script_path, 0o755)

        print(f"✅ Created script: {self.script_path}")
        return self.script_path

    def execute_and_test(self):
        """
        Step 4: Execute and test the script.
        """
        print("\n=== Step 4: Execute & Test ===\n")

        # Run the script
        print(f"Executing {self.script_path}...")
        try:
            result = subprocess.run(['python3', self.script_path], capture_output=True, text=True)

            print("\nExecution Results:")
            print("-" * 50)
            print(f"Return code: {result.returncode}")
            print("\nStandard output:")
            print(result.stdout or "(No output)")

            if result.stderr:
                print("\nStandard error:")
                print(result.stderr)

            if result.returncode == 0:
                print("\n✅ Script executed successfully")
            else:
                print("\n⚠️ Script execution failed")

        except Exception as e:
            print(f"Error executing script: {e}")

    def document_results(self):
        """
        Step 5: Document the results.
        """
        print("\n=== Step 5: Document Results ===\n")

        if self.interactive:
            print("Please document the results of testing:")
            print("1. Did the script execute as expected?")
            print("2. Are there any issues or improvements needed?")
            print("3. What next steps are required?")

            results = input("\nEnter your observations (press Enter twice to finish):\n")

            # Update the work effort file with results
            if results and os.path.exists(self.work_effort_path):
                with open(self.work_effort_path, 'r') as f:
                    content = f.read()

                # Update the Outcomes & Results section
                if "## ✅ Outcomes & Results" in content:
                    updated_content = content.replace(
                        "## ✅ Outcomes & Results\n- Explicitly log outcomes, lessons learned, and code changes.",
                        f"## ✅ Outcomes & Results\n- Testing results: {results.strip()}"
                    )

                    with open(self.work_effort_path, 'w') as f:
                        f.write(updated_content)

                    print(f"✅ Updated work effort with testing results")

    def add_tests(self):
        """
        Step 7: Add tests.
        """
        print("\n=== Step 7: Add Tests ===\n")

        # Generate test path in the scripts directory
        self.test_path = os.path.join(self.scripts_dir, f"test_{self.script_name}.py")

        # Create test content
        content = TEST_TEMPLATE.format(
            script_name=self.script_name,
            class_name=self.class_name,
            feature_name=self.feature_name
        )

        # Write the test file
        with open(self.test_path, 'w') as f:
            f.write(content)

        # Make the test executable
        os.chmod(self.test_path, 0o755)

        print(f"✅ Created test script: {self.test_path}")

        # Run the tests
        if self.interactive and self.prompt("Would you like to run the tests? (y/n)", "y").lower() == 'y':
            print(f"Running tests in {self.test_path}...")
            try:
                result = subprocess.run(['python3', self.test_path], capture_output=True, text=True)

                print("\nTest Results:")
                print("-" * 50)
                print(f"Return code: {result.returncode}")
                print("\nStandard output:")
                print(result.stdout or "(No output)")

                if result.stderr:
                    print("\nStandard error:")
                    print(result.stderr)

                if result.returncode == 0:
                    print("\n✅ Tests passed")
                else:
                    print("\n⚠️ Tests failed")

            except Exception as e:
                print(f"Error running tests: {e}")

        return self.test_path

    def update_work_effort_status(self, new_status):
        """
        Update the status of a work effort and move it to the appropriate directory.

        Args:
            new_status (str): The new status of the work effort (active, completed, archived, paused)

        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(self.work_effort_path):
            print(f"❌ Work effort not found at {self.work_effort_path}")
            return False

        # Read the current content
        with open(self.work_effort_path, 'r') as f:
            content = f.read()

        # Update the status in the content
        # Use regex to replace status line in frontmatter
        status_pattern = r'status: "(active|completed|archived|paused)"'
        replacement = f'status: "{new_status}"'

        if re.search(status_pattern, content):
            updated_content = re.sub(status_pattern, replacement, content)
        else:
            print(f"❌ Status field not found in work effort document")
            return False

        # Determine the target directory
        if new_status == "active":
            target_dir = self.active_dir
        elif new_status == "completed":
            target_dir = self.completed_dir
        elif new_status == "archived":
            target_dir = self.archived_dir
        else:
            # For "paused" or other statuses, keep in active directory
            target_dir = self.active_dir

        # Get just the filename from the path
        filename = os.path.basename(self.work_effort_path)
        target_path = os.path.join(target_dir, filename)

        # Write the updated content to the new location
        try:
            # Create the updated file
            with open(target_path, 'w') as f:
                f.write(updated_content)

            # If the target path is different from the current path, remove the old file
            if target_path != self.work_effort_path:
                os.remove(self.work_effort_path)

            # Update the work effort path
            self.work_effort_path = target_path
            self.status = new_status

            print(f"✅ Updated work effort status to '{new_status}' and moved to {target_dir}")
            return True
        except Exception as e:
            print(f"❌ Error updating work effort status: {str(e)}")
            return False

    def update_documentation(self):
        """
        Step 8: Update all documentation.
        """
        print("\n=== Step 8: Update All Documentation ===\n")

        # Update work effort status if completed
        if self.interactive:
            status_choice = self.prompt("Would you like to update the work effort status? (active/completed/archived/paused)", "active")
            if status_choice != "active":
                self.update_work_effort_status(status_choice)

        # Update CHANGELOG if it exists
        if os.path.exists(self.changelog_path) and self.interactive:
            if self.prompt("Would you like to update the CHANGELOG? (y/n)", "y").lower() == 'y':
                print("Enter the changelog entry for the Unreleased section:")
                entry = input("- ")

                if entry:
                    with open(self.changelog_path, 'r') as f:
                        content = f.read()

                    # Find the Unreleased section and add entry
                    if "## [Unreleased]" in content:
                        # Find where to add the entry
                        unreleased_pos = content.find("## [Unreleased]")
                        added_pos = content.find("### Added", unreleased_pos)

                        if added_pos > -1:
                            # Insert after "### Added" line
                            insert_pos = content.find("\n", added_pos) + 1
                            updated_content = (
                                content[:insert_pos] +
                                f"- {entry}\n" +
                                content[insert_pos:]
                            )

                            with open(self.changelog_path, 'w') as f:
                                f.write(updated_content)

                            print(f"✅ Updated CHANGELOG: {self.changelog_path}")

        # Validate documentation
        self.validate_documentation()

    def validate_documentation(self):
        """
        Validate that all necessary documentation has been updated.
        """
        checks = [
            ("Work Effort Document", os.path.exists(self.work_effort_path)),
            ("Script", os.path.exists(self.script_path)),
            ("Tests", os.path.exists(self.test_path)),
            ("Devlog Entry", os.path.exists(self.devlog_path))
        ]

        print("\nDocumentation Checklist:")
        for name, exists in checks:
            status = "✅" if exists else "❌"
            print(f"{status} {name}")

        if all(exists for _, exists in checks):
            print("\n🎉 All required documentation has been created!")
        else:
            print("\n⚠️ Some documentation is missing. Please review and complete.")

    def run_workflow(self):
        """
        Run the complete workflow process.
        """
        print("\n🚀 Starting Code Conductor Workflow Process\n")

        # 1. Create Work Effort Document
        work_effort_filename = self.create_work_effort()

        # 2. Add Context & Requirements
        print("\n=== Step 2: Add Context & Requirements ===\n")
        print(f"Please edit {self.work_effort_path} to add:")
        print("- Specific goals for this feature")
        print("- Functional and non-functional requirements")
        print("- Acceptance criteria")
        print("- Implementation plan")

        if self.interactive:
            input("\nPress Enter when you've completed this step...")

        # 3. Create Script or Code
        self.create_script()

        # 4. Execute & Test
        self.execute_and_test()

        # 5. Document Results
        self.document_results()

        # 6. Refine Until Successful
        print("\n=== Step 6: Refine Until Successful ===\n")
        print("The script has been created and tested.")
        print("You should now:")
        print("1. Review the test results")
        print("2. Make necessary improvements to the script")
        print("3. Re-test until satisfied")

        if self.interactive:
            input("\nPress Enter when you're ready to proceed to adding tests...")

        # 7. Add Tests
        self.add_tests()

        # 8. Update All Documentation
        self.update_documentation()

        print("\n🎉 Workflow process completed successfully!")
        print("\nCreated files:")
        print(f"- Work Effort: {self.work_effort_path}")
        print(f"- Script: {self.script_path}")
        print(f"- Tests: {self.test_path}")

        print("\nNext steps:")
        print("1. Complete the implementation of your feature")
        print("2. Expand test coverage for your feature")
        print("3. Finalize documentation")
        print("4. Commit your changes to version control")

        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the Code Conductor workflow process")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run in non-interactive mode with default values")
    parser.add_argument("--feature-name", type=str,
                        help="Name of the feature to develop")
    args = parser.parse_args()

    # Create the workflow runner
    runner = WorkflowRunner(interactive=not args.non_interactive)

    # Set feature name if provided
    if args.feature_name:
        # Set all feature-related properties before running the workflow
        runner.feature_name = args.feature_name
        runner.feature_title = args.feature_name
        runner.feature_description = f"Implementation of {args.feature_name}"
        runner.script_name = runner.slugify(args.feature_name)
        runner.class_name = ''.join(word.capitalize() for word in runner.script_name.split('_'))

        print(f"Using provided feature name: {args.feature_name}")
        print(f"Script name will be: {runner.script_name}.py")
        print(f"Script will be created at: {os.path.join(runner.scripts_dir, f'{runner.script_name}.py')}")

    # Run the workflow
    return runner.run_workflow()


if __name__ == "__main__":
    sys.exit(main())