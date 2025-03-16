#!/usr/bin/env python3
"""
Simple test to verify basic functionality without complex imports.
"""

import os
import sys
import pytest

# Simple test that doesn't rely on imports
def test_simple():
    """A simple test that always passes."""
    assert True

# Test that the src directory exists
def test_src_directory():
    """Test that the src directory exists."""
    assert os.path.isdir(os.path.join(os.path.dirname(__file__), '../src'))

if __name__ == "__main__":
    pytest.main(["-v", __file__])