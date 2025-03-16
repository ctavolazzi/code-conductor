#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for work effort manager configuration integration.

This module tests whether:
1. The config.json file is properly loaded
2. The work effort manager is used when specified in config.json
3. A work effort can be created using the work effort manager
4. The CLI properly uses the work effort manager when specified in config
"""

import os
import sys
import json
import shutil
import unittest
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
import datetime

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the project modules
import cli
from work_efforts.scripts.work_effort_manager import WorkEffortManager

class TestWorkEffortManagerConfig(unittest.TestCase):
    """Test the work effort manager configuration and integration."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create the _AI-Setup directory
        self.ai_setup_dir = os.path.join(self.test_dir, '_AI-Setup')
        os.makedirs(self.ai_setup_dir, exist_ok=True)

        # Create work_efforts directory structure
        self.work_efforts_dir = os.path.join(self.test_dir, 'work_efforts')
        os.makedirs(os.path.join(self.work_efforts_dir, 'active'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'completed'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'archived'), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, 'templates'), exist_ok=True)

        # Create a sample template
        template_content = """# {{title}}

**Status:** {{status}}
**Priority:** {{priority}}
**Assignee:** {{assignee}}
**Created:** {{created}}
**Last Updated:** {{last_updated}}
**Due Date:** {{due_date}}

## Objectives
- Clearly define goals for this work effort.

## Tasks
- [ ] Task 1
- [ ] Task 2

## Notes
- Context, links to relevant code, designs, references.
"""
        template_path = os.path.join(self.work_efforts_dir, 'templates', 'default.md')
        with open(template_path, 'w') as f:
            f.write(template_content)

        # Save original working directory to restore later
        self.original_dir = os.getcwd()

        # Change to test directory
        os.chdir(self.test_dir)

        # Create the config.json file
        self.create_config_json()

    def create_config_json(self):
        """Create the config.json file for testing."""
        config = {
            "work_efforts": {
                "use_manager": True,
                "manager_script": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work_efforts', 'scripts', 'work_effort_manager.py')),
                "runner_script": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work_efforts', 'scripts', 'run_work_effort_manager.py')),
                "project_dir": self.test_dir,
                "auto_start": True,
                "default_settings": {
                    "assignee": "Test User",
                    "priority": "medium",
                    "due_date": "+7d"
                },
                "directories": {
                    "active": "work_efforts/active",
                    "completed": "work_efforts/completed",
                    "archived": "work_efforts/archived",
                    "templates": "work_efforts/templates"
                }
            },
            "ai_settings": {
                "preferred_model": "phi3",
                "timeout": 60
            }
        }

        config_path = os.path.join(self.ai_setup_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def tearDown(self):
        """Clean up after tests."""
        # Change back to original directory
        os.chdir(self.original_dir)

        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_config_loading(self):
        """Test that the config.json file is properly loaded."""
        # Call the load_config function from cli.py
        config = cli.load_config()

        # Verify that the config was loaded correctly
        self.assertIsNotNone(config)
        self.assertIn('work_efforts', config)
        self.assertTrue(config['work_efforts']['use_manager'])
        self.assertEqual(config['work_efforts']['default_settings']['assignee'], 'Test User')

    @patch('subprocess.Popen')
    def test_runner_script_called(self, mock_popen):
        """Test that the runner script is called when autostart is enabled."""
        # Create a mock for subprocess.Popen
        mock_popen.return_value = MagicMock()

        # Call the main function from cli.py with work command to trigger work effort manager
        with patch('sys.argv', ['cli.py', 'work', '--title', 'Test Work Effort', '--assignee', 'Tester']):
            cli.main_entry()

        # Verify that Popen was called with the correct arguments
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('run_work_effort_manager.py', call_args[1])
        self.assertIn('--no-auto-start', call_args[2])

    def test_manager_used_when_configured(self):
        """Test that the work effort manager is used when specified in config."""
        # Create a direct test of the integration
        # Rather than using mocks, we'll create a real file with a specific name
        # and check that it's created

        # Create a unique title for this test
        unique_title = f"Test Integration {datetime.datetime.now().strftime('%H%M%S')}"

        # Set up the config file to use the work effort manager
        config = {
            "work_efforts": {
                "use_manager": True,
                "manager_script": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work_efforts', 'scripts', 'work_effort_manager.py')),
                "runner_script": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work_efforts', 'scripts', 'run_work_effort_manager.py')),
                "project_dir": self.test_dir,
                "auto_start": False,
                "directories": {
                    "active": "work_efforts/active",
                    "completed": "work_efforts/completed",
                    "archived": "work_efforts/archived",
                    "templates": "work_efforts/templates"
                }
            }
        }

        # Write the config to the config.json file
        config_path = os.path.join(self.ai_setup_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Add the test directory to sys.path so we can import modules
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        # Import the work_effort_manager.py module
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'work_efforts', 'scripts'))
        from work_effort_manager import WorkEffortManager

        # Create a WorkEffortManager instance
        manager = WorkEffortManager(project_dir=self.test_dir, config=config["work_efforts"])

        # Create a work effort with the unique title
        work_effort_path = manager.create_work_effort(
            title=unique_title,
            assignee="Test User",
            priority="medium",
            due_date="+7d"
        )

        # Verify that the work effort was created
        self.assertIsNotNone(work_effort_path)
        self.assertTrue(os.path.exists(work_effort_path))

        # Verify that the file contains the unique title
        with open(work_effort_path, 'r') as f:
            content = f.read()
            self.assertIn(unique_title, content)

    def test_actual_work_effort_creation(self):
        """Test that a work effort can actually be created using the manager."""
        # Create a WorkEffortManager instance
        manager = WorkEffortManager(project_dir=self.test_dir, config={
            "directories": {
                "active": "work_efforts/active",
                "completed": "work_efforts/completed",
                "archived": "work_efforts/archived",
                "templates": "work_efforts/templates"
            }
        })

        # Create a work effort
        now = datetime.datetime.now()
        title = "Test Work Effort"
        assignee = "Tester"
        priority = "medium"
        due_date = (now + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        # Create the work effort
        work_effort_path = manager.create_work_effort(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date
        )

        # Verify that the work effort was created
        self.assertIsNotNone(work_effort_path)
        self.assertTrue(os.path.exists(work_effort_path))

        # Read the content of the file to verify it was created correctly
        with open(work_effort_path, 'r') as f:
            content = f.read()

        # Verify that the placeholders were replaced
        self.assertIn(title, content)
        self.assertIn(assignee, content)
        self.assertIn(priority, content)
        self.assertIn(due_date, content)

    def test_load_config_from_ai_setup(self):
        """Test that the config can be loaded from the _AI-Setup directory by the run_work_effort_manager script."""
        # Import the load_config_from_ai_setup function from run_work_effort_manager.py
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work_efforts', 'scripts')))
        from run_work_effort_manager import load_config_from_ai_setup

        # Call the function
        config = load_config_from_ai_setup()

        # Verify that the config was loaded correctly
        self.assertIsNotNone(config)
        self.assertIn('work_efforts', config)
        self.assertTrue(config['work_efforts']['use_manager'])
        self.assertEqual(config['work_efforts']['default_settings']['assignee'], 'Test User')

if __name__ == '__main__':
    unittest.main()