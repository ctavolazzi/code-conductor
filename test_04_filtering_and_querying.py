#!/usr/bin/env python3
"""
Test work effort filtering and querying capabilities.

This test verifies:
1. Filtering work efforts by status
2. Filtering work efforts by priority
3. Filtering work efforts by assignee
4. Filtering work efforts by due date
5. Filtering work efforts by title/content
6. Querying work efforts with multiple criteria
7. Handling empty query results
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from test_utils import (
    create_test_environment,
    cleanup_test_environment,
    create_test_work_effort,
    logger
)

# Set up additional logging for this test file
if __name__ == "__main__":
    # Configure a more verbose logging level when running this file directly
    logger.setLevel(logging.DEBUG)
    # Add a console handler that shows more detail for direct execution
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.debug("Running test_04_filtering_and_querying.py with enhanced logging")

def test_filter_by_status():
    """Test filtering work efforts by status."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting filter by status test")

        # Create work efforts with different statuses
        titles = []

        # Create active work efforts
        for i in range(3):
            title = f"Active Work Effort {i} {int(time.time())}"
            folder_path, filename = create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )
            titles.append(title)

        # Create completed work efforts
        for i in range(2):
            title = f"Completed Work Effort {i} {int(time.time())}"
            folder_path, filename = create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )
            # Update to completed
            manager.update_work_effort_status(filename, "completed", "active")
            titles.append(title)

        # Create archived work efforts
        for i in range(1):
            title = f"Archived Work Effort {i} {int(time.time())}"
            folder_path, filename = create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )
            # Update to archived
            manager.update_work_effort_status(filename, "archived", "active")
            titles.append(title)

        # Filter by active status
        active_wes = manager.filter_work_efforts(status="active")
        if len(active_wes) != 3:
            logger.error(f"Expected 3 active work efforts, got {len(active_wes)}")
            return False

        # Filter by completed status
        completed_wes = manager.filter_work_efforts(status="completed")
        if len(completed_wes) != 2:
            logger.error(f"Expected 2 completed work efforts, got {len(completed_wes)}")
            return False

        # Filter by archived status
        archived_wes = manager.filter_work_efforts(status="archived")
        if len(archived_wes) != 1:
            logger.error(f"Expected 1 archived work effort, got {len(archived_wes)}")
            return False

        # Get all work efforts
        all_wes = manager.get_work_efforts()
        if len(all_wes) != 6:
            logger.error(f"Expected 6 total work efforts, got {len(all_wes)}")
            return False

        logger.info("Filter by status test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_filter_by_priority():
    """Test filtering work efforts by priority."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting filter by priority test")

        # Create work efforts with different priorities
        priorities = ["low", "medium", "high", "critical"]

        for priority in priorities:
            # Create 2 work efforts with each priority
            for i in range(2):
                title = f"{priority.capitalize()} Priority Work Effort {i} {int(time.time())}"
                create_test_work_effort(
                    manager,
                    title=title,
                    assignee="tester",
                    priority=priority,
                    due_date="2025-12-31"
                )

        # Filter by each priority
        for priority in priorities:
            filtered_wes = manager.filter_work_efforts(priority=priority)
            if len(filtered_wes) != 2:
                logger.error(f"Expected 2 {priority} priority work efforts, got {len(filtered_wes)}")
                return False

        # Filter by multiple priorities
        multi_filtered = manager.filter_work_efforts(priority=["high", "critical"])
        if len(multi_filtered) != 4:
            logger.error(f"Expected 4 high/critical priority work efforts, got {len(multi_filtered)}")
            return False

        logger.info("Filter by priority test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_filter_by_assignee():
    """Test filtering work efforts by assignee."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting filter by assignee test")

        # Create work efforts with different assignees
        assignees = ["developer", "tester", "manager", "designer", "unassigned"]

        for assignee in assignees:
            title = f"Work Effort for {assignee.capitalize()} {int(time.time())}"
            create_test_work_effort(
                manager,
                title=title,
                assignee=assignee,
                priority="medium",
                due_date="2025-12-31"
            )

        # Filter by each assignee
        for assignee in assignees:
            filtered_wes = manager.filter_work_efforts(assignee=assignee)
            if len(filtered_wes) != 1:
                logger.error(f"Expected 1 work effort for {assignee}, got {len(filtered_wes)}")
                return False

        # Filter by multiple assignees
        multi_filtered = manager.filter_work_efforts(assignee=["developer", "tester"])
        if len(multi_filtered) != 2:
            logger.error(f"Expected 2 work efforts for developer/tester, got {len(multi_filtered)}")
            return False

        logger.info("Filter by assignee test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_filter_by_due_date():
    """Test filtering work efforts by due date."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting filter by due date test")

        # Create work efforts with different due dates
        today = datetime.now().strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        next_year = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

        due_dates = [today, next_week, next_month, next_year]

        for due_date in due_dates:
            title = f"Due {due_date} Work Effort {int(time.time())}"
            create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date=due_date
            )

        # Filter by due before a date
        before_next_year = manager.filter_work_efforts(due_before=next_year)
        if len(before_next_year) != 3:
            logger.error(f"Expected 3 work efforts due before {next_year}, got {len(before_next_year)}")
            return False

        # Filter by due after a date
        after_today = manager.filter_work_efforts(due_after=today)
        if len(after_today) != 3:
            logger.error(f"Expected 3 work efforts due after {today}, got {len(after_today)}")
            return False

        # Filter by date range
        in_range = manager.filter_work_efforts(due_after=next_week, due_before=next_year)
        if len(in_range) != 2:
            logger.error(f"Expected 2 work efforts due between {next_week} and {next_year}, got {len(in_range)}")
            return False

        logger.info("Filter by due date test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_filter_by_title_content():
    """Test filtering work efforts by title/content."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting filter by title/content test")

        # Create work efforts with unique keywords in titles
        unique_keywords = ["Project", "Bug", "Feature", "Meeting", "Release"]

        for keyword in unique_keywords:
            title = f"{keyword} Work Effort {int(time.time())}"
            create_test_work_effort(
                manager,
                title=title,
                assignee="tester",
                priority="medium",
                due_date="2025-12-31"
            )

        # Filter by title
        for keyword in unique_keywords:
            filtered_wes = manager.filter_work_efforts(title_contains=keyword)
            if len(filtered_wes) != 1:
                logger.error(f"Expected 1 work effort with {keyword} in title, got {len(filtered_wes)}")
                return False

        # Create work effort with specific content
        content_keyword = "UNIQUE_CONTENT_STRING"
        title = f"Content Test {int(time.time())}"
        folder_path, filename = create_test_work_effort(
            manager,
            title=title,
            assignee="tester",
            priority="medium",
            due_date="2025-12-31"
        )

        # Update the content
        folder_name = os.path.splitext(filename)[0]
        file_path = os.path.join(manager.active_dir, folder_name, filename)

        with open(file_path, 'r') as f:
            content = f.read()

        updated_content = content + f"\n\n## Test Content\n\nThis is a test with {content_keyword} in the content."

        with open(file_path, 'w') as f:
            f.write(updated_content)

        # Refresh the manager's work efforts
        manager._load_work_efforts()

        # Filter by content
        content_filtered = manager.filter_work_efforts(title_contains=content_keyword)
        if len(content_filtered) != 1:
            logger.error(f"Expected 1 work effort with {content_keyword} in title, got {len(content_filtered)}")
            return False

        logger.info("Filter by title/content test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_multi_criteria_query():
    """Test querying work efforts with multiple criteria."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting multi-criteria query test")

        # Create various work efforts with different combinations
        create_test_work_effort(
            manager,
            title="High Priority Bug",
            assignee="developer",
            priority="high",
            due_date="2025-01-15"
        )

        create_test_work_effort(
            manager,
            title="Medium Priority Bug",
            assignee="tester",
            priority="medium",
            due_date="2025-02-15"
        )

        create_test_work_effort(
            manager,
            title="High Priority Feature",
            assignee="developer",
            priority="high",
            due_date="2025-03-15"
        )

        create_test_work_effort(
            manager,
            title="Low Priority Feature",
            assignee="designer",
            priority="low",
            due_date="2025-04-15"
        )

        # Create and complete one work effort
        folder_path, filename = create_test_work_effort(
            manager,
            title="Completed Feature",
            assignee="developer",
            priority="medium",
            due_date="2025-05-15"
        )
        manager.update_work_effort_status(filename, "completed", "active")

        # Test various combinations of filters

        # High priority assigned to developer
        filtered = manager.filter_work_efforts(
            priority="high",
            assignee="developer"
        )
        if len(filtered) != 2:
            logger.error(f"Expected 2 high priority work efforts for developer, got {len(filtered)}")
            return False

        # High priority active bugs
        filtered = manager.filter_work_efforts(
            priority="high",
            status="active",
            title_contains="Bug"
        )
        if len(filtered) != 1:
            logger.error(f"Expected 1 high priority active bug, got {len(filtered)}")
            return False

        # Features due before April
        filtered = manager.filter_work_efforts(
            title_contains="Feature",
            due_before="2025-04-01"
        )
        if len(filtered) != 1:
            logger.error(f"Expected 1 feature due before April, got {len(filtered)}")
            return False

        # Developer's completed work
        filtered = manager.filter_work_efforts(
            assignee="developer",
            status="completed"
        )
        if len(filtered) != 1:
            logger.error(f"Expected 1 completed work effort for developer, got {len(filtered)}")
            return False

        logger.info("Multi-criteria query test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def test_empty_query_results():
    """Test handling of empty query results."""
    test_dir, manager = create_test_environment()

    try:
        logger.info("Starting empty query results test")

        # Create some work efforts
        create_test_work_effort(
            manager,
            title="Test Work Effort",
            assignee="developer",
            priority="medium",
            due_date="2025-12-31"
        )

        # Query for non-existent criteria
        filtered = manager.filter_work_efforts(
            priority="nonexistent",
        )
        if filtered is not None and len(filtered) != 0:
            logger.error(f"Expected empty list for non-existent priority, got {len(filtered)}")
            return False

        filtered = manager.filter_work_efforts(
            assignee="nonexistent",
        )
        if filtered is not None and len(filtered) != 0:
            logger.error(f"Expected empty list for non-existent assignee, got {len(filtered)}")
            return False

        filtered = manager.filter_work_efforts(
            title_contains="nonexistent",
        )
        if filtered is not None and len(filtered) != 0:
            logger.error(f"Expected empty list for non-existent title, got {len(filtered)}")
            return False

        filtered = manager.filter_work_efforts(
            status="nonexistent",
        )
        if filtered is not None and len(filtered) != 0:
            logger.error(f"Expected empty list for non-existent status, got {len(filtered)}")
            return False

        logger.info("Empty query results test PASSED")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        cleanup_test_environment(test_dir)

def main():
    """Run all tests in this file."""
    tests = [
        ("Filter by Status", test_filter_by_status),
        ("Filter by Priority", test_filter_by_priority),
        ("Filter by Assignee", test_filter_by_assignee),
        ("Filter by Due Date", test_filter_by_due_date),
        ("Filter by Title/Content", test_filter_by_title_content),
        ("Multi-Criteria Query", test_multi_criteria_query),
        ("Empty Query Results", test_empty_query_results),
    ]

    failures = 0

    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        result = test_func()

        if result:
            logger.info(f"✓ {test_name}: PASSED")
        else:
            logger.error(f"✗ {test_name}: FAILED")
            failures += 1

    if failures:
        logger.error(f"{failures} tests failed")
        return 1
    else:
        logger.info("All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())