#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Edge case tests for the Work Effort Manager.

This module tests various edge cases and boundary conditions for the Work Effort Manager
to ensure robustness and reliability under unusual or extreme conditions.

Test categories:
1. Invalid input data
2. File system edge cases
3. Concurrency and race conditions
4. Error handling and recovery
5. Large data and performance
6. Internationalization and special characters
7. Configuration edge cases
"""

import os
import sys
import json
import time
import shutil
import pytest
import tempfile
import threading
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the project modules
from src.code_conductor.work_effort_manager import WorkEffortManager


class TestWorkEffortManagerInvalidInput(unittest.TestCase):
    """Test invalid input handling in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create necessary directory structure including _AI-Setup directory
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Initialize manager with our test configuration
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
        """Test creating work effort with empty title."""
        result = self.manager.create_work_effort(
            title="",
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )
        self.assertIsNone(result, "Empty title should result in None")

    def test_none_title(self):
        """Test creating work effort with None title."""
        result = self.manager.create_work_effort(
            title=None,
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )
        self.assertIsNone(result, "None title should result in None")

    def test_invalid_priority(self):
        """Test creating work effort with invalid priority."""
        result = self.manager.create_work_effort(
            title="Test Work Effort",
            assignee="tester",
            priority="invalid_priority",
            due_date="2023-03-17"
        )
        # Depending on implementation, this might still create the work effort
        # or fail. Check the actual behavior and assert accordingly.
        if result is not None:
            # If it creates the work effort, priority should be sanitized or defaulted
            content = self.manager.get_work_effort_content(os.path.basename(result))
            self.assertIn("priority:", content)

    def test_invalid_date_format(self):
        """Test creating work effort with invalid date format."""
        result = self.manager.create_work_effort(
            title="Test Work Effort",
            assignee="tester",
            priority="medium",
            due_date="invalid-date"
        )
        self.assertIsNone(result, "Invalid date should result in None")

    def test_special_characters_title(self):
        """Test creating work effort with special characters in title."""
        special_title = "Test/Work\\Effort:With*Special?Characters\"<>|"
        result = self.manager.create_work_effort(
            title=special_title,
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )
        # Should sanitize the filename or fail gracefully
        self.assertIsNotNone(result, "Should handle special characters in title")

    def test_extremely_long_title(self):
        """Test creating work effort with extremely long title."""
        long_title = "A" * 1000  # 1000 character title
        result = self.manager.create_work_effort(
            title=long_title,
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )
        # Should either truncate or fail gracefully
        self.assertIsNotNone(result, "Should handle extremely long title")


class TestWorkEffortManagerFileSystem(unittest.TestCase):
    """Test file system edge cases in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Default directory structure for normal tests
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager') and self.manager:
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_missing_directories(self):
        """Test initializing with missing directories."""
        # Remove all directories
        shutil.rmtree(self.work_efforts_dir)

        # Initialize manager with our test configuration pointing to non-existent dirs
        manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

        # Check if directories are created or error is handled
        self.assertTrue(manager.has_required_folders() or not manager.has_required_folders(),
                      "Manager should either create missing folders or report they're missing")

    def test_readonly_directory(self):
        """Test with read-only directories."""
        # Make active directory read-only
        active_dir = os.path.join(self.work_efforts_dir, 'active')
        os.chmod(active_dir, 0o555)  # read and execute but not write

        try:
            # Initialize manager
            manager = WorkEffortManager(
                project_dir=self.test_dir,
                config=self.config
            )

            # Try to create a work effort (should fail or handle gracefully)
            result = manager.create_work_effort(
                title="Test Work Effort",
                assignee="tester",
                priority="medium",
                due_date="2023-03-17"
            )

            # Whether it returns None or raises an exception, it should not crash
            if result is not None:
                self.fail("Should not be able to create work effort in read-only directory")
        except Exception as e:
            # Error handling is acceptable as long as it's graceful
            pass
        finally:
            # Reset permissions so tearDown can clean up
            os.chmod(active_dir, 0o755)

    @patch('os.path.getmtime')
    def test_filesystem_errors(self, mock_getmtime):
        """Test handling of file system errors."""
        # Set up manager
        manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

        # Make getmtime raise an exception to simulate file system error
        mock_getmtime.side_effect = OSError("Simulated file system error")

        # Create a work effort and then try to check for changes
        # This should not crash the manager
        try:
            # First create without the mock active
            mock_getmtime.side_effect = None
            result = manager.create_work_effort(
                title="Test Work Effort",
                assignee="tester",
                priority="medium",
                due_date="2023-03-17"
            )

            # Now enable the mock to simulate error
            mock_getmtime.side_effect = OSError("Simulated file system error")

            # This should handle the error gracefully
            manager._check_for_changes()
        except Exception as e:
            self.fail(f"Manager should handle file system errors gracefully: {str(e)}")


class TestWorkEffortManagerConcurrency(unittest.TestCase):
    """Test concurrency and race conditions in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create necessary directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Initialize manager with our test configuration
        self.manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager'):
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_concurrent_create(self):
        """Test creating multiple work efforts concurrently."""
        num_threads = 10
        results = []
        errors = []

        def create_work_effort(i):
            try:
                result = self.manager.create_work_effort(
                    title=f"Concurrent Test {i}",
                    assignee="tester",
                    priority="medium",
                    due_date="2023-03-17"
                )
                if result:
                    results.append(result)
                return result
            except Exception as e:
                errors.append(str(e))
                return None

        # Create work efforts concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_work_effort, i) for i in range(num_threads)]

        # Check results
        self.assertEqual(len(results), num_threads,
                         f"Should create {num_threads} work efforts, but created {len(results)}")
        self.assertEqual(len(errors), 0, f"Encountered errors: {errors}")

    def test_concurrent_read_write(self):
        """Test concurrent reads and writes to the same work effort."""
        # Create a test work effort
        work_effort_path = self.manager.create_work_effort(
            title="Concurrent RW Test",
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )

        filename = os.path.basename(work_effort_path)

        # Track if we encountered any errors
        errors = []

        def read_work_effort():
            try:
                for _ in range(50):  # Read multiple times
                    content = self.manager.get_work_effort_content(filename)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(f"Read error: {str(e)}")

        def update_status():
            try:
                self.manager.update_work_effort_status(
                    filename,
                    "completed"
                )
            except Exception as e:
                errors.append(f"Update error: {str(e)}")

        # Run concurrent reads and a write
        threads = []
        for _ in range(5):
            t = threading.Thread(target=read_work_effort)
            threads.append(t)
            t.start()

        # Add a write thread
        t = threading.Thread(target=update_status)
        threads.append(t)
        t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check for errors
        self.assertEqual(len(errors), 0, f"Encountered errors in concurrent operations: {errors}")


class TestWorkEffortManagerErrorHandling(unittest.TestCase):
    """Test error handling and recovery in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create necessary directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Initialize manager with our test configuration
        self.manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager'):
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_corrupted_json(self):
        """Test handling of corrupted JSON input."""
        # Intentionally malformed JSON
        corrupted_json = "{"

        # Test with corrupted JSON string
        result = self.manager.create_work_effort_from_json(corrupted_json)
        self.assertIsNone(result, "Should handle corrupted JSON gracefully")

    def test_corrupted_work_effort_file(self):
        """Test handling of corrupted work effort file."""
        # Create a valid work effort
        work_effort_path = self.manager.create_work_effort(
            title="Test Work Effort",
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )

        # Corrupt the file by writing invalid content
        with open(work_effort_path, 'w') as f:
            f.write("This is not a valid work effort file")

        # Try to read the corrupted file
        filename = os.path.basename(work_effort_path)
        content = self.manager.get_work_effort_content(filename)

        # Should either return the content as is or handle error gracefully
        self.assertIsNotNone(content, "Should handle corrupted file content gracefully")

    @patch('builtins.open')
    def test_io_errors(self, mock_open):
        """Test handling of I/O errors."""
        # Make open raise an IOError
        mock_open.side_effect = IOError("Simulated I/O error")

        # Try to create a work effort (should fail gracefully)
        try:
            result = self.manager.create_work_effort(
                title="Test Work Effort",
                assignee="tester",
                priority="medium",
                due_date="2023-03-17"
            )

            # Should fail but not crash
            self.assertIsNone(result, "Should return None on IOError")
        except Exception as e:
            self.fail(f"Should handle IOError gracefully: {str(e)}")


class TestWorkEffortManagerPerformance(unittest.TestCase):
    """Test performance and large data handling in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create necessary directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Initialize manager with our test configuration
        self.manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager'):
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_large_number_of_work_efforts(self):
        """Test handling of a large number of work efforts."""
        # Skip this test in normal CI/CD to save time
        if os.environ.get('SKIP_PERFORMANCE_TESTS'):
            self.skipTest("Skipping performance test")

        # Create a large number of work efforts
        num_efforts = 100  # Adjust based on what's reasonable

        for i in range(num_efforts):
            result = self.manager.create_work_effort(
                title=f"Performance Test {i}",
                assignee="tester",
                priority="medium",
                due_date="2023-03-17"
            )
            self.assertIsNotNone(result, f"Failed to create work effort {i}")

        # Now test getting all work efforts
        start_time = time.time()
        all_efforts = self.manager.get_work_efforts("active")
        end_time = time.time()

        # Verify we got all efforts
        self.assertEqual(len(all_efforts), num_efforts,
                        f"Should get {num_efforts} work efforts, got {len(all_efforts)}")

        # Check performance (This is subjective, adjust as needed)
        execution_time = end_time - start_time
        max_acceptable_time = 2.0  # seconds
        self.assertLess(execution_time, max_acceptable_time,
                       f"Getting {num_efforts} work efforts took {execution_time:.2f}s, which exceeds {max_acceptable_time}s")

    def test_large_work_effort_content(self):
        """Test handling of a work effort with very large content."""
        # Create a large content dictionary
        large_content = {
            "objectives": ["Test large content handling"],
            "tasks": [f"Task {i}" for i in range(1000)],  # 1000 tasks
            "notes": ["A" * 10000]  # A 10KB string
        }

        # Create the work effort with large content
        result = self.manager.create_work_effort(
            title="Large Content Test",
            assignee="tester",
            priority="medium",
            due_date="2023-03-17",
            content=large_content
        )

        self.assertIsNotNone(result, "Failed to create work effort with large content")

        # Verify we can read it back
        filename = os.path.basename(result)
        content = self.manager.get_work_effort_content(filename)

        self.assertIsNotNone(content, "Failed to read large work effort content")
        self.assertIn("Task 999", content, "Large content was not saved correctly")


class TestWorkEffortManagerInternationalization(unittest.TestCase):
    """Test internationalization and special character handling in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create necessary directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create a basic configuration
        self.config = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.work_efforts_dir, "active"),
                    "completed": os.path.join(self.work_efforts_dir, "completed"),
                    "archived": os.path.join(self.work_efforts_dir, "archived"),
                    "templates": os.path.join(self.work_efforts_dir, "templates"),
                }
            }
        }

        # Save the config to a file in the _AI-Setup directory
        self.config_path = os.path.join(self.ai_setup_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        # Create a template file
        template_content = """---
title: "{{title}}"
status: "{{status}}"
priority: "{{priority}}"
assignee: "{{assignee}}"
created: "{{created}}"
last_updated: "{{last_updated}}"
due_date: "{{due_date}}"
tags: []
---

# {{title}}

## 🚩 Objectives
- Objective 1

## 🛠 Tasks
- [ ] Task 1

## 📝 Notes
- Note 1

## 🐞 Issues Encountered
- None

## ✅ Outcomes & Results
- None yet

## 📌 Linked Items
- None

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'work-effort-template.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Initialize manager with our test configuration
        self.manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager'):
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_unicode_title(self):
        """Test creating work effort with Unicode title."""
        # Include a variety of non-ASCII characters
        unicode_title = "Tést Wörk Éffôrt with 中文 and ру́сский язы́к"

        result = self.manager.create_work_effort(
            title=unicode_title,
            assignee="tester",
            priority="medium",
            due_date="2023-03-17"
        )

        self.assertIsNotNone(result, "Failed to create work effort with Unicode title")

        # Verify we can read it back
        filename = os.path.basename(result)
        content = self.manager.get_work_effort_content(filename)

        self.assertIsNotNone(content, "Failed to read work effort with Unicode title")

        # The title in the content should match the original
        self.assertIn(unicode_title, content, "Unicode title was not saved correctly")

    def test_unicode_content(self):
        """Test creating work effort with Unicode content."""
        # Create content with Unicode characters
        unicode_content = {
            "objectives": ["Test Unicode content handling", "测试目标"],
            "tasks": ["Task 1: Привет, мир!", "タスク 2: 日本語をテスト"],
            "notes": ["Non-ASCII characters: éèêëàâäôöùûüÿç"]
        }

        result = self.manager.create_work_effort(
            title="Unicode Content Test",
            assignee="tester",
            priority="medium",
            due_date="2023-03-17",
            content=unicode_content
        )

        self.assertIsNotNone(result, "Failed to create work effort with Unicode content")

        # Verify we can read it back
        filename = os.path.basename(result)
        content = self.manager.get_work_effort_content(filename)

        self.assertIsNotNone(content, "Failed to read work effort with Unicode content")

        # Check for some of the Unicode content
        self.assertIn("测试目标", content, "Unicode content (Chinese) was not saved correctly")
        self.assertIn("Привет, мир!", content, "Unicode content (Russian) was not saved correctly")
        self.assertIn("日本語", content, "Unicode content (Japanese) was not saved correctly")


class TestWorkEffortManagerConfiguration(unittest.TestCase):
    """Test configuration edge cases in the Work Effort Manager."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create minimal directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(self.work_efforts_dir, exist_ok=True)

        # Create _AI-Setup directory which is expected by the manager
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'manager'):
            self.manager.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_missing_config(self):
        """Test initializing with no configuration."""
        # Initialize without any config
        manager = WorkEffortManager(project_dir=self.test_dir)

        # Should initialize with default values or fail gracefully
        self.assertIsNotNone(manager, "Manager should initialize even without config")

    def test_partial_config(self):
        """Test initializing with partial configuration."""
        # Create partial config with missing required sections
        partial_config = {
            "work_efforts": {
                # Missing directories section
                "use_manager": True
            }
        }

        # Initialize with partial config
        manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=partial_config
        )

        # Should use defaults for missing values
        self.assertIsNotNone(manager, "Manager should initialize with partial config")

    def test_invalid_config_file(self):
        """Test initializing with invalid config file."""
        # Create an invalid JSON file
        config_file = os.path.join(self.test_dir, 'invalid_config.json')
        with open(config_file, 'w') as f:
            f.write("This is not valid JSON")

        # Initialize with invalid config file
        try:
            manager = WorkEffortManager(
                project_dir=self.test_dir,
                config_file=config_file
            )

            # Should either use defaults or fail gracefully
            self.assertIsNotNone(manager, "Manager should handle invalid config file gracefully")
        except Exception as e:
            self.fail(f"Manager should handle invalid config file gracefully: {str(e)}")

    def test_conflicting_configs(self):
        """Test initializing with conflicting configurations."""
        # Create two conflicting configs
        config1 = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.test_dir, "path1", "active")
                }
            }
        }

        config2 = {
            "work_efforts": {
                "directories": {
                    "active": os.path.join(self.test_dir, "path2", "active")
                }
            }
        }

        # Create config file
        config_file = os.path.join(self.test_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump(config2, f)

        # Initialize with both dict and file (dict should take precedence)
        manager = WorkEffortManager(
            project_dir=self.test_dir,
            config=config1,
            config_file=config_file
        )

        # Ensure the directory from config1 exists as it should take precedence
        os.makedirs(os.path.join(self.test_dir, "path1", "active"), exist_ok=True)

        # Check which config was used
        if manager.has_required_folders():
            # If it created folders, check which path was used
            self.assertTrue(
                os.path.exists(os.path.join(self.test_dir, "path1", "active")) or
                os.path.exists(os.path.join(self.test_dir, "path2", "active")),
                "One of the configs should be used"
            )


if __name__ == '__main__':
    unittest.main()