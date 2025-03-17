#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pytest
import shutil
import tempfile
from unittest.mock import patch

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from src.code_conductor.cli.cli import create_work_effort
    from src.code_conductor.config import Config
except ModuleNotFoundError:
    print("Warning: Required modules not found. Some functionality will be limited.")
    Config = None

from src.code_conductor.folder_scanner import FolderStructureValidator

# Test data
basic_structure = [
    "_AI-Setup",
    "_AI-Setup/INSTRUCTIONS.md",
    "_AI-Setup/AI-setup-validation-instructions.md",
    "_AI-Setup/AI-work-effort-system.md",
    "_AI-Setup/AI-setup-instructions.md",
    "work_efforts",
    "work_efforts/templates",
    "work_efforts/templates/work-effort-template.md",
    "work_efforts/active",
    "work_efforts/completed",
    "work_efforts/archived",
]

class TestFolderStructure:
    def setup_method(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Test directory structure
        self.test_dirs = basic_structure.copy()

        # Create test directory structure
        for item in self.test_dirs:
            path = os.path.join(self.temp_dir, item)
            if '.' in os.path.basename(path):
                # It's a file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(f"Test content for {item}")
            else:
                # It's a directory
                os.makedirs(path, exist_ok=True)

    def teardown_method(self):
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_valid_structure(self):
        """Test that a valid structure passes validation."""
        validator = FolderStructureValidator(self.temp_dir)
        assert validator.validate()
        assert len(validator.errors) == 0

    def test_missing_ai_setup(self):
        """Test validation with missing _AI-Setup directory."""
        # Remove _AI-Setup directory
        shutil.rmtree(os.path.join(self.temp_dir, "_AI-Setup"))

        validator = FolderStructureValidator(self.temp_dir)
        assert not validator.validate()
        assert any("_AI-Setup" in error for error in validator.errors)

    def test_missing_work_efforts(self):
        """Test validation with missing work_efforts directory."""
        # Remove work_efforts directory
        shutil.rmtree(os.path.join(self.temp_dir, "work_efforts"))

        validator = FolderStructureValidator(self.temp_dir)
        assert not validator.validate()
        assert any("work_efforts" in error for error in validator.errors)

    def test_missing_template(self):
        """Test validation with missing template file."""
        # Remove template file
        os.remove(os.path.join(self.temp_dir, "work_efforts/templates/work-effort-template.md"))

        validator = FolderStructureValidator(self.temp_dir)
        assert not validator.validate()
        assert any("template" in error for error in validator.errors)

    def test_create_work_effort(self):
        """Test creating a work effort."""
        public_apis_dir = os.path.join(self.temp_dir, "public_apis")
        os.makedirs(public_apis_dir, exist_ok=True)

        # Setup proper structure in public_apis
        for item in basic_structure:
            path = os.path.join(public_apis_dir, item)
            if '.' in os.path.basename(path):
                # It's a file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(f"Test content for {item}")
            else:
                # It's a directory
                os.makedirs(path, exist_ok=True)

        # Mock the current date/time to ensure consistent test results
        with patch('code_conductor.utils.work_effort.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20230101_test"

            from src.code_conductor.work_effort import WorkEffortManager

            config = Config(public_apis_dir)
            manager = WorkEffortManager(config)

            target_dir = os.path.join(public_apis_dir, "_AI-Setup/work_efforts/active")
            print(f"Creating work effort in: {target_dir}")
            result = manager.create_work_effort("Test Effort", "high", "Test description", "user")

            assert result
            assert os.path.exists(os.path.join(public_apis_dir, "_AI-Setup/work_efforts/active/20230101_test_effort.md"))

            # Verify content
            with open(os.path.join(public_apis_dir, "_AI-Setup/work_efforts/active/20230101_test_effort.md"), 'r') as f:
                content = f.read()
                assert "Test Effort" in content
                assert "high" in content
                assert "Test description" in content
                assert "user" in content

def main():
    # Set up test parameters
    title = "API Testing Framework"
    assignee = "self"
    priority = "high"
    due_date = datetime.now().strftime("%Y-%m-%d")
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/work-effort-template.md")

    # Set target directory to public-apis
    public_apis_dir = "/Users/ctavolazzi/Code/public-apis"
    target_dir = os.path.join(public_apis_dir, "_AI-Setup/work_efforts/active")

    print(f"Creating work effort in: {target_dir}")

    # Create a work effort
    file_path = create_work_effort(
        title=title,
        assignee=assignee,
        priority=priority,
        due_date=due_date,
        template_path=template_path,
        target_dir=target_dir
    )

    print(f"Created work effort at: {file_path}")

    # Check if a folder was created
    if file_path:
        folder_path = os.path.dirname(file_path)
        print(f"Folder path: {folder_path}")
        print(f"Is folder: {os.path.isdir(folder_path)}")
        print(f"Folder contents: {os.listdir(folder_path)}")

        # Try adding a test file to the folder
        test_file_path = os.path.join(folder_path, "test_file.txt")
        with open(test_file_path, "w") as f:
            f.write("This is a test file to demonstrate folder structure.")

        print(f"Added test file: {test_file_path}")
        print(f"Updated folder contents: {os.listdir(folder_path)}")

if __name__ == "__main__":
    main()