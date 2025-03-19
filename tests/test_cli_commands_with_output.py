#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test CLI Commands with Output Capture

This script tests various CLI commands for the Code Conductor tool and saves
the output from each command to a file for analysis.
"""

import os
import sys
import json
import logging
import unittest
import subprocess
from datetime import datetime
from pathlib import Path

from setup_test_workspace import setup_test_workspace, teardown_test_workspace

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CodeConductorTests')

class TestCliCommandsWithOutput(unittest.TestCase):
    """Test cases for CLI commands with output capture."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        logger.info("Starting Code Conductor CLI tests with output capture...")
        cls.test_workspace = setup_test_workspace()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Create output directory
        cls.output_dir = os.path.join(cls.project_root, "test_outputs")
        os.makedirs(cls.output_dir, exist_ok=True)

        # Initialize results dictionary
        cls.test_results = {
            "timestamp": datetime.now().isoformat(),
            "commands": {}
        }

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment and save results."""
        teardown_test_workspace()

        # Save results to file
        output_file = os.path.join(cls.output_dir, f"cli_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, 'w') as f:
            json.dump(cls.test_results, f, indent=2)

        logger.info(f"Test results saved to: {output_file}")
        logger.info("Test cleanup complete.")

    def setUp(self):
        """Set up each test."""
        os.chdir(self.project_root)  # Ensure we're in the project root

    def run_command(self, command, test_name):
        """Run a command and capture its output."""
        logger.info(f"Running command: {command}")

        # Run the command and capture output
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        # Store the results
        self.test_results["commands"][test_name] = {
            "command": command,
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "timestamp": datetime.now().isoformat()
        }

        return process.returncode

    def test_basic_commands(self):
        """Test basic CLI commands."""
        logger.info("Testing basic commands...")

        # Test help command
        result = self.run_command("code-conductor --help", "help_command")
        self.assertEqual(result, 0, "Help command should succeed")

        # Test version command
        result = self.run_command("code-conductor --version", "version_command")
        self.assertEqual(result, 0, "Version command should succeed")

    def test_setup_commands(self):
        """Test setup-related commands."""
        logger.info("Testing setup commands...")

        # Test setup command
        result = self.run_command("code-conductor setup", "setup_command")
        self.assertEqual(result, 0, "Setup command should succeed")

        # Verify directory structure
        self.assertTrue(os.path.exists(os.path.join(self.test_workspace, "work_efforts")))
        self.assertTrue(os.path.exists(os.path.join(self.test_workspace, "work_efforts", "active")))
        self.assertTrue(os.path.exists(os.path.join(self.test_workspace, "work_efforts", "completed")))
        self.assertTrue(os.path.exists(os.path.join(self.test_workspace, "work_efforts", "archived")))

    def test_work_effort_commands(self):
        """Test work effort commands."""
        logger.info("Testing work effort commands...")

        # Test creating a work effort
        result = self.run_command(
            "code-conductor new-work-effort --title 'Test Work Effort' --assignee 'Test User' --priority medium",
            "create_work_effort"
        )
        self.assertEqual(result, 0, "Creating work effort should succeed")

        # Test listing work efforts
        result = self.run_command("code-conductor list", "list_work_efforts")
        self.assertEqual(result, 0, "Listing work efforts should succeed")

        # Test creating a work effort with AI
        result = self.run_command(
            "code-conductor new-work-effort --title 'AI Test' --use-ai --description 'Test description'",
            "create_ai_work_effort"
        )
        self.assertEqual(result, 0, "Creating work effort with AI should succeed")

    def test_manager_commands(self):
        """Test manager commands."""
        logger.info("Testing manager commands...")

        # Test creating a new manager
        result = self.run_command(
            "code-conductor new-work-manager --manager-name 'TestManager2' --target-dir 'test_workspace/manager2'",
            "create_manager"
        )
        self.assertEqual(result, 0, "Creating work manager should succeed")

        # Test listing managers
        result = self.run_command("code-conductor list-managers", "list_managers")
        self.assertEqual(result, 0, "Listing managers should succeed")

        # Test setting default manager
        result = self.run_command(
            "code-conductor set-default --manager-name 'TestManager2'",
            "set_default_manager"
        )
        self.assertEqual(result, 0, "Setting default manager should succeed")

    def test_status_commands(self):
        """Test status commands."""
        logger.info("Testing status commands...")

        # Create a work effort first
        self.run_command(
            "code-conductor new-work-effort --title 'Status Test' --assignee 'Test User' --priority medium",
            "create_status_test_work_effort"
        )

        # Test updating status
        result = self.run_command(
            "code-conductor update-status --work-effort 'Status Test' --new-status completed",
            "update_status"
        )
        self.assertEqual(result, 0, "Updating work effort status should succeed")

    def test_root_commands(self):
        """Test root commands."""
        logger.info("Testing root commands...")

        # Test finding project root
        result = self.run_command("code-conductor find-root", "find_root")
        self.assertEqual(result, 0, "Finding project root should succeed")

    def test_shorthand_commands(self):
        """Test shorthand commands."""
        logger.info("Testing shorthand commands...")

        # Test cc-work-e command
        result = self.run_command("cc-work-e --title 'Shorthand Test'", "cc_work_e")
        self.assertEqual(result, 0, "Shorthand work effort command should succeed")

        # Test cc-new command
        result = self.run_command("cc-new 'Quick Test' -p high -a 'Test User'", "cc_new")
        self.assertEqual(result, 0, "Quick new work effort command should succeed")

        # Test cc-index command
        result = self.run_command("cc-index", "cc_index")
        self.assertEqual(result, 0, "Index command should succeed")

if __name__ == "__main__":
    # Run tests and collect results
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCliCommandsWithOutput)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())