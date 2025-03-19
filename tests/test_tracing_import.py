"""
Test importing and instantiating the WorkEffortManager.
"""

import os
import sys
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_create_work_effort_manager():
    """Test that we can import and create a WorkEffortManager instance."""
    from src.code_conductor import WorkEffortManager

    # Create a WorkEffortManager instance
    manager = WorkEffortManager()

    # Verify it's an instance of WorkEffortManager
    assert isinstance(manager, WorkEffortManager)

    # Test some basic attributes that should exist
    assert hasattr(manager, 'project_dir')
    assert hasattr(manager, 'config')