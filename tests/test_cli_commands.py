#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test CLI Commands

This script tests various CLI commands for the Code Conductor tool.
"""

import os
import sys
import json
import logging
import unittest
from datetime import datetime
from pathlib import Path

from setup_test_workspace import setup_test_workspace, teardown_test_workspace

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CodeConductorTests')

class TestCliCommands(unittest.TestCase):
    """Test cases for CLI commands."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        logger.info("Starting Code Conductor CLI tests...")
        cls.test_workspace = setup_test_workspace()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        teardown_test_workspace()
        logger.info("Test cleanup complete.")

    def setUp(self):
        """Set up each test."""
        os.chdir(self.project_root)  # Ensure we're in the project root

    def test_basic_commands(self):
        """Test basic CLI commands."""
        logger.info("Testing basic commands...")

        # Test help command
        result = os.system("code-conductor --help")
        self.assertEqual(result, 0, "Help command should succeed")

        # Test version command
        result = os.system("code-conductor --version")
        self.assertEqual(result, 0, "Version command should succeed")

    def test_setup_commands(self):
        """Test setup-related commands."""
        logger.info("Testing setup commands...")

        # Test setup command
        result = os.system("code-conductor setup")
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
        result = os.system("code-conductor new-work-effort --title 'Test Work Effort' --assignee 'Test User' --priority medium")
        self.assertEqual(result, 0, "Creating work effort should succeed")

        # Test listing work efforts
        result = os.system("code-conductor list")
        self.assertEqual(result, 0, "Listing work efforts should succeed")

        # Test creating a work effort with AI
        result = os.system("code-conductor new-work-effort --title 'AI Test' --use-ai --description 'Test description'")
        self.assertEqual(result, 0, "Creating work effort with AI should succeed")

    def test_manager_commands(self):
        """Test manager commands."""
        logger.info("Testing manager commands...")

        # Test creating a new manager
        result = os.system("code-conductor new-work-manager --manager-name 'TestManager2' --target-dir 'test_workspace/manager2'")
        self.assertEqual(result, 0, "Creating work manager should succeed")

        # Test listing managers
        result = os.system("code-conductor list-managers")
        self.assertEqual(result, 0, "Listing managers should succeed")

        # Test setting default manager
        result = os.system("code-conductor set-default --manager-name 'TestManager2'")
        self.assertEqual(result, 0, "Setting default manager should succeed")

    def test_status_commands(self):
        """Test status commands."""
        logger.info("Testing status commands...")

        # Create a work effort first
        os.system("code-conductor new-work-effort --title 'Status Test' --assignee 'Test User' --priority medium")

        # Test updating status
        result = os.system("code-conductor update-status --work-effort 'Status Test' --new-status completed")
        self.assertEqual(result, 0, "Updating work effort status should succeed")

    def test_root_commands(self):
        """Test root commands."""
        logger.info("Testing root commands...")

        # Test finding project root
        result = os.system("code-conductor find-root")
        self.assertEqual(result, 0, "Finding project root should succeed")

    def test_shorthand_commands(self):
        """Test shorthand commands."""
        logger.info("Testing shorthand commands...")

        # Test cc-work-e command
        result = os.system("cc-work-e --title 'Shorthand Test'")
        self.assertEqual(result, 0, "Shorthand work effort command should succeed")

        # Test cc-new command
        result = os.system("cc-new 'Quick Test' -p high -a 'Test User'")
        self.assertEqual(result, 0, "Quick new work effort command should succeed")

        # Test cc-index command
        result = os.system("cc-index")
        self.assertEqual(result, 0, "Index command should succeed")

def generate_test_report(test_results):
    """Generate a test report."""
    report_file = os.path.join("test_workspace", "test_report.md")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    with open(report_file, "w") as f:
        # Write report header
        f.write("# Code Conductor CLI Test Report\n")
        f.write(f"Generated on: {datetime.now().isoformat()}\n\n")

        # Write test summary
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results if result.get("success", False))
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        f.write("## Test Summary\n")
        f.write(f"- Total Tests: {total_tests}\n")
        f.write(f"- Successful Tests: {successful_tests}\n")
        f.write(f"- Failed Tests: {failed_tests}\n")
        f.write(f"- Success Rate: {success_rate:.2f}%\n\n")

        # Write detailed results
        f.write("## Detailed Results\n\n")
        for result in test_results:
            status = "✅" if result.get("success", False) else "❌"
            f.write(f"### {status} {result['name']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n\n")

            if "output" in result:
                f.write("Output:\n```\n")
                f.write(result["output"])
                f.write("\n```\n\n")

            if "error" in result:
                f.write("Error:\n```\n")
                f.write(result["error"])
                f.write("\n```\n")

    logger.info(f"Test report generated at: {report_file}")
    print(f"\nTest report generated successfully at: {report_file}")

if __name__ == "__main__":
    # Run tests and collect results
    test_results = []
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCliCommands)
    result = runner.run(suite)

    # Collect test results from the test case methods
    for test_method in dir(TestCliCommands):
        if test_method.startswith('test_'):
            test_result = {
                "name": test_method,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }

            # Check if the test failed
            for failure in result.failures:
                if failure[0]._testMethodName == test_method:
                    test_result["success"] = False
                    test_result["error"] = failure[1]
                    break

            # Check if the test had an error
            for error in result.errors:
                if error[0]._testMethodName == test_method:
                    test_result["success"] = False
                    test_result["error"] = error[1]
                    break

            test_results.append(test_result)

    # Generate test report
    generate_test_report(test_results)