"""
Test importing the WorkEffortManager.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_import():
    """Test that we can import the WorkEffortManager."""
    from src.code_conductor import WorkEffortManager
    assert WorkEffortManager is not None