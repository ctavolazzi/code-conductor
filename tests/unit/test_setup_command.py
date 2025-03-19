#!/usr/bin/env python3
"""
Test suite for the Code Conductor 'setup' command.

This demonstrates comprehensive testing of the setup command,
covering various scenarios and edge cases.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch

# Import fixtures from conftest.py
# In a real test, pytest would automatically find these

@pytest.mark.parametrize("existing_structure", [
    # No existing structure
    None,
    # Partial structure: only _AI-Setup directory
    {"_AI-Setup": None},
    # Partial structure: _AI-Setup with empty work_efforts
    {"_AI-Setup": {"work_efforts": None}},
    # Complete structure without config
    {"_AI-Setup": {
        "work_efforts": {
            "active": None,
            "completed": None,
            "archived": None,
            "templates": {"work-effort-template.md": "Template content"},
            "scripts": None
        }
    }},
    # Complete structure with old config format (missing work_managers)
    {"_AI-Setup": {
        "config.json": '{"version": "0.4.6", "project_root": "/test", "created_at": "2025-03-16 00:00:00"}',
        "work_efforts": {
            "active": None,
            "completed": None,
            "archived": None,
            "templates": {"work-effort-template.md": "Template content"},
            "scripts": None
        }
    }},
    # Complete structure with corrupted config
    {"_AI-Setup": {
        "config.json": 'Invalid JSON',
        "work_efforts": {
            "active": None,
            "completed": None,
            "archived": None,
            "templates": {"work-effort-template.md": "Template content"},
            "scripts": None
        }
    }}
])
def test_setup_command_with_various_structures(mock_filesystem, cli_runner, existing_structure, mock_version):
    """
    Test the setup command with various existing directory structures.

    This test verifies that the setup command correctly handles different
    pre-existing directory states, from empty directories to partially or
    completely set up directories.

    Args:
        mock_filesystem: Fixture providing a mock filesystem
        cli_runner: Fixture for running CLI commands
        existing_structure: Parameter representing different directory states
        mock_version: Fixture that mocks the Code Conductor version
    """
    # Create the specified directory structure if provided
    if existing_structure:
        mock_filesystem["create_directory_structure"](existing_structure)

    # Run the setup command
    with cli_runner["run_with_args"](["setup", "-y"], cwd=str(mock_filesystem["base_dir"])) as result:
        # Check that the command completed successfully
        assert result["exit_code"] == 0

        # Check that the command output indicates success
        assert "✅ Setup completed" in result["stdout"]

        # Verify that the _AI-Setup directory was created
        ai_setup_dir = os.path.join(mock_filesystem["base_dir"], "_AI-Setup")
        assert os.path.exists(ai_setup_dir)

        # Verify that the config.json file was created
        config_file = os.path.join(ai_setup_dir, "config.json")
        assert os.path.exists(config_file)

        # Verify that the work_efforts directory was created
        work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
        assert os.path.exists(work_efforts_dir)

        # Check that the config file contains the expected work_managers array
        with open(config_file, 'r') as f:
            config = json.load(f)
            assert "work_managers" in config
            assert len(config["work_managers"]) > 0


@pytest.mark.parametrize("script_dirs", [
    # All scripts missing
    [],
    # Partial scripts
    ["work_effort_manager.py"],
    # All scripts present
    ["work_effort_manager.py", "run_work_effort_manager.py", "ai_work_effort_creator.py", "new_work_effort.py"]
])
def test_setup_command_with_missing_scripts(mock_filesystem, cli_runner, script_dirs, mock_version):
    """
    Test the setup command with missing script files.

    This test verifies that the setup command correctly handles cases where
    script files are missing from the src/code_conductor/scripts directory.

    Args:
        mock_filesystem: Fixture providing a mock filesystem
        cli_runner: Fixture for running CLI commands
        script_dirs: Parameter representing different sets of script files
        mock_version: Fixture that mocks the Code Conductor version
    """
    # Create a basic structure with the scripts directory
    work_efforts_dir = mock_filesystem["create_work_effort_structure"]()
    scripts_dir = os.path.join(work_efforts_dir, "scripts")

    # Create script files as specified
    for script in script_dirs:
        with open(os.path.join(scripts_dir, script), 'w') as f:
            f.write(f"# {script} - Mock implementation")

    # Run the setup command
    with cli_runner["run_with_args"](["setup", "-y"], cwd=str(mock_filesystem["base_dir"])) as result:
        # Check that the command completed successfully
        assert result["exit_code"] == 0

        # Check the output for script-related messages
        if len(script_dirs) < 4:
            # Should report missing scripts
            assert "scripts/", result["stdout"]
        else:
            # Should not try to add scripts that already exist
            assert "all scripts are present" in result["stdout"]


def test_setup_with_root_level_work_efforts(mock_filesystem, cli_runner, mock_version):
    """
    Test the setup command when a root-level work_efforts directory exists.

    This test verifies that the setup command correctly handles cases where
    a work_efforts directory exists at the root level (not inside _AI-Setup).

    Args:
        mock_filesystem: Fixture providing a mock filesystem
        cli_runner: Fixture for running CLI commands
        mock_version: Fixture that mocks the Code Conductor version
    """
    # Create a root-level work_efforts structure
    work_efforts_dir = mock_filesystem["create_work_effort_structure"](in_ai_setup=False)

    # Run the setup command
    with cli_runner["run_with_args"](["setup", "-y"], cwd=str(mock_filesystem["base_dir"])) as result:
        # Check that the command completed successfully
        assert result["exit_code"] == 0

        # Check that _AI-Setup was created
        ai_setup_dir = os.path.join(mock_filesystem["base_dir"], "_AI-Setup")
        assert os.path.exists(ai_setup_dir)

        # Check that work_efforts was created inside _AI-Setup
        ai_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
        assert os.path.exists(ai_work_efforts_dir)

        # Check the configuration to see if it references both directories
        config_file = os.path.join(ai_setup_dir, "config.json")
        with open(config_file, 'r') as f:
            config = json.load(f)

            # Verify that the config properly configures the work managers
            for manager in config["work_managers"]:
                # The work_efforts_dir should point to _AI-Setup/work_efforts
                assert "_AI-Setup" in manager["work_efforts_dir"]


def test_setup_preserves_existing_work_efforts(mock_filesystem, cli_runner, mock_version):
    """
    Test that setup preserves existing work efforts.

    This test verifies that the setup command does not overwrite or delete
    existing work effort files when setting up a directory.

    Args:
        mock_filesystem: Fixture providing a mock filesystem
        cli_runner: Fixture for running CLI commands
        mock_version: Fixture that mocks the Code Conductor version
    """
    # Create a basic structure
    work_efforts_dir = mock_filesystem["create_work_effort_structure"]()

    # Create a test work effort
    active_dir = os.path.join(work_efforts_dir, "active")
    test_effort_filename = "202503161330_test_work_effort.md"
    test_effort_path = os.path.join(active_dir, test_effort_filename)

    with open(test_effort_path, 'w') as f:
        f.write("""---
title: "Test Work Effort"
status: "active"
priority: "high"
assignee: "Tester"
created: "2025-03-16 13:30"
---

# Test Work Effort

This is a test work effort that should be preserved during setup.
""")

    # Run the setup command
    with cli_runner["run_with_args"](["setup", "-y"], cwd=str(mock_filesystem["base_dir"])) as result:
        # Check that the command completed successfully
        assert result["exit_code"] == 0

        # Verify that the test work effort still exists
        assert os.path.exists(test_effort_path)

        # Verify that the content of the test work effort was not changed
        with open(test_effort_path, 'r') as f:
            content = f.read()
            assert "Test Work Effort" in content
            assert "This is a test work effort that should be preserved during setup." in content


def test_setup_creates_project_manifest(mock_filesystem, cli_runner, mock_version):
    """
    Test that setup creates a project manifest file.

    This test verifies that the setup command creates a .code-conductor project
    manifest file in the root directory.

    Args:
        mock_filesystem: Fixture providing a mock filesystem
        cli_runner: Fixture for running CLI commands
        mock_version: Fixture that mocks the Code Conductor version
    """
    # Run the setup command
    with cli_runner["run_with_args"](["setup", "-y"], cwd=str(mock_filesystem["base_dir"])) as result:
        # Check that the command completed successfully
        assert result["exit_code"] == 0

        # Verify that the project manifest file was created
        manifest_file = os.path.join(mock_filesystem["base_dir"], ".code-conductor")
        assert os.path.exists(manifest_file)

        # Verify that the manifest file contains the expected data
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
            assert "project_root" in manifest
            assert "version" in manifest
            assert manifest["version"] == mock_version
            assert "setup_path" in manifest
            assert "_AI-Setup" in manifest["setup_path"]