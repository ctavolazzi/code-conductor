#!/usr/bin/env python3
"""
Test script for workflow_runner.py which tests the basic functionality of the workflow runner.

This test suite validates that the workflow runner can:
1. Create work effort documents
2. Update the devlog
3. Create script files
4. Execute scripts and capture output
5. Add test files
6. Update documentation

Usage:
    python test_workflow_runner.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

# Import the workflow runner module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import src.code_conductor.workflow.workflow_runner
from src.code_conductor.workflow.workflow_runner import WorkflowRunner

class TestWorkflowRunner(unittest.TestCase):
    """Test suite for the WorkflowRunner class"""

    def setUp(self):
        """Set up test environment with temporary directories"""
        self.temp_dir = tempfile.mkdtemp()

        # Create temporary directories for work efforts, devlog, etc.
        self.work_efforts_dir = os.path.join(self.temp_dir, "work_efforts")
        self.active_dir = os.path.join(self.work_efforts_dir, "active")
        os.makedirs(self.active_dir, exist_ok=True)

        # Create a temporary devlog file
        self.devlog_file = os.path.join(self.work_efforts_dir, "devlog.md")
        with open(self.devlog_file, "w") as f:
            f.write("# Development Log\n\n")

        # Create a temporary changelog file
        self.changelog_file = os.path.join(self.temp_dir, "CHANGELOG.md")
        with open(self.changelog_file, "w") as f:
            f.write("# Changelog\n\n## [Unreleased]\n\n### Added\n\n### Changed\n\n")

        # Save original constants
        self.original_work_efforts_dir = workflow_runner.WORK_EFFORTS_DIR
        self.original_active_dir = workflow_runner.ACTIVE_DIR
        self.original_devlog_path = workflow_runner.DEVLOG_PATH
        self.original_changelog_path = workflow_runner.CHANGELOG_PATH

        # Override constants for testing
        workflow_runner.WORK_EFFORTS_DIR = self.work_efforts_dir
        workflow_runner.ACTIVE_DIR = self.active_dir
        workflow_runner.DEVLOG_PATH = self.devlog_file
        workflow_runner.CHANGELOG_PATH = self.changelog_file

        # Initialize the workflow runner with non-interactive mode
        self.workflow_runner = WorkflowRunner(interactive=False)

    def tearDown(self):
        """Clean up temporary directories after tests"""
        # Restore original constants
        workflow_runner.WORK_EFFORTS_DIR = self.original_work_efforts_dir
        workflow_runner.ACTIVE_DIR = self.original_active_dir
        workflow_runner.DEVLOG_PATH = self.original_devlog_path
        workflow_runner.CHANGELOG_PATH = self.original_changelog_path

        shutil.rmtree(self.temp_dir)

    @patch('builtins.input')
    def test_create_work_effort(self, mock_input):
        """Test creating a work effort document"""
        # Mock user inputs
        mock_input.side_effect = [
            "Test Feature",  # Feature name
            "This is a test feature",  # Description
            "Testing",  # Category
            "Low"  # Priority
        ]

        # Set feature information directly
        self.workflow_runner.feature_name = "Test Feature"
        self.workflow_runner.feature_title = "Test Feature"
        self.workflow_runner.feature_description = "This is a test feature"
        self.workflow_runner.feature_priority = "Low"
        self.workflow_runner.feature_tags = ["Testing"]

        # Create the work effort
        work_effort_filename = self.workflow_runner.create_work_effort()
        work_effort_path = os.path.join(self.active_dir, work_effort_filename)

        # Check that the file was created
        self.assertTrue(os.path.exists(work_effort_path))

        # Check the content of the file
        with open(work_effort_path, "r") as f:
            content = f.read()
            self.assertIn("# Test Feature", content)
            self.assertIn("This is a test feature", content)
            self.assertIn("priority: \"Low\"", content)

    def test_update_devlog(self):
        """Test updating the devlog"""
        # Create a mock work effort filename
        work_effort_filename = "test_feature.md"
        work_effort_path = os.path.join(self.active_dir, work_effort_filename)
        with open(work_effort_path, "w") as f:
            f.write("---\ntitle: Test Feature\ndescription: This is a test feature\n---\n\n# Test Feature\n")

        # Set feature information directly
        self.workflow_runner.feature_name = "Test Feature"
        self.workflow_runner.feature_title = "Test Feature"
        self.workflow_runner.feature_description = "This is a test feature"

        # Update the devlog
        self.workflow_runner.update_devlog(work_effort_filename)

        # Check that the devlog was updated
        with open(self.devlog_file, "r") as f:
            content = f.read()
            self.assertIn("Test Feature", content)
            self.assertIn("This is a test feature", content)

    def test_create_script(self):
        """Test creating a script file"""
        # Set feature information directly
        self.workflow_runner.feature_name = "Test Feature"
        self.workflow_runner.feature_description = "This is a test feature"
        self.workflow_runner.script_name = "test_feature"

        # Create the script
        script_path = self.workflow_runner.create_script()

        # Check that the script was created
        self.assertTrue(os.path.exists(script_path))

        # Check the content of the script
        with open(script_path, "r") as f:
            content = f.read()
            self.assertIn("#!/usr/bin/env python3", content)
            self.assertIn("Test Feature", content)
            self.assertIn("This is a test feature", content)

    @patch('subprocess.run')
    def test_execute_and_test(self, mock_run):
        """Test executing and testing a script"""
        # Mock the subprocess.run function
        mock_process = MagicMock()
        mock_process.stdout = "Test output"
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # Create a mock script path
        self.workflow_runner.script_path = os.path.join(self.temp_dir, "test_feature.py")
        with open(self.workflow_runner.script_path, "w") as f:
            f.write("#!/usr/bin/env python3\nprint('Test output')")

        # Make the script executable
        os.chmod(self.workflow_runner.script_path, 0o755)

        # Execute and test the script
        self.workflow_runner.execute_and_test()

        # Verify subprocess.run was called
        mock_run.assert_called()

    def test_add_tests(self):
        """Test adding a test file"""
        # Set feature information directly
        self.workflow_runner.feature_name = "Test Feature"
        self.workflow_runner.script_name = "test_feature"
        self.workflow_runner.class_name = "TestFeature"
        self.workflow_runner.script_path = os.path.join(self.temp_dir, "test_feature.py")

        # Create script file
        with open(self.workflow_runner.script_path, "w") as f:
            f.write("#!/usr/bin/env python3\nprint('Test output')")

        # Add a test file
        test_path = self.workflow_runner.add_tests()

        # Check that the test file was created
        self.assertTrue(os.path.exists(test_path))

        # Check the content of the test file
        with open(test_path, "r") as f:
            content = f.read()
            self.assertIn("#!/usr/bin/env python3", content)
            self.assertIn("unittest", content)
            self.assertIn("test_feature", content)

    def test_update_documentation(self):
        """Test updating documentation"""
        # Set feature information directly
        self.workflow_runner.work_effort_path = os.path.join(self.active_dir, "test_feature.md")
        with open(self.workflow_runner.work_effort_path, "w") as f:
            f.write("---\ntitle: Test Feature\ndescription: This is a test feature\n---\n\n# Test Feature\n")

        # Update documentation
        self.workflow_runner.update_documentation()

if __name__ == "__main__":
    unittest.main()