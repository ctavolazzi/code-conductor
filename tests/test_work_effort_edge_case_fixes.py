#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the edge case fixes in the WorkEffortManager.

These tests verify that the WorkEffortManager properly handles various edge cases
like invalid inputs, special characters, long titles, etc.
"""

import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime
import string
import random

# Add parent directory to path to import work_efforts modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import WorkEffortManager
from code_conductor.core.work_effort.manager import WorkEffortManager


class TestWorkEffortManagerEdgeCaseFixes(unittest.TestCase):
    """Test the edge case fixes for the WorkEffortManager."""

    def setUp(self):
        """Set up a test environment with necessary directories."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create required directories
        self.work_efforts_dir = os.path.join(self.test_dir, "work_efforts")
        self.active_dir = os.path.join(self.work_efforts_dir, "active")
        self.completed_dir = os.path.join(self.work_efforts_dir, "completed")
        self.archived_dir = os.path.join(self.work_efforts_dir, "archived")
        self.templates_dir = os.path.join(self.work_efforts_dir, "templates")
        self.ai_setup_dir = os.path.join(self.test_dir, "_AI-Setup")

        os.makedirs(self.work_efforts_dir, exist_ok=True)
        os.makedirs(self.active_dir, exist_ok=True)
        os.makedirs(self.completed_dir, exist_ok=True)
        os.makedirs(self.archived_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic config for testing
        self.config = {
            "directories": {
                "active": "work_efforts/active",
                "completed": "work_efforts/completed",
                "archived": "work_efforts/archived",
                "templates": "work_efforts/templates"
            }
        }

        # Initialize the WorkEffortManager with our test configuration
        self.manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up after tests."""
        # Stop the manager if it's running
        if hasattr(self, 'manager') and self.manager:
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_empty_title(self):
        """Test that empty titles are rejected."""
        result = self.manager.create_work_effort(
            title="",
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )
        self.assertIsNone(result, "Empty title should result in None")

    def test_none_title(self):
        """Test that None titles are rejected."""
        result = self.manager.create_work_effort(
            title=None,
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )
        self.assertIsNone(result, "None title should result in None")

    def test_special_characters_in_title(self):
        """Test that special characters in titles are properly sanitized."""
        title = 'Test: Special "Characters" / \\ * ? < > |'
        result = self.manager.create_work_effort(
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )
        self.assertIsNotNone(result, "Should handle special characters in title")
        self.assertTrue(os.path.exists(result), "File should be created")

        # Check that the file contains the original title
        with open(result, 'r') as f:
            content = f.read()
            self.assertIn(title, content, "Original title should be preserved in content")

        # The filename should not contain special characters
        filename = os.path.basename(result)
        special_chars = r':"*/\?<>|'
        for char in special_chars:
            self.assertNotIn(char, filename, f"Filename should not contain {char}")

    def test_extremely_long_title(self):
        """Test that extremely long titles are truncated in the filename."""
        # Create a 500-character title
        long_title = "A" * 500

        result = self.manager.create_work_effort(
            title=long_title,
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )
        self.assertIsNotNone(result, "Should handle extremely long title")
        self.assertTrue(os.path.exists(result), "File should be created")

        # Check that the filename is shorter than the title
        filename = os.path.basename(result)
        # Filename should be much shorter than the title (including timestamp, etc.)
        self.assertLess(len(filename), 250, "Filename should be truncated")

        # The content should still have the full title
        with open(result, 'r') as f:
            content = f.read()
            self.assertIn(long_title, content, "Full title should be preserved in content")

    def test_invalid_date_format(self):
        """Test that invalid date formats are rejected."""
        result = self.manager.create_work_effort(
            title="Test Work Effort",
            assignee="tester",
            priority="medium",
            due_date="invalid-date"
        )
        self.assertIsNone(result, "Invalid date format should result in None")

    def test_directory_existence(self):
        """Test that directories are created if they don't exist."""
        # Remove the active directory
        shutil.rmtree(self.active_dir)

        # Try to create a work effort
        result = self.manager.create_work_effort(
            title="Test Directory Creation",
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )

        # The manager should recreate the directory
        self.assertIsNotNone(result, "Should recreate missing directory")
        self.assertTrue(os.path.exists(result), "File should be created")
        self.assertTrue(os.path.isdir(self.active_dir), "Active directory should be recreated")

    def test_status_update_with_sanitization(self):
        """Test updating work effort status with sanitized titles."""
        # Create a work effort with special characters
        title = 'Status Test: Special "Characters" / \\ * ? < > |'
        original_path = self.manager.create_work_effort(
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2023-06-15"
        )

        # Get the filename
        filename = os.path.basename(original_path)

        # Update the status
        result = self.manager.update_work_effort_status(
            filename=filename,
            new_status="completed",
            old_status="active"
        )

        self.assertTrue(result, "Status update should succeed")

        # The original file should be gone
        self.assertFalse(os.path.exists(original_path), "Original file should be moved")

        # The file should now be in the completed directory
        new_path = os.path.join(self.completed_dir, filename)
        self.assertTrue(os.path.exists(new_path), "File should be in completed directory")

        # Check that the status was updated in the file
        with open(new_path, 'r') as f:
            content = f.read()
            self.assertIn('status: "completed"', content, "Status should be updated in content")
            self.assertNotIn('status: "active"', content, "Old status should not be in content")

    def test_concurrent_operations_simulation(self):
        """
        Test that file locking prevents concurrent operations.

        Note: This is a simulation since we can't easily create real concurrent operations in a unit test.
        """
        # Create a work effort and keep the lock
        result = self.manager.create_work_effort(
            title="Concurrent Test",
            assignee="tester",
            priority="medium",
            due_date="2023-06-15",
            keep_lock=True  # Keep the lock after creation
        )

        # Get the filename
        filename = os.path.basename(result)

        # Verify that the lock file exists
        lock_file = f"{result}.lock"
        self.assertTrue(os.path.exists(lock_file), "Lock file should exist after creation")

        # Release the lock
        self.manager._release_file_lock(result)

        # Verify that the lock file is gone
        self.assertFalse(os.path.exists(lock_file), "Lock file should not exist after release")

        # Acquire the lock again
        lock_result = self.manager._acquire_file_lock(result)
        self.assertTrue(lock_result, "Should be able to acquire lock after release")

        # Clean up
        self.manager._release_file_lock(result)


if __name__ == '__main__':
    unittest.main()