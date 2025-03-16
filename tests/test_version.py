"""
Tests for version consistency across all modules.
"""

import unittest
import sys
import os
import re

# Add parent directory to path to allow importing the package directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the root package and modules directly
import work_efforts.core
import work_efforts.utils
import work_efforts.models
import work_efforts.events
import work_efforts.filesystem
from cli import VERSION


class TestVersionConsistency(unittest.TestCase):
    """Test that versions are consistent across all modules."""

    def test_root_version_defined(self):
        """Test that the root package has a version defined."""
        # Import directly from __init__.py
        from __init__ import __version__
        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)
        # Should match semantic versioning format (major.minor.patch)
        self.assertRegex(__version__, r'^\d+\.\d+\.\d+$')

    def test_submodule_versions_match_root(self):
        """Test that all submodule versions match the root package version."""
        # Import directly from __init__.py
        from __init__ import __version__

        self.assertEqual(work_efforts.core.__version__, __version__)
        self.assertEqual(work_efforts.utils.__version__, __version__)
        self.assertEqual(work_efforts.models.__version__, __version__)
        self.assertEqual(work_efforts.events.__version__, __version__)
        self.assertEqual(work_efforts.filesystem.__version__, __version__)

    def test_cli_version_matches_root(self):
        """Test that the CLI version matches the root package version."""
        # Import directly from __init__.py
        from __init__ import __version__

        self.assertEqual(VERSION, __version__)

    def test_setup_py_version_matches_root(self):
        """Test that the version in setup.py matches the root package version."""
        # Import directly from __init__.py
        from __init__ import __version__

        # Read the setup.py file
        with open(os.path.join(os.path.dirname(__file__), '..', 'setup.py'), 'r') as f:
            setup_content = f.read()

        # Extract the version with regex
        version_match = re.search(r'version=([\'"])([^\'"]+)\\1', setup_content)
        if not version_match:
            # Check if it's reading from __init__.py
            has_dynamic_version = "with open('code_conductor/__init__.py'" in setup_content or \
                                "with open('__init__.py'" in setup_content
            self.assertTrue(has_dynamic_version, "setup.py should either define version directly or read from __init__.py")
        else:
            setup_version = version_match.group(2)
            self.assertEqual(setup_version, __version__)


if __name__ == '__main__':
    unittest.main()