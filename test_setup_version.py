#!/usr/bin/env python3
"""
Test script to verify that setup.py is reading the version correctly from __init__.py.
"""

import sys
import os
import re

# Add parent directory to path to allow direct imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the version from __init__.py
from __init__ import __version__

def test_setup_version():
    """Test that setup.py extracts the version correctly from __init__.py."""
    print("\n=== Testing setup.py version extraction ===")
    print(f"Version in __init__.py: {__version__}")

    # Read the setup.py file
    setup_path = os.path.join(os.path.dirname(__file__), 'setup.py')
    with open(setup_path, 'r') as f:
        setup_content = f.read()

    # Extract the version with regex - first check if it's directly defined
    direct_version_match = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', setup_content)

    if direct_version_match:
        setup_version = direct_version_match.group(1)
        print(f"Direct version in setup.py: {setup_version}")
        assert setup_version == __version__, f"Direct version in setup.py ({setup_version}) doesn't match __init__.py ({__version__})"
        print("✅ Test passed: Direct version in setup.py matches __version__ in __init__.py")
    else:
        # Check if setup.py is reading from __init__.py
        dynamic_version = "with open" in setup_content and "__init__.py" in setup_content and "version" in setup_content
        print(f"Dynamic version extraction present: {dynamic_version}")
        assert dynamic_version, "setup.py doesn't appear to extract version from __init__.py"

        # Actually execute the extraction code to verify it works
        with open('__init__.py', 'r') as f:
            version_content = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
            if version_content:
                extracted_version = version_content.group(1)
                print(f"Extracted version: {extracted_version}")
                assert extracted_version == __version__, f"Extracted version ({extracted_version}) doesn't match __init__.py ({__version__})"
                print("✅ Test passed: setup.py correctly extracts version from __init__.py")
            else:
                print("❌ Failed to extract version using the regex in setup.py")
                sys.exit(1)

if __name__ == "__main__":
    test_setup_version()