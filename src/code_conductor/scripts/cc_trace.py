#!/usr/bin/env python3
"""
Command-line interface for tracing work efforts.
"""

import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

try:
    # Direct import if installed as a package
    from code_conductor.core.work_effort.manager import WorkEffortManager
except ImportError:
    try:
        # Try importing from src directory
        from src.code_conductor.core.work_effort.manager import WorkEffortManager
    except ImportError:
        print("Error: Could not import WorkEffortManager. Make sure code_conductor is installed.")
        sys.exit(1)

def format_work_efforts_as_table(work_efforts: List[Dict[str, Any]]) -> str:
    """Format work efforts as a nicely formatted table."""
    if not work_efforts:
        return "No work efforts found."

    # Define column widths
    widths = {
        "Title": max(20, min(40, max(len(we.get("metadata", {}).get("title", "Untitled")) for we in work_efforts) + 2)),
        "Status": 10,
        "Created": 20,
        "Last Updated": 20
    }

    # Create header
    header = (
        f"{'Title':<{widths['Title']}} "
        f"{'Status':<{widths['Status']}} "
        f"{'Created':<{widths['Created']}} "
        f"{'Last Updated':<{widths['Last Updated']}}"
    )
    divider = "-" * (sum(widths.values()) + len(widths))

    # Create rows
    rows = []
    for we in work_efforts:
        metadata = we.get("metadata", {})
        title = metadata.get("title", "Untitled")
        status = we.get("status", "unknown")
        created = we.get("created_at", "")
        updated = we.get("last_updated", "")

        # Truncate title if too long
        if len(title) > widths["Title"] - 3:
            title = title[:widths["Title"] - 5] + "..."

        # Format row
        row = (
            f"{title:<{widths['Title']}} "
            f"{status:<{widths['Status']}} "
            f"{created:<{widths['Created']}} "
            f"{updated:<{widths['Last Updated']}}"
        )
        rows.append(row)

    # Combine all parts
    return "\n".join([header, divider] + rows)

def format_history_as_table(history: List[Dict[str, Any]]) -> str:
    """Format work effort history as a nicely formatted table."""
    if not history:
        return "No history found."

    # Define column widths
    widths = {
        "Timestamp": 20,
        "Event": 15,
        "Details": 50
    }

    # Create header
    header = (
        f"{'Timestamp':<{widths['Timestamp']}} "
        f"{'Event':<{widths['Event']}} "
        f"{'Details':<{widths['Details']}}"
    )
    divider = "-" * (sum(widths.values()) + len(widths))

    # Create rows
    rows = []
    for event in history:
        timestamp = event.get("timestamp", "")
        event_type = event.get("event", "")
        details = event.get("details", "")

        # Format row
        row = (
            f"{timestamp:<{widths['Timestamp']}} "
            f"{event_type:<{widths['Event']}} "
            f"{details:<{widths['Details']}}"
        )
        rows.append(row)

    # Combine all parts
    return "\n".join([header, divider] + rows)

def main():
    """Main entry point for the cc-trace command."""
    parser = argparse.ArgumentParser(description="Trace work efforts and their relationships")
    parser.add_argument("work_effort", help="The work effort to trace (by ID or title)")
    parser.add_argument("--related", action="store_true", help="Find related work efforts")
    parser.add_argument("--recursive", action="store_true", help="Recursively find relations of relations")
    parser.add_argument("--history", action="store_true", help="Show work effort history")
    parser.add_argument("--chain", action="store_true", help="Show the chain of work efforts")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    args = parser.parse_args()

    # Initialize the manager
    manager = WorkEffortManager()

    # Handle different tracing modes
    if args.related:
        work_efforts = manager.find_related_work_efforts(args.work_effort, recursive=args.recursive)
        if args.format == "table":
            print(format_work_efforts_as_table(work_efforts))
        else:
            print(json.dumps(work_efforts, indent=2))

    elif args.history:
        history = manager.get_work_effort_history(args.work_effort)
        if args.format == "table":
            print(format_history_as_table(history))
        else:
            print(json.dumps(history, indent=2))

    elif args.chain:
        chain = manager.trace_work_effort_chain(args.work_effort)
        if args.format == "table":
            print(format_work_efforts_as_table(chain))
        else:
            print(json.dumps(chain, indent=2))

    else:
        print("Please specify a tracing mode: --related, --history, or --chain")
        sys.exit(1)

if __name__ == "__main__":
    main()