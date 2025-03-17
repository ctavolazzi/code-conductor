#!/usr/bin/env python3
"""
Tests for version consistency across all modules.
"""

import unittest
import sys
import os
import re
import pytest

# Add the src directory to the path for proper importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the version directly from the package
from src.code_conductor import __version__ as root_version


class TestVersionConsistency(unittest.TestCase):
    """Test that versions are consistent across all modules."""

    def test_root_version_defined(self):
        """Test that the root package has a version defined."""
        self.assertIsNotNone(root_version)
        self.assertIsInstance(root_version, str)
        # Should match semantic versioning format (major.minor.patch)
        self.assertRegex(root_version, r'^\d+\.\d+\.\d+$')

    def test_setup_py_version_matches_root(self):
        """Test that the version in setup.py matches the root package version."""
        # Read the setup.py file
        setup_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
        with open(setup_py_path, 'r') as f:
            setup_content = f.read()

        # Extract the version with regex
        version_match = re.search(r'version\s*=\s*[\'"]([^\'"]*)[\'"]', setup_content)
        if not version_match:
            # Check if it's reading from __init__.py
            has_dynamic_version = "with open('src/code_conductor/__init__.py'" in setup_content
            self.assertTrue(has_dynamic_version, "setup.py should either define version directly or read from __init__.py")
        else:
            setup_version = version_match.group(1)
            self.assertEqual(setup_version, root_version)


if __name__ == '__main__':
    pytest.main(["-xvs", __file__])