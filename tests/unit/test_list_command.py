#!/usr/bin/env python3
"""
Test suite for the Code Conductor 'list' command.

This demonstrates testing the list command without requiring
the actual code_conductor package.
"""

import os
import sys
import pytest
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

class MockWorkEffort:
    """Mock work effort class for testing."""
    def __init__(self, title, status, priority, created_at, filename=None):
        self.title = title
        self.status = status
        self.priority = priority
        self.created_at = created_at
        self.filename = filename or f"{datetime.now().strftime('%Y%m%d%H%M')}_{title.lower().replace(' ', '_')}.md"

    def __str__(self):
        return f"{self.title} ({self.status}, {self.priority})"

class MockListCommand:
    """Mock implementation of the list command."""
    @staticmethod
    def list_work_efforts(status=None, priority=None, manager=None):
        """Mock implementation of listing work efforts."""
        # Create some dummy work efforts
        work_efforts = [
            MockWorkEffort("Test Project 1", "active", "high", "2025-03-15"),
            MockWorkEffort("Bug Fix Task", "active", "critical", "2025-03-16"),
            MockWorkEffort("Documentation", "completed", "medium", "2025-03-10"),
            MockWorkEffort("Refactoring", "paused", "low", "2025-03-12"),
            MockWorkEffort("Feature Implementation", "active", "medium", "2025-03-14")
        ]

        # Filter by status if provided
        if status:
            work_efforts = [we for we in work_efforts if we.status == status]

        # Filter by priority if provided
        if priority:
            work_efforts = [we for we in work_efforts if we.priority == priority]

        return work_efforts

@pytest.fixture
def mock_list_command():
    """Fixture providing a mock list command."""
    return MockListCommand()

def test_list_all_work_efforts(mock_list_command):
    """Test listing all work efforts."""
    work_efforts = mock_list_command.list_work_efforts()
    assert len(work_efforts) == 5
    assert any(we.title == "Test Project 1" for we in work_efforts)
    assert any(we.title == "Bug Fix Task" for we in work_efforts)

def test_list_by_status(mock_list_command):
    """Test filtering work efforts by status."""
    active_work_efforts = mock_list_command.list_work_efforts(status="active")
    assert len(active_work_efforts) == 3
    assert all(we.status == "active" for we in active_work_efforts)

    completed_work_efforts = mock_list_command.list_work_efforts(status="completed")
    assert len(completed_work_efforts) == 1
    assert completed_work_efforts[0].title == "Documentation"

    paused_work_efforts = mock_list_command.list_work_efforts(status="paused")
    assert len(paused_work_efforts) == 1
    assert paused_work_efforts[0].title == "Refactoring"

def test_list_by_priority(mock_list_command):
    """Test filtering work efforts by priority."""
    high_priority = mock_list_command.list_work_efforts(priority="high")
    assert len(high_priority) == 1
    assert high_priority[0].title == "Test Project 1"

    critical_priority = mock_list_command.list_work_efforts(priority="critical")
    assert len(critical_priority) == 1
    assert critical_priority[0].title == "Bug Fix Task"

def test_list_by_status_and_priority(mock_list_command):
    """Test filtering work efforts by both status and priority."""
    active_medium = mock_list_command.list_work_efforts(status="active", priority="medium")
    assert len(active_medium) == 1
    assert active_medium[0].title == "Feature Implementation"

@patch('os.listdir')
def test_list_with_filesystem_mocking(mock_listdir):
    """Test list command with mocked filesystem."""
    # Setup the mock to return a list of files
    mock_listdir.return_value = [
        "20250315_project_alpha.md",
        "20250316_project_beta.md",
        "20250317_project_gamma.md",
        "README.md"  # Non-work effort file
    ]

    # Create a mock for open to return predefined content
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        """---
title: "Project Alpha"
status: "active"
priority: "high"
created: "2025-03-15"
---""",
        """---
title: "Project Beta"
status: "completed"
priority: "medium"
created: "2025-03-16"
---""",
        """---
title: "Project Gamma"
status: "active"
priority: "low"
created: "2025-03-17"
---"""
    ]

    # Use the mock to simulate reading work effort files
    with patch('builtins.open', mock_open):
        # This simulates how the real code would iterate over files and read them
        work_efforts = []
        for filename in os.listdir():
            if filename.endswith('.md') and filename != "README.md":
                with open(filename, 'r') as f:
                    content = f.read()
                    # Extract title from the content
                    title = content.split('title: "')[1].split('"')[0]
                    status = content.split('status: "')[1].split('"')[0]
                    priority = content.split('priority: "')[1].split('"')[0]
                    work_efforts.append({
                        'filename': filename,
                        'title': title,
                        'status': status,
                        'priority': priority
                    })

        # Assertions based on our mocked data
        assert len(work_efforts) == 3
        assert work_efforts[0]['title'] == "Project Alpha"
        assert work_efforts[1]['status'] == "completed"
        assert work_efforts[2]['priority'] == "low"