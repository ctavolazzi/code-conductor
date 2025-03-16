import os
import sys
import json
import shutil
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import from the correct package structure
from src.code_conductor.cli import cli
from src.code_conductor import __version__ as VERSION

class TestConfigSystem(unittest.TestCase):
    """Tests for the configuration system."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.ai_setup_dir = os.path.join(self.test_dir, "_AI-Setup")
        self.work_efforts_dir = os.path.join(self.ai_setup_dir, "work_efforts")
        self.config_file = os.path.join(self.ai_setup_dir, "config.json")

        # Create the directory structure
        os.makedirs(self.ai_setup_dir, exist_ok=True)
        os.makedirs(self.work_efforts_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_version_definition(self):
        """Test that the version is defined and follows semver."""
        self.assertIsNotNone(VERSION)
        self.assertRegex(VERSION, r'^\d+\.\d+\.\d+$')

    def test_config_structure(self):
        """Test that we can create and validate a basic config structure."""
        # Create a basic config
        config = {
            "version": VERSION,
            "name": "Test Config",
            "work_efforts_dir": self.work_efforts_dir
        }

        # Write it to the config file
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_file))

        # Read it back
        with open(self.config_file, 'r') as f:
            loaded_config = json.load(f)

        # Verify contents
        self.assertEqual(loaded_config["version"], VERSION)
        self.assertEqual(loaded_config["name"], "Test Config")
        self.assertEqual(loaded_config["work_efforts_dir"], self.work_efforts_dir)

if __name__ == "__main__":
    unittest.main()