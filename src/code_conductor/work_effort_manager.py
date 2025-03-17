#!/usr/bin/env python3
"""
Work Effort Manager module for code_conductor package.

This module provides compatibility for tests by re-exporting classes and functions
from the work_efforts package.
"""

# Re-export for backward compatibility
from src.code_conductor.work_efforts.scripts.work_effort_manager import WorkEffortManager

# Also re-export common functions for tests
class Config:
    """Simple config class for tests"""
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()
        self.work_efforts = {
            'directories': {
                'active': 'work_efforts/active',
                'completed': 'work_efforts/completed',
                'archived': 'work_efforts/archived',
                'templates': 'work_efforts/templates'
            }
        }
