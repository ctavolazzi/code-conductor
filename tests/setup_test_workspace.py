#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Workspace Setup Script

This script provides functions to set up and tear down a test workspace for testing
the Code Conductor CLI.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

def setup_test_workspace():
    """Set up a fresh test workspace."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_workspace = os.path.join(project_root, "test_workspace")

    # Remove existing test workspace if it exists
    if os.path.exists(test_workspace):
        shutil.rmtree(test_workspace)

    # Create test workspace directory structure
    os.makedirs(test_workspace)
    os.makedirs(os.path.join(test_workspace, "work_efforts"))
    os.makedirs(os.path.join(test_workspace, "work_efforts", "active"))
    os.makedirs(os.path.join(test_workspace, "work_efforts", "completed"))
    os.makedirs(os.path.join(test_workspace, "work_efforts", "archived"))
    os.makedirs(os.path.join(test_workspace, "work_efforts", "templates"))
    os.makedirs(os.path.join(test_workspace, "work_efforts", "scripts"))

    # Create test workspace config
    config = {
        "version": "0.5.0",
        "project_root": project_root,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "default_work_manager": "test_workspace",
        "work_managers": [
            {
                "name": "TestManager",
                "path": "test_workspace",
                "work_efforts_dir": "work_efforts",
                "use_manager": True,
                "manager_script": "work_efforts/scripts/work_effort_manager.py",
                "runner_script": "work_efforts/scripts/run_work_effort_manager.py",
                "auto_start": True
            }
        ],
        "default_settings": {
            "assignee": "Test User",
            "priority": "medium",
            "due_date": "+7d"
        }
    }

    # Create test workspace manifest
    manifest = {
        "version": "0.5.0",
        "setup_path": "test_workspace",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Write config and manifest files
    with open(os.path.join(test_workspace, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    with open(os.path.join(project_root, ".code-conductor"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Test workspace created at: {test_workspace}")
    return test_workspace

def teardown_test_workspace():
    """Clean up the test workspace."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_workspace = os.path.join(project_root, "test_workspace")

    if os.path.exists(test_workspace):
        shutil.rmtree(test_workspace)
        print(f"✅ Test workspace removed: {test_workspace}")

    manifest_file = os.path.join(project_root, ".code-conductor")
    if os.path.exists(manifest_file):
        os.remove(manifest_file)
        print(f"✅ Project manifest removed: {manifest_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "teardown":
        teardown_test_workspace()
    else:
        setup_test_workspace()