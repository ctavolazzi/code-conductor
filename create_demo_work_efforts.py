#!/usr/bin/env python3
"""
Demo script to create new work efforts using the improved counter.

This script demonstrates how to create new work efforts with the correct
numerical prefix using the improved counter system. It supports both standard
sequential numbering and date-prefixed numbering.
"""

import os
import logging
import argparse
import datetime
from improved_counter import (
    get_counter,
    initialize_counter_from_existing_work_efforts,
    format_work_effort_filename
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WorkEffortCreator")

def create_work_effort(work_efforts_dir, title, description, status="active", use_date_prefix=False):
    """
    Create a new work effort with the proper numerical prefix.

    Args:
        work_efforts_dir: Base directory for work efforts
        title: Title of the work effort
        description: Description of the work effort
        status: Status of the work effort (active, completed, archived)
        use_date_prefix: Whether to use date prefix in the filename

    Returns:
        Path to the created work effort
    """
    # Ensure directory structure exists
    os.makedirs(work_efforts_dir, exist_ok=True)

    status_dir = os.path.join(work_efforts_dir, status)
    os.makedirs(status_dir, exist_ok=True)

    # Initialize or get counter
    counter_file = os.path.join(work_efforts_dir, "counter.json")

    # First check if we need to initialize from existing work efforts
    if not os.path.exists(counter_file):
        logger.info(f"Initializing counter based on existing work efforts in {work_efforts_dir}")
        initialize_counter_from_existing_work_efforts(work_efforts_dir, counter_file)

    # Get next count
    counter = get_counter(counter_file)
    count = counter.get_next_count()

    # Format the filename using the improved formatter
    base_filename = format_work_effort_filename(title, count, use_date_prefix)
    filename = f"{base_filename}.md"

    # Create full path to work effort file
    work_effort_path = os.path.join(status_dir, filename)

    # Format count string for display in the content
    if count <= 9999:
        count_str = f"{count:04d}"
    else:
        count_str = str(count)

    # Generate work effort content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# {title}

## Work Effort {count_str}

**Status:** {status}
**Created:** {timestamp}

## Description

{description}

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Notes

Add notes here as the work progresses.

"""

    # Write work effort file
    with open(work_effort_path, "w") as f:
        f.write(content)

    logger.info(f"Created work effort: {filename}")
    return work_effort_path

def main():
    """Main function to create demo work efforts."""
    parser = argparse.ArgumentParser(description="Create demo work efforts")
    parser.add_argument("--work-dir", default="./work_efforts", help="Work efforts directory")
    parser.add_argument("--use-date-prefix", action="store_true", help="Use date prefix in work effort filenames")
    parser.add_argument("--demo-large-numbers", action="store_true", help="Demo large number handling by creating work efforts with numbers >9999")
    args = parser.parse_args()

    # Create work efforts directory if it doesn't exist
    os.makedirs(args.work_dir, exist_ok=True)

    # Create "active" and "completed" directories if they don't exist
    active_dir = os.path.join(args.work_dir, "active")
    completed_dir = os.path.join(args.work_dir, "completed")
    archived_dir = os.path.join(args.work_dir, "archived")

    os.makedirs(active_dir, exist_ok=True)
    os.makedirs(completed_dir, exist_ok=True)
    os.makedirs(archived_dir, exist_ok=True)

    # Create first work effort with standard numbering
    first_path = create_work_effort(
        args.work_dir,
        "Sequential Numbering Example",
        "This work effort uses standard sequential numbering.",
        use_date_prefix=args.use_date_prefix
    )

    # Create second work effort with standard numbering
    second_path = create_work_effort(
        args.work_dir,
        "Another Sequential Example",
        "Another example of sequential numbering for work efforts.",
        use_date_prefix=args.use_date_prefix
    )

    paths = [first_path, second_path]

    # Optionally demo large number handling
    if args.demo_large_numbers:
        # Manually set counter to a high value to demonstrate >9999 handling
        counter_file = os.path.join(args.work_dir, "counter.json")
        counter = get_counter(counter_file)
        counter.initialize(9998)

        # Create work efforts that cross the 9999 threshold
        third_path = create_work_effort(
            args.work_dir,
            "Approaching Limit",
            "This work effort approaches the 9999 limit.",
            use_date_prefix=args.use_date_prefix
        )

        fourth_path = create_work_effort(
            args.work_dir,
            "At The Limit",
            "This work effort is at the 9999 limit.",
            use_date_prefix=args.use_date_prefix
        )

        fifth_path = create_work_effort(
            args.work_dir,
            "Beyond The Limit",
            "This work effort demonstrates the counter handling numbers beyond 9999.",
            use_date_prefix=args.use_date_prefix
        )

        paths.extend([third_path, fourth_path, fifth_path])

    # Log all created paths
    logger.info("Created work efforts at:")
    for i, path in enumerate(paths, 1):
        logger.info(f"{i}. {path}")

if __name__ == "__main__":
    main()