#!/usr/bin/env python3
"""
Simple test to verify version consistency without complex imports.
"""

import os
import sys
import re
import subprocess
import pytest

def test_version_from_package():
    """Test that the package version is a valid semver."""
    # Read the version directly from the __init__.py file
    init_path = os.path.join(os.path.dirname(__file__), '../src/code_conductor/__init__.py')

    with open(init_path, 'r') as f:
        init_content = f.read()

    # Extract version using regex
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    assert version_match, "Version not found in __init__.py"

    version = version_match.group(1)
    assert re.match(r'^\d+\.\d+\.\d+$', version), f"Version {version} doesn't follow semver"

    print(f"\nPackage version: {version}")
    return version

def test_version_from_cli():
    """Test that the CLI reports the same version."""
    # Run the CLI with --version flag
    proc = subprocess.run(
        ["python3", "-m", "code_conductor.cli.cli", "--version"],
        cwd=os.path.join(os.path.dirname(__file__), '../'),
        capture_output=True,
        text=True
    )

    # Check that command succeeded
    assert proc.returncode == 0, f"CLI command failed with error: {proc.stderr}"

    # Extract version from output
    version_match = re.search(r'(\d+\.\d+\.\d+)', proc.stdout)
    assert version_match, f"Version not found in CLI output: {proc.stdout}"

    cli_version = version_match.group(1)
    print(f"CLI version: {cli_version}")
    return cli_version

def test_versions_match():
    """Test that package and CLI versions match."""
    pkg_version = test_version_from_package()
    cli_version = test_version_from_cli()

    assert pkg_version == cli_version, f"Package version {pkg_version} != CLI version {cli_version}"

if __name__ == "__main__":
    pytest.main(["-v", __file__])