#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for project_restructuring

This script tests the functionality of project_restructuring.py

Usage:
    python test_project_restructuring.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Import the module to test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import project_restructuring

class TestProjectRestructuring(unittest.TestCase):
    """Test the Project Restructuring functionality."""

    def setUp(self):
        """Set up test environment with a temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Create a mock project structure for testing
        self.create_mock_project()

    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def create_mock_project(self):
        """Create a mock project directory structure for testing."""
        # Create root level files
        Path('cli.py').write_text("print('CLI Module')")
        Path('workflow_runner.py').write_text("print('Workflow Runner')")
        Path('setup.py').write_text("from setuptools import setup, find_packages\nsetup(name='code-conductor')")
        Path('README.md').write_text("# Code Conductor")

        # Create directories
        os.makedirs('.AI-Setup/work_efforts/active', exist_ok=True)
        os.makedirs('.AI-Setup/work_efforts/completed', exist_ok=True)
        os.makedirs('.AI-Setup/work_efforts/scripts', exist_ok=True)
        os.makedirs('utils', exist_ok=True)
        os.makedirs('providers', exist_ok=True)
        os.makedirs('docs', exist_ok=True)
        os.makedirs('tests', exist_ok=True)

        # Create a few files in these directories
        Path('.AI-Setup/work_efforts/active/test.md').write_text("# Test Work Effort")
        Path('.AI-Setup/config.json').write_text("{}")
        Path('utils/helpers.py').write_text("def help_function(): pass")
        Path('tests/test_cli.py').write_text("import unittest\ndef test_cli(): pass")
        Path('providers/openai.py').write_text("def call_openai(): pass")

    def test_parse_args(self):
        """Test argument parsing."""
        # Test with no args
        sys.argv = ['test_project_restructuring.py']
        args = project_restructuring.parse_args()
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)

        # Test with args
        sys.argv = ['test_project_restructuring.py', '--dry-run', '--verbose']
        args = project_restructuring.parse_args()
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)

    def test_create_directory_structure(self):
        """Test directory structure creation."""
        test_structure = {
            "dir1": {
                "subdir1": {},
                "subdir2": {}
            },
            "dir2": {}
        }

        project_restructuring.create_directory_structure(".", test_structure, False, False)

        self.assertTrue(os.path.exists("dir1"))
        self.assertTrue(os.path.exists("dir1/subdir1"))
        self.assertTrue(os.path.exists("dir1/subdir2"))
        self.assertTrue(os.path.exists("dir2"))

    def test_move_files(self):
        """Test file movement functionality."""
        # Create test files
        Path('test_source.txt').write_text("Test content")

        # Define mapping
        mapping = {
            "test_source.txt": "dir1/test_dest.txt"
        }

        # Create directory
        os.makedirs("dir1", exist_ok=True)

        # Test moving
        project_restructuring.move_files(mapping, False, False)

        # Check results
        self.assertTrue(os.path.exists("dir1/test_dest.txt"))
        self.assertEqual(Path('dir1/test_dest.txt').read_text(), "Test content")

    def test_copy_directories(self):
        """Test directory copying."""
        # Create test directory with files
        os.makedirs("source_dir/subdir", exist_ok=True)
        Path('source_dir/file1.txt').write_text("File 1")
        Path('source_dir/subdir/file2.txt').write_text("File 2")

        # Define mapping
        mapping = {
            "source_dir": "dest_dir"
        }

        # Test copying
        project_restructuring.copy_directories(mapping, False, False)

        # Check results
        self.assertTrue(os.path.exists("dest_dir"))
        self.assertTrue(os.path.exists("dest_dir/file1.txt"))
        self.assertTrue(os.path.exists("dest_dir/subdir/file2.txt"))
        self.assertEqual(Path('dest_dir/file1.txt').read_text(), "File 1")
        self.assertEqual(Path('dest_dir/subdir/file2.txt').read_text(), "File 2")

    def test_create_readme_files(self):
        """Test README.md creation."""
        # Define a small subset of directories
        test_readme_content = {
            "test_dir1": "# Test Dir 1",
            "test_dir2/subdir": "# Test Subdir"
        }

        # Replace the actual dictionary with our test one
        original_content = project_restructuring.readme_content
        project_restructuring.readme_content = test_readme_content

        # Run the function
        project_restructuring.create_readme_files(False, False)

        # Check results
        self.assertTrue(os.path.exists("test_dir1/README.md"))
        self.assertTrue(os.path.exists("test_dir2/subdir/README.md"))
        self.assertEqual(Path('test_dir1/README.md').read_text(), "# Test Dir 1")
        self.assertEqual(Path('test_dir2/subdir/README.md').read_text(), "# Test Subdir")

        # Restore original content
        project_restructuring.readme_content = original_content

    def test_dry_run(self):
        """Test dry run mode."""
        # Create a test file
        Path('dry_run_test.txt').write_text("Test content")

        # Define mapping that would move the file
        mapping = {
            "dry_run_test.txt": "nonexistent_dir/moved_file.txt"
        }

        # Run with dry_run=True
        project_restructuring.move_files(mapping, True, False)

        # File should not be moved and target dir should not exist
        self.assertFalse(os.path.exists("nonexistent_dir"))
        self.assertTrue(os.path.exists("dry_run_test.txt"))

    def test_cleanup_empty_directories(self):
        """Test cleaning up empty directories."""
        # Create empty and non-empty dirs
        os.makedirs("empty_dir", exist_ok=True)
        os.makedirs("non_empty_dir", exist_ok=True)
        Path('non_empty_dir/file.txt').write_text("Test content")

        # Set up the cleanup list
        dirs_to_check = ["empty_dir", "non_empty_dir", "nonexistent_dir"]

        # Run the cleanup
        project_restructuring.cleanup_empty_directories(dirs_to_check, False, False)

        # Check results
        self.assertFalse(os.path.exists("empty_dir"))
        self.assertTrue(os.path.exists("non_empty_dir"))

    def test_integration(self):
        """Test the overall restructuring process with a very simple example."""
        # We'll use a minimal subset of the real structure for testing
        test_structure = {
            "src": {
                "code_conductor": {
                    "core": {}
                }
            }
        }

        # Define minimal file mapping
        test_mapping = {
            "cli.py": "src/code_conductor/core/cli.py"
        }

        # Define minimal directory mapping
        test_dir_mapping = {}  # Empty to avoid copying non-existent directories

        # Replace the actual dictionaries with our test ones
        original_structure = project_restructuring.NEW_STRUCTURE
        original_mapping = project_restructuring.MOVE_MAPPING
        original_dir_mapping = project_restructuring.DIR_COPY_MAPPING
        original_ai_setup_mapping = project_restructuring.AI_SETUP_MAPPING

        project_restructuring.NEW_STRUCTURE = test_structure
        project_restructuring.MOVE_MAPPING = test_mapping
        project_restructuring.DIR_COPY_MAPPING = test_dir_mapping
        project_restructuring.AI_SETUP_MAPPING = {}  # Empty to avoid copying non-existent directories

        # Create the directory structure first to ensure it exists
        project_restructuring.create_directory_structure(".", test_structure, False, False)

        # Verify the directory was created
        self.assertTrue(os.path.exists("src/code_conductor/core"))

        # Run main with sys.argv mocked to use dry run
        sys.argv = ['project_restructuring.py', '--dry-run']
        project_restructuring.main()

        # File should not be moved in dry run
        self.assertFalse(os.path.exists("src/code_conductor/core/cli.py"))
        self.assertTrue(os.path.exists("cli.py"))

        # Run for real
        sys.argv = ['project_restructuring.py']
        project_restructuring.main()

        # Check results
        self.assertTrue(os.path.exists("src/code_conductor/core/cli.py"))

        # Restore original values
        project_restructuring.NEW_STRUCTURE = original_structure
        project_restructuring.MOVE_MAPPING = original_mapping
        project_restructuring.DIR_COPY_MAPPING = original_dir_mapping
        project_restructuring.AI_SETUP_MAPPING = original_ai_setup_mapping


if __name__ == "__main__":
    print(f"Running tests for Project Restructuring...")
    unittest.main()
    print("Tests completed successfully!")
