#!/usr/bin/env python3
"""
Tests for work effort tracing functionality.
"""

import os
import json
import pytest
import datetime
from typing import Dict, Any
from src.code_conductor import WorkEffortManager

@pytest.fixture
def work_effort_manager(tmp_path):
    """Create a temporary WorkEffortManager for testing."""
    # Create a temporary project directory
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create work efforts directory structure
    work_efforts_dir = project_dir / "work_efforts"
    work_efforts_dir.mkdir()
    (work_efforts_dir / "active").mkdir()
    (work_efforts_dir / "completed").mkdir()
    (work_efforts_dir / "archived").mkdir()

    # Create manager with test directory
    manager = WorkEffortManager(project_dir=str(project_dir))
    return manager

@pytest.fixture
def sample_work_efforts(work_effort_manager):
    """Create a set of test work efforts with various relationships."""
    # Create parent work effort
    parent = work_effort_manager.create_work_effort(
        title="Test Parent Work Effort",
        content="""---
title: "Test Parent Work Effort"
status: "active"
priority: "high"
assignee: "Team"
created: "2025-03-19 10:07"
last_updated: "2025-03-19 10:07"
due_date: "2025-03-26"
tags: ["test", "tracing"]
---

# Test Parent Work Effort

## 📌 Linked Items
- [[Test Child Work Effort]]
- [[Test Sibling Work Effort]]
"""
    )

    # Create child work effort
    child = work_effort_manager.create_work_effort(
        title="Test Child Work Effort",
        content="""---
title: "Test Child Work Effort"
status: "active"
priority: "high"
assignee: "Team"
created: "2025-03-19 10:08"
last_updated: "2025-03-19 10:08"
due_date: "2025-03-26"
tags: ["test", "tracing"]
---

# Test Child Work Effort

## 📌 Linked Items
- [[Test Parent Work Effort]]
- [[Test Grandchild Work Effort]]
"""
    )

    # Create sibling work effort
    sibling = work_effort_manager.create_work_effort(
        title="Test Sibling Work Effort",
        content="""---
title: "Test Sibling Work Effort"
status: "active"
priority: "high"
assignee: "Team"
created: "2025-03-19 10:09"
last_updated: "2025-03-19 10:09"
due_date: "2025-03-26"
tags: ["test", "tracing"]
---

# Test Sibling Work Effort

## 📌 Linked Items
- [[Test Parent Work Effort]]
"""
    )

    # Create grandchild work effort
    grandchild = work_effort_manager.create_work_effort(
        title="Test Grandchild Work Effort",
        content="""---
title: "Test Grandchild Work Effort"
status: "active"
priority: "high"
assignee: "Team"
created: "2025-03-19 10:10"
last_updated: "2025-03-19 10:10"
due_date: "2025-03-26"
tags: ["test", "tracing"]
---

# Test Grandchild Work Effort

## 📌 Linked Items
- [[Test Child Work Effort]]
"""
    )

    return {
        "parent": parent,
        "child": child,
        "sibling": sibling,
        "grandchild": grandchild
    }

def test_find_related_work_efforts(work_effort_manager, sample_work_efforts):
    """Test finding related work efforts."""
    # Test finding relations from parent
    parent_relations = work_effort_manager.find_related_work_efforts("Test Parent Work Effort")
    assert len(parent_relations) == 2  # Child and sibling
    titles = [we.get("metadata", {}).get("title") for we in parent_relations]
    assert "Test Child Work Effort" in titles
    assert "Test Sibling Work Effort" in titles

    # Test finding relations from child
    child_relations = work_effort_manager.find_related_work_efforts("Test Child Work Effort")
    assert len(child_relations) == 2  # Parent and grandchild
    titles = [we.get("metadata", {}).get("title") for we in child_relations]
    assert "Test Parent Work Effort" in titles
    assert "Test Grandchild Work Effort" in titles

    # Test recursive relations from parent
    parent_recursive = work_effort_manager.find_related_work_efforts("Test Parent Work Effort", recursive=True)
    assert len(parent_recursive) == 4  # Child, sibling, grandchild (through child)
    titles = [we.get("metadata", {}).get("title") for we in parent_recursive]
    assert "Test Grandchild Work Effort" in titles

def test_get_work_effort_history(work_effort_manager, sample_work_efforts):
    """Test retrieving work effort history."""
    # Get history for a work effort
    history = work_effort_manager.get_work_effort_history("Test Parent Work Effort")
    assert len(history) >= 1  # At least creation event

    # Verify creation event
    creation_event = next(event for event in history if event["type"] == "created")
    assert creation_event["details"] == "Work effort created"

    # Update status and verify history
    work_effort_manager.update_work_effort_status("Test Parent Work Effort", "completed")
    history = work_effort_manager.get_work_effort_history("Test Parent Work Effort")
    assert len(history) >= 2  # Creation and status change
    status_event = next(event for event in history if event["type"] == "status_change")
    assert "Status changed from active to completed" in status_event["details"]

def test_trace_work_effort_chain(work_effort_manager, sample_work_efforts):
    """Test tracing work effort dependency chain."""
    # Test chain from grandchild
    chain = work_effort_manager.trace_work_effort_chain("Test Grandchild Work Effort")
    assert len(chain) == 3  # Parent -> Child -> Grandchild

    # Verify chain order
    titles = [we.get("metadata", {}).get("title") for we in chain]
    assert titles == [
        "Test Parent Work Effort",
        "Test Child Work Effort",
        "Test Grandchild Work Effort"
    ]

    # Test chain from sibling
    chain = work_effort_manager.trace_work_effort_chain("Test Sibling Work Effort")
    assert len(chain) == 2  # Parent -> Sibling
    titles = [we.get("metadata", {}).get("title") for we in chain]
    assert titles == ["Test Parent Work Effort", "Test Sibling Work Effort"]

def test_update_work_effort_status(work_effort_manager, sample_work_efforts):
    """Test updating work effort status and history tracking."""
    # Update status
    success = work_effort_manager.update_work_effort_status("Test Parent Work Effort", "completed")
    assert success

    # Verify status was updated
    work_effort = work_effort_manager.get_work_effort("Test Parent Work Effort")
    assert work_effort.get("status") == "completed"

    # Verify history was updated
    history = work_effort_manager.get_work_effort_history("Test Parent Work Effort")
    status_events = [event for event in history if event["type"] == "status_change"]
    assert len(status_events) == 1
    assert "Status changed from active to completed" in status_events[0]["details"]

def test_get_work_effort_content(work_effort_manager, sample_work_efforts):
    """Test retrieving work effort content."""
    # Get content of parent work effort
    content = work_effort_manager.get_work_effort_content("Test Parent Work Effort.md")
    assert content is not None
    assert "Test Parent Work Effort" in content
    assert "[[Test Child Work Effort]]" in content
    assert "[[Test Sibling Work Effort]]" in content

    # Test non-existent work effort
    content = work_effort_manager.get_work_effort_content("NonExistent.md")
    assert content is None

def test_work_effort_relationships(work_effort_manager, sample_work_efforts):
    """Test various work effort relationships and queries."""
    # Test finding all relations of a work effort
    parent = work_effort_manager.get_work_effort("Test Parent Work Effort")
    assert parent is not None
    assert parent.get("metadata", {}).get("title") == "Test Parent Work Effort"

    # Test finding work effort by title
    child = work_effort_manager.get_work_effort("Test Child Work Effort")
    assert child is not None
    assert child.get("metadata", {}).get("title") == "Test Child Work Effort"

    # Test finding work effort by filename
    sibling = work_effort_manager.get_work_effort("Test Sibling Work Effort.md")
    assert sibling is not None
    assert sibling.get("metadata", {}).get("title") == "Test Sibling Work Effort"

def test_error_handling(work_effort_manager):
    """Test error handling for various edge cases."""
    # Test finding relations of non-existent work effort
    relations = work_effort_manager.find_related_work_efforts("NonExistent")
    assert relations == []

    # Test getting history of non-existent work effort
    history = work_effort_manager.get_work_effort_history("NonExistent")
    assert history == []

    # Test tracing chain of non-existent work effort
    chain = work_effort_manager.trace_work_effort_chain("NonExistent")
    assert chain == []

    # Test updating status of non-existent work effort
    success = work_effort_manager.update_work_effort_status("NonExistent", "completed")
    assert not success