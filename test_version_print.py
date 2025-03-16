#!/usr/bin/env python3
"""
Test script to verify that the print_version function works correctly.
"""

import sys
import os

# Add parent directory to path to allow direct imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the necessary functions
from cli import print_version, VERSION
from __init__ import __version__

def test_version_print():
    """Test that the print_version function displays the correct version."""
    print("\n=== Testing cli.py print_version function ===")
    print(f"Version in __init__.py: {__version__}")
    print(f"VERSION in cli.py: {VERSION}")
    print("Calling print_version():")
    print_version()

    assert VERSION == __version__, f"VERSION in cli.py ({VERSION}) does not match __version__ in __init__.py ({__version__})"
    print("✅ Test passed: VERSION in cli.py matches __version__ in __init__.py")

if __name__ == "__main__":
    test_version_print()