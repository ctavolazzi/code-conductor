#!/usr/bin/env python3
"""
Folder Scanner module for code_conductor package.

This module provides a validator for checking the structure of the code conductor project.
"""

import os
from typing import Dict, List

class FolderStructureValidator:
    """
    Validator for checking the structure of the code conductor project.
    """
    def __init__(self, base_dir=None):
        """
        Initialize a new folder structure validator.

        Args:
            base_dir: Base directory to check (default: current directory)
        """
        self.base_dir = base_dir or os.getcwd()
        self.errors = []

    def validate(self):
        """
        Validate the folder structure.

        Returns:
            bool: True if the structure is valid, False otherwise
        """
        self.errors = []

        # Check for required directories
        required_dirs = [
            "_AI-Setup",
            "work_efforts",
            "work_efforts/templates",
            "work_efforts/active",
            "work_efforts/completed",
            "work_efforts/archived"
        ]

        for required_dir in required_dirs:
            dir_path = os.path.join(self.base_dir, required_dir)
            if not os.path.isdir(dir_path):
                self.errors.append(f"Required directory missing: {required_dir}")

        # Check for required files
        required_files = [
            "work_efforts/templates/work-effort-template.md"
        ]

        for required_file in required_files:
            file_path = os.path.join(self.base_dir, required_file)
            if not os.path.isfile(file_path):
                self.errors.append(f"Required file missing: {required_file}")

        return len(self.errors) == 0