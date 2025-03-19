#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to index all work efforts across the project.

This script scans the entire project for work efforts, regardless of their location,
and creates a comprehensive index of all work efforts found.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from code_conductor.core.project import find_project_root
from code_conductor.core.work_effort.manager import WorkEffortManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("index_work_efforts")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Index all work efforts across the project."
    )

    parser.add_argument(
        "--project-dir", "-d",
        default=os.getcwd(),
        help="Project directory to scan (default: current directory)"
    )

    parser.add_argument(
        "--output", "-o",
        default="work_efforts_index.json",
        help="Output file for the index (default: work_efforts_index.json)"
    )

    parser.add_argument(
        "--no-save", "-n",
        action="store_true",
        help="Don't save the index to a file"
    )

    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show summary of work efforts"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["json", "table"],
        default="table",
        help="Output format (default: table)"
    )

    parser.add_argument(
        "--thorough", "-t",
        action="store_true",
        help="Use thorough search to find all possible work efforts (may be slower but more comprehensive)"
    )

    parser.add_argument(
        "--simple", "-S",
        action="store_true",
        help="Use simple search (faster but less comprehensive)"
    )

    parser.add_argument(
        "--filter", "-F",
        help="Filter results by text in title or content"
    )

    return parser.parse_args()

def format_work_efforts_as_table(work_efforts: List[Dict[str, Any]]) -> str:
    """Format work efforts as a nicely formatted table."""
    if not work_efforts:
        return "No work efforts found."

    # Define column widths
    widths = {
        "Title": max(20, min(40, max(len(we.get("metadata", {}).get("title", "Untitled")) for we in work_efforts) + 2)),
        "Status": 10,
        "Location": 30,
        "Last Modified": 20
    }

    # Create header
    header = (
        f"{'Title':<{widths['Title']}} "
        f"{'Status':<{widths['Status']}} "
        f"{'Location':<{widths['Location']}} "
        f"{'Last Modified':<{widths['Last Modified']}}"
    )
    divider = "-" * (sum(widths.values()) + len(widths))

    # Create rows
    rows = []
    for we in work_efforts:
        metadata = we.get("metadata", {})
        title = metadata.get("title", "Untitled")
        status = we.get("status", "unknown")
        container = we.get("container_type", "unknown")
        location = we.get("relative_path", "")
        modified = we.get("last_modified", "")

        # Truncate title if too long
        if len(title) > widths["Title"] - 3:
            title = title[:widths["Title"] - 5] + "..."

        # Truncate location if too long
        if len(location) > widths["Location"] - 3:
            location = location[:widths["Location"] - 5] + "..."

        # Format row
        row = (
            f"{title:<{widths['Title']}} "
            f"{status:<{widths['Status']}} "
            f"{location:<{widths['Location']}} "
            f"{modified:<{widths['Last Modified']}}"
        )
        rows.append(row)

    # Combine all parts
    return "\n".join([header, divider] + rows)

def generate_summary(work_efforts: List[Dict[str, Any]]) -> str:
    """Generate a summary of work efforts."""
    if not work_efforts:
        return "No work efforts found."

    # Count by status
    status_counts = {}
    for we in work_efforts:
        status = we.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    # Count by container type
    container_counts = {}
    for we in work_efforts:
        container = we.get("container_type", "unknown")
        container_counts[container] = container_counts.get(container, 0) + 1

    # Count by directory
    dir_counts = {}
    for we in work_efforts:
        rel_path = we.get("relative_path", "")
        dir_path = os.path.dirname(rel_path)
        if not dir_path:
            dir_path = "(root)"
        dir_counts[dir_path] = dir_counts.get(dir_path, 0) + 1

    # Find newest and oldest
    work_efforts_with_dates = [we for we in work_efforts if we.get("last_modified")]
    if work_efforts_with_dates:
        newest = max(work_efforts_with_dates, key=lambda we: we.get("last_modified", ""))
        oldest = min(work_efforts_with_dates, key=lambda we: we.get("last_modified", ""))
    else:
        newest = oldest = None

    # Build summary
    summary = [
        f"Total work efforts: {len(work_efforts)}",
        "\nBy status:",
    ]
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        summary.append(f"  - {status}: {count}")

    summary.append("\nBy container type:")
    for container, count in sorted(container_counts.items(), key=lambda x: x[1], reverse=True):
        summary.append(f"  - {container}: {count}")

    # Add top directories
    top_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    if top_dirs:
        summary.append("\nTop directories:")
        for dir_path, count in top_dirs:
            summary.append(f"  - {dir_path}: {count}")

    if newest:
        summary.append(f"\nNewest work effort: {newest['metadata'].get('title', 'Untitled')} ({newest['last_modified']})")
    if oldest:
        summary.append(f"Oldest work effort: {oldest['metadata'].get('title', 'Untitled')} ({oldest['last_modified']})")

    return "\n".join(summary)

def main():
    """Main entry point for the index_work_efforts script."""
    try:
        # Get project root
        project_root = find_project_root()
        if not project_root:
            logger.error("❌ Could not find project root")
            return 1

        # Initialize manager
        manager = WorkEffortManager(project_dir=project_root)
        logger.info(f"Scanning project directory: {project_root}")

        # Index all work efforts
        work_efforts = manager.index_all_work_efforts()
        if work_efforts is None:
            logger.error("❌ Failed to index work efforts")
            return 1

        logger.info(f"✅ Indexed {len(work_efforts)} work efforts")
        return 0

    except Exception as e:
        logger.error(f"Error indexing work efforts: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())