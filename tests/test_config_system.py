import os
import sys
import json
import shutil
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions to test
from cli import (
    create_or_update_config,
    find_nearest_config,
    find_work_efforts_directory,
    setup_ai_in_current_dir,
    VERSION
)

class TestConfigSystem(unittest.TestCase):
    """Tests for the configuration system."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.ai_setup_dir = os.path.join(self.test_dir, "_AI-Setup")
        self.work_efforts_dir = os.path.join(self.ai_setup_dir, "work_efforts")
        self.config_file = os.path.join(self.ai_setup_dir, "config.json")

        # Create directory structure
        os.makedirs(self.ai_setup_dir, exist_ok=True)
        os.makedirs(self.work_efforts_dir, exist_ok=True)

        # Create subdirectories in work_efforts
        os.makedirs(os.path.join(self.work_efforts_dir, "active"), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, "completed"), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, "archived"), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.work_efforts_dir, "scripts"), exist_ok=True)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_create_config(self):
        """Test creating a new config file."""
        config_file, config = create_or_update_config(self.test_dir)

        self.assertTrue(os.path.exists(config_file))
        self.assertEqual(config["version"], VERSION)
        self.assertEqual(config["project_root"], self.test_dir)
        self.assertEqual(config["work_efforts"]["location"], "in_ai_setup")

    def test_update_config(self):
        """Test updating an existing config file."""
        # First create a config
        config_file, config = create_or_update_config(self.test_dir)

        # Now update it with new settings
        new_config = {
            "work_efforts": {
                "location": "in_root"
            }
        }

        updated_file, updated_config = create_or_update_config(self.test_dir, new_config)

        self.assertTrue(os.path.exists(updated_file))
        self.assertEqual(updated_config["work_efforts"]["location"], "in_root")
        # Original settings should be preserved
        self.assertEqual(updated_config["version"], VERSION)

    def test_find_nearest_config(self):
        """Test finding the nearest config file."""
        # Create config file
        create_or_update_config(self.test_dir)

        # Create a subdirectory
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        # Find config from subdirectory
        found_config, config_data = find_nearest_config(subdir)

        self.assertEqual(found_config, self.config_file)
        self.assertEqual(config_data["version"], VERSION)

    def test_find_work_efforts_dir_with_config(self):
        """Test finding work efforts directory when config exists."""
        # Create config with default settings (in_ai_setup)
        create_or_update_config(self.test_dir)

        # Find work efforts directory
        work_dir, in_ai_setup = find_work_efforts_directory(self.test_dir)

        self.assertEqual(work_dir, self.work_efforts_dir)
        self.assertTrue(in_ai_setup)

    def test_find_work_efforts_dir_with_root_config(self):
        """Test finding work efforts directory when config specifies root location."""
        # Create config with root location preference
        create_or_update_config(self.test_dir, {
            "work_efforts": {
                "location": "in_root"
            }
        })

        # Create work_efforts at root level
        root_work_efforts = os.path.join(self.test_dir, "work_efforts")
        os.makedirs(root_work_efforts, exist_ok=True)

        # Find work efforts directory
        work_dir, in_ai_setup = find_work_efforts_directory(self.test_dir)

        self.assertEqual(work_dir, root_work_efforts)
        self.assertFalse(in_ai_setup)

    def test_find_work_efforts_dir_no_config(self):
        """Test finding work efforts directory when no config exists."""
        # Remove config if it exists
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

        # Find work efforts directory
        work_dir, in_ai_setup = find_work_efforts_directory(self.test_dir)

        self.assertEqual(work_dir, self.work_efforts_dir)
        self.assertTrue(in_ai_setup)

    def test_find_work_efforts_dir_from_subdir(self):
        """Test finding work efforts directory from a subdirectory."""
        # Create config
        create_or_update_config(self.test_dir)

        # Create a subdirectory
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        # Find work efforts directory from subdirectory
        work_dir, in_ai_setup = find_work_efforts_directory(subdir)

        self.assertEqual(work_dir, self.work_efforts_dir)
        self.assertTrue(in_ai_setup)

    @patch('cli.input', return_value='y')
    @patch('cli.setup_work_efforts_structure')
    @patch('cli.create_template_if_missing')
    @patch('cli.create_work_effort')
    def test_setup_with_config(self, mock_create_work, mock_create_template, mock_setup, mock_input):
        """Test setup creates and uses config file."""
        # Mock the necessary functions
        mock_setup.return_value = (self.work_efforts_dir, "template_path", "active_dir", "completed_dir", "archived_dir")
        mock_create_work.return_value = "file_path"

        # Run setup with current directory set to test directory
        with patch('os.getcwd', return_value=self.test_dir):
            setup_ai_in_current_dir()

        # Config file should be created
        self.assertTrue(os.path.exists(self.config_file))

        # Read config to verify contents
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        self.assertEqual(config["version"], VERSION)
        self.assertEqual(config["project_root"], self.test_dir)

if __name__ == '__main__':
    unittest.main()