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
import json
import shutil
import argparse
import datetime
import subprocess
from pathlib import Path

# Constants
WORK_EFFORTS_DIR = ".AI-Setup/work_efforts"
ACTIVE_DIR = f"{WORK_EFFORTS_DIR}/active"
DEVLOG_PATH = f"{WORK_EFFORTS_DIR}/devlog.md"
CHANGELOG_PATH = "CHANGELOG.md"
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

    # TODO: Implement your feature here
    print("Implementing {feature_name}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
"""

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
from pathlib import Path

# Import the module to test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import {script_name}


class Test{class_name}(unittest.TestCase):
    \"\"\"Test the {feature_name} functionality.\"\"\"

    def setUp(self):
        \"\"\"Set up the test environment.\"\"\"
        # TODO: Set up test environment
        pass

    def tearDown(self):
        \"\"\"Clean up after the tests.\"\"\"
        # TODO: Clean up test environment
        pass

    def test_basic_functionality(self):
        \"\"\"Test basic functionality.\"\"\"
        # TODO: Implement basic test
        self.assertTrue(True)  # Placeholder assertion


def run_tests():
    \"\"\"Run the test suite.\"\"\"
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    print("Running tests for {feature_name}...")
    run_tests()
    print("Tests completed successfully!")
"""

WORK_EFFORT_TEMPLATE = """---
title: "{title}"
created: "{created}"
priority: "{priority}"
status: "active"
tags: {tags}
---

# {title}

## Overview

{description}

## Goals

- TODO: Define specific goals for this feature

## Requirements

- TODO: List functional requirements
- TODO: List non-functional requirements

## Acceptance Criteria

- TODO: Define how success will be measured

## Implementation Plan

1. TODO: Step 1
2. TODO: Step 2
3. TODO: Step 3

## Progress

### Phase 1: Initial Implementation

**Status**: Not started

**Notes**:
- Initial planning completed

### Phase 2: Testing & Refinement

**Status**: Not started

**Notes**:
- Tests not yet implemented

### Phase 3: Documentation & Integration

**Status**: Not started

**Notes**:
- Documentation to be created

## Related Work

- TODO: Link related work efforts using `[[document]]` syntax
"""

DEVLOG_ENTRY_TEMPLATE = """## {date}: {title}

**Goal:** {description}

### Completed:

1. **Planning & Setup**
   - Created work effort document
   - Defined goals and requirements
   - Established implementation plan

2. **Initial Implementation**
   - TODO: Document implementation details
   - TODO: Note any challenges encountered
   - TODO: Describe approach taken

3. **Testing & Validation**
   - TODO: Document testing process
   - TODO: Summarize test results
   - TODO: Note any performance considerations

TODO: Add a brief summary of the feature and its value to the project.

Related to: [[{work_effort_filename}]]

"""


class WorkflowRunner:
    """
    Guides users through the Code Conductor workflow process.
    """

    def __init__(self, interactive=True):
        """
        Initialize the workflow runner.

        Args:
            interactive (bool): Whether to run in interactive mode
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
        self.script_name = ""
        self.class_name = ""

        # File paths
        self.work_effort_path = ""
        self.script_path = ""
        self.test_path = ""

        # Ensure directories exist
        os.makedirs(ACTIVE_DIR, exist_ok=True)

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

    def create_work_effort(self):
        """
        Step 1: Create a work effort document.
        """
        print("\n=== Step 1: Create Work Effort Document ===\n")

        # Get feature information
        self.feature_name = self.prompt("Feature name", "New Feature")
        self.feature_title = self.prompt("Feature title", self.feature_name)
        self.feature_description = self.prompt("Feature description", "A new feature for Code Conductor")
        self.feature_priority = self.prompt("Priority (low, medium, high)", "medium")
        tags_input = self.prompt("Tags (comma-separated)", "feature, documentation")
        self.feature_tags = [tag.strip() for tag in tags_input.split(",")]

        # Generate file name and paths
        self.script_name = self.slugify(self.feature_name)
        self.class_name = ''.join(word.capitalize() for word in self.slugify(self.feature_name).split('_'))
        work_effort_filename = f"{self.timestamp}_{self.slugify(self.feature_name)}.md"
        self.work_effort_path = os.path.join(ACTIVE_DIR, work_effort_filename)

        # Create work effort content
        content = WORK_EFFORT_TEMPLATE.format(
            title=self.feature_title,
            created=self.created,
            priority=self.feature_priority,
            tags=json.dumps(self.feature_tags),
            description=self.feature_description
        )

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
        if os.path.exists(DEVLOG_PATH):
            with open(DEVLOG_PATH, 'r') as f:
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

            with open(DEVLOG_PATH, 'w') as f:
                f.write(updated_content)

            print(f"✅ Updated devlog: {DEVLOG_PATH}")
        else:
            print(f"⚠️ Devlog not found at {DEVLOG_PATH}, skipping update")

    def create_script(self):
        """
        Step 3: Create script or code.
        """
        print("\n=== Step 3: Create Script or Code ===\n")

        # Generate script path
        self.script_path = f"{self.script_name}.py"

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
            result = subprocess.run(['python', self.script_path], capture_output=True, text=True)

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

                # Add results to the Progress section
                if "## Progress" in content:
                    updated_content = content.replace(
                        "**Notes**:\n- Initial planning completed",
                        f"**Notes**:\n- Initial planning completed\n- Testing results: {results.strip()}"
                    )

                    with open(self.work_effort_path, 'w') as f:
                        f.write(updated_content)

                    print(f"✅ Updated work effort with testing results")

    def add_tests(self):
        """
        Step 7: Add tests.
        """
        print("\n=== Step 7: Add Tests ===\n")

        # Generate test path
        self.test_path = f"test_{self.script_name}.py"

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
                result = subprocess.run(['python', self.test_path], capture_output=True, text=True)

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

    def update_documentation(self):
        """
        Step 8: Update all documentation.
        """
        print("\n=== Step 8: Update All Documentation ===\n")

        # Update CHANGELOG if it exists
        if os.path.exists(CHANGELOG_PATH) and self.interactive:
            if self.prompt("Would you like to update the CHANGELOG? (y/n)", "y").lower() == 'y':
                print("Enter the changelog entry for the Unreleased section:")
                entry = input("- ")

                if entry:
                    with open(CHANGELOG_PATH, 'r') as f:
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

                            with open(CHANGELOG_PATH, 'w') as f:
                                f.write(updated_content)

                            print(f"✅ Updated CHANGELOG: {CHANGELOG_PATH}")

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
            ("Devlog Entry", os.path.exists(DEVLOG_PATH))
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Code Conductor workflow process")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run in non-interactive mode with default values")
    parser.add_argument("--feature-name", type=str,
                        help="Name of the feature to develop")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()

    # Create and run the workflow
    runner = WorkflowRunner(interactive=not args.non_interactive)

    # Set feature name if provided
    if args.feature_name:
        runner.feature_name = args.feature_name

    # Run the workflow
    return runner.run_workflow()


if __name__ == "__main__":
    sys.exit(main())