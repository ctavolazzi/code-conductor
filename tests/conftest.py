#!/usr/bin/env python3
"""
Test configuration and fixtures for the code-conductor test suite.

This file provides pytest fixtures and configuration to make testing easier.
"""

import os
import sys
import json
import pytest
import shutil
import tempfile
from contextlib import contextmanager
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root and src directories to Python path
# This should work with the pytest.ini configuration, but we add it here as a backup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the package
try:
    from src.code_conductor import __version__ as VERSION
except ImportError:
    VERSION = "0.0.0"

@pytest.fixture
def temp_work_directory(tmp_path):
    """Create a temporary working directory with _AI-Setup folder structure."""
    work_dir = tmp_path / "test_project"
    ai_setup_dir = work_dir / "_AI-Setup"
    work_efforts_dir = ai_setup_dir / "work_efforts"

    # Create directory structure
    work_dir.mkdir(exist_ok=True)
    ai_setup_dir.mkdir(exist_ok=True)
    work_efforts_dir.mkdir(exist_ok=True)

    # Create necessary subdirectories
    (work_efforts_dir / "active").mkdir(exist_ok=True)
    (work_efforts_dir / "completed").mkdir(exist_ok=True)
    (work_efforts_dir / "archived").mkdir(exist_ok=True)

    # Change to the working directory
    original_dir = os.getcwd()
    os.chdir(work_dir)

    yield work_dir

    # Change back to the original directory
    os.chdir(original_dir)

@pytest.fixture
def mock_config():
    """Return a mock configuration object."""
    return {
        "version": VERSION,
        "name": "Test Config",
        "work_efforts_dir": os.path.join("_AI-Setup", "work_efforts"),
        "default_work_effort_manager": "MainManager",
        "managers": [
            {
                "name": "MainManager",
                "path": os.path.join("_AI-Setup", "work_efforts")
            }
        ]
    }

@pytest.fixture
def mock_cli_context():
    """Return a mock CLI context object with common functions."""
    context = MagicMock()
    context.VERSION = VERSION
    context.find_work_efforts_directory.return_value = os.path.join("_AI-Setup", "work_efforts")
    return context

@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Create a temporary directory for testing with basic structure.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path object pointing to the temporary test directory
    """
    # Return the pytest-provided temporary directory
    yield tmp_path
    # No cleanup needed as pytest handles this automatically


@pytest.fixture
def mock_filesystem(temp_test_dir):
    """
    Create a more elaborate mock filesystem with configurable structure.

    This fixture creates a temporary directory with a structure that can be
    configured for different test scenarios.

    Args:
        temp_test_dir: The temporary directory fixture

    Returns:
        Dictionary with paths and utility functions for testing
    """
    # Helper function to create a directory structure
    def create_directory_structure(base_dir, structure):
        """Create a directory structure based on a nested dictionary."""
        for name, content in structure.items():
            path = os.path.join(base_dir, name)
            if isinstance(content, dict):
                # If content is a dict, it's a subdirectory
                os.makedirs(path, exist_ok=True)
                create_directory_structure(path, content)
            elif content is None:
                # If content is None, create an empty directory
                os.makedirs(path, exist_ok=True)
            else:
                # Otherwise, it's a file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)

    # Helper function to create a work effort structure
    def create_work_effort_structure(base_dir, in_ai_setup=True):
        """Create a standard work_efforts directory structure."""
        if in_ai_setup:
            ai_setup_dir = os.path.join(base_dir, "_AI-Setup")
            os.makedirs(ai_setup_dir, exist_ok=True)
            work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
        else:
            work_efforts_dir = os.path.join(base_dir, "work_efforts")

        # Create standard subdirectories
        for subdir in ["active", "completed", "archived", "templates", "scripts"]:
            os.makedirs(os.path.join(work_efforts_dir, subdir), exist_ok=True)

        # Create a template file
        template_path = os.path.join(work_efforts_dir, "templates", "work-effort-template.md")
        with open(template_path, 'w') as f:
            f.write("""---
title: "{{title}}"
status: "{{status}}" # options: active, paused, completed
priority: "{{priority}}" # options: low, medium, high, critical
assignee: "{{assignee}}"
created: "{{created}}" # YYYY-MM-DD HH:mm
last_updated: "{{last_updated}}" # YYYY-MM-DD HH:mm
due_date: "{{due_date}}" # YYYY-MM-DD
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# {{title}}

## 🚩 Objectives
- Clearly define goals for this work effort.

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references.

## 🐞 Issues Encountered
- Document issues and obstacles clearly.

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes.

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
""")

        # Create README
        readme_path = os.path.join(work_efforts_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write("""# Work Efforts

This directory contains structured documentation for tracking tasks, features, and bug fixes.

## Organization

- **active/**: Current work efforts being actively worked on
- **completed/**: Completed work efforts
- **archived/**: Archived work efforts (no longer relevant)
- **templates/**: Templates for creating new work efforts
- **scripts/**: Scripts for managing work efforts
""")

        return work_efforts_dir

    # Helper function to create a config file
    def create_config_file(base_dir, config_data=None, version="0.4.6"):
        """Create a config.json file in the _AI-Setup directory."""
        ai_setup_dir = os.path.join(base_dir, "_AI-Setup")
        os.makedirs(ai_setup_dir, exist_ok=True)

        # Default configuration
        default_config = {
            "version": version,
            "project_root": base_dir,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "default_work_manager": ".",
            "work_managers": [
                {
                    "name": os.path.basename(base_dir) or "main",
                    "path": ".",
                    "work_efforts_dir": os.path.join("_AI-Setup", "work_efforts"),
                    "use_manager": True,
                    "manager_script": os.path.join("_AI-Setup", "work_efforts", "scripts", "work_effort_manager.py"),
                    "runner_script": os.path.join("_AI-Setup", "work_efforts", "scripts", "run_work_effort_manager.py"),
                    "auto_start": True
                }
            ],
            "default_settings": {
                "assignee": "AI Assistant",
                "priority": "medium",
                "due_date": "+7d"
            }
        }

        # Merge with provided config data
        if config_data:
            for key, value in config_data.items():
                if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value

        # Write the config file
        config_file = os.path.join(ai_setup_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return config_file

    # Helper function to create project manifest file
    def create_project_manifest(base_dir):
        """Create a .code-conductor project manifest file."""
        manifest_file = os.path.join(base_dir, ".code-conductor")
        manifest_data = {
            "project_root": base_dir,
            "version": "0.4.6",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "setup_path": os.path.join(base_dir, "_AI-Setup")
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)

        return manifest_file

    # Return a dictionary of paths and helper functions
    fs = {
        "base_dir": temp_test_dir,
        "create_directory_structure": lambda structure: create_directory_structure(temp_test_dir, structure),
        "create_work_effort_structure": lambda in_ai_setup=True: create_work_effort_structure(temp_test_dir, in_ai_setup),
        "create_config_file": lambda config_data=None, version="0.4.6": create_config_file(temp_test_dir, config_data, version),
        "create_project_manifest": lambda: create_project_manifest(temp_test_dir)
    }

    yield fs


@pytest.fixture
def cli_runner():
    """
    Fixture for testing CLI commands.

    This fixture provides utilities for running CLI commands and capturing their output.

    Returns:
        Dictionary with utilities for running CLI commands
    """
    @contextmanager
    def run_with_args(args, cwd=None):
        """Run a CLI command with the specified arguments, capturing stdout and stderr."""
        # Save the original sys.argv
        old_argv = sys.argv
        old_cwd = os.getcwd()

        # Create a temporary file for capturing output
        stdout_file = tempfile.NamedTemporaryFile(delete=False)
        stderr_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            # Mock the command-line arguments
            sys.argv = ["code-conductor"] + args

            # Change to the specified directory if provided
            if cwd:
                os.chdir(cwd)

            # Redirect stdout and stderr
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = stdout_file, stderr_file

            # Import the main function
            from code_conductor.cli.cli import main_entry

            # Call the main function
            result = main_entry()

            # Flush the output
            sys.stdout.flush()
            sys.stderr.flush()

            # Reset stdout and stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr

            # Read the output
            with open(stdout_file.name, 'r') as f:
                stdout = f.read()
            with open(stderr_file.name, 'r') as f:
                stderr = f.read()

            # Yield the result
            yield {
                "exit_code": result,
                "stdout": stdout,
                "stderr": stderr
            }

        finally:
            # Restore the original sys.argv and cwd
            sys.argv = old_argv
            os.chdir(old_cwd)

            # Close and remove the temporary files
            stdout_file.close()
            stderr_file.close()
            os.unlink(stdout_file.name)
            os.unlink(stderr_file.name)

    # Return the runner utilities
    return {
        "run_with_args": run_with_args
    }


@pytest.fixture
def ai_content_generator():
    """
    Mock AI content generator for testing AI-generated content.

    Returns:
        Dictionary with utilities for mocking AI content generation
    """
    # Create a mock object for the generate_content_with_ollama function
    mock_generator = MagicMock()
    mock_generator.return_value = {
        "objectives": "- Test the functionality of the AI-generated content\n- Verify that the system integrates properly with AI",
        "tasks": "- [ ] Test with different AI models\n- [ ] Test with various prompt structures\n- [ ] Test error handling",
        "notes": "- The AI content generation should be robust and handle various inputs gracefully\n- Edge cases should be properly handled"
    }

    # Context manager for patching the AI content generator
    @contextmanager
    def patch_generator():
        with patch('code_conductor.utils.thought_process.generate_content_with_ollama', mock_generator):
            yield mock_generator

    # Return the mock generator and utility functions
    return {
        "mock_generator": mock_generator,
        "patch_generator": patch_generator
    }


@pytest.fixture
def mock_version():
    """Mock the version number for testing version-dependent functionality."""
    with patch('code_conductor.cli.cli.VERSION', '0.4.6'):
        with patch('code_conductor.__version__', '0.4.6'):
            yield '0.4.6'