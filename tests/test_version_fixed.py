#!/usr/bin/env python3
"""
Test module for verifying Code Conductor's version numbers.

This is a fixed version of the original test_version.py that uses
the correct import paths based on the actual package structure.
"""

import os
import sys
import re
import pytest
from unittest.mock import patch, MagicMock
import unittest

# Add the src directory to the path for proper importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the version directly from the package
from src.code_conductor import __version__ as root_version

def test_version_format():
    """Test that version follows semantic versioning (X.Y.Z)."""
    assert re.match(r'^\d+\.\d+\.\d+$', root_version), f"Version {root_version} doesn't follow semver"
    print(f"\nPackage version: {root_version}")

class TestVersionConsistency(unittest.TestCase):
    """Test that versions are consistent across all modules."""

    def test_root_version_defined(self):
        """Test that the root package has a version defined."""
        self.assertIsNotNone(root_version)
        self.assertIsInstance(root_version, str)

    def test_setup_py_version_matches_root(self):
        """Test that the version in setup.py matches the root package version."""
        setup_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
        with open(setup_py_path, 'r') as f:
            setup_py_content = f.read()

        # Look for the version in setup.py
        version_match = re.search(r'version\s*=\s*[\'"]([^\'"]*)[\'"]', setup_py_content)
        if version_match:
            setup_py_version = version_match.group(1)
        else:
            # Look for version extracted from the package
            version_match = re.search(r'version\s*=\s*version', setup_py_content)
            if version_match:
                # If setup.py is getting version from the package, consider it a match
                setup_py_version = root_version
            else:
                setup_py_version = None

        self.assertIsNotNone(setup_py_version, "Version not found in setup.py")
        self.assertEqual(setup_py_version, root_version,
                         f"setup.py version {setup_py_version} does not match root version {root_version}")

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])