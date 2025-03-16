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

# Add the src directory to the path for proper importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import code_conductor modules with the correct path
from code_conductor import __version__ as pkg_version
from code_conductor.cli.cli import VERSION as cli_version


def test_version_consistency():
    """Test that version is consistent across package and CLI."""
    # Versions should be identical
    assert pkg_version == cli_version, f"Package version {pkg_version} != CLI version {cli_version}"

    # Version should follow semantic versioning (X.Y.Z)
    assert re.match(r'^\d+\.\d+\.\d+$', pkg_version), f"Version {pkg_version} doesn't follow semver"

    print(f"\nPackage version: {pkg_version}")
    print(f"CLI version: {cli_version}")


def test_version_in_help():
    """Test that version appears in CLI help output."""
    # Mock sys.stdout to capture output
    mock_stdout = MagicMock()

    # Patch sys.argv and sys.stdout
    with patch('sys.argv', ['code-conductor', '--version']), \
         patch('sys.stdout', mock_stdout):

        try:
            # Import code_conductor CLI
            from code_conductor.cli.cli import main_entry

            # This might raise SystemExit
            main_entry()
        except SystemExit:
            pass

        # Check that version was printed
        mock_stdout.write.assert_called()

        # Get all calls to write as a list of strings
        output = ''.join([call[0][0] for call in mock_stdout.write.call_args_list])

        # Check that version appears in output
        assert cli_version in output, f"Version {cli_version} not found in CLI output"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])