#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieve Work Effort

A script to retrieve and display work effort content as context for AI assistants.
It locates work efforts by name, status or date, and outputs their content along with
any associated files to provide comprehensive context.

Usage:
    python retrieve_work_effort.py --name <n>
    python retrieve_work_effort.py --status <active|completed|archived>
    python retrieve_work_effort.py --date <YYYYMMDD>
    python retrieve_work_effort.py --latest [count]
    python retrieve_work_effort.py --related <work_effort_name>
"""

import os
import sys
import re
import argparse
import yaml
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define constants
WORK_EFFORTS_DIR = "_AI-Setup/work_efforts"
ACTIVE_DIR = os.path.join(WORK_EFFORTS_DIR, "active")
COMPLETED_DIR = os.path.join(WORK_EFFORTS_DIR, "completed")
ARCHIVED_DIR = os.path.join(WORK_EFFORTS_DIR, "archived")
SCRIPTS_DIR = os.path.join(WORK_EFFORTS_DIR, "scripts")

# Ensure we're in the project root
def ensure_project_root():
    """Make sure we're running from the project root directory."""
    if not os.path.isdir(WORK_EFFORTS_DIR):
        print(f"Error: {WORK_EFFORTS_DIR} directory not found.")
        print("Please run this script from the project root directory.")
        sys.exit(1)

def extract_frontmatter(content):
    """Extract frontmatter from markdown content."""
    logger.debug("Extracting frontmatter from content: %s", content[:100])  # Log first 100 characters
    frontmatter = {}
    if content.startswith('---'):
        end_marker = content.find('---', 3)
        if end_marker != -1:
            frontmatter_text = content[3:end_marker].strip()
            try:
                # Try parsing as YAML
                frontmatter = yaml.safe_load(frontmatter_text)
                logger.debug("Parsed frontmatter: %s", frontmatter)
            except yaml.YAMLError as e:
                logger.error("YAML parsing error: %s", e)
                # If YAML parsing fails, try a simple key-value approach
                for line in frontmatter_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter

def extract_links(content):
    """Extract Obsidian-style links from content."""
    # Match [[link_text]] or [[link|display_text]]
    links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
    return links

def find_work_effort_by_name(name):
    """Find a work effort by name across all directories."""
    directories = [ACTIVE_DIR, COMPLETED_DIR, ARCHIVED_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            continue

        # Search for exact filename match
        for filename in os.listdir(directory):
            if filename.endswith('.md') and name in filename:
                return os.path.join(directory, filename)

    # If no exact match, do a more flexible search
    for directory in directories:
        if not os.path.exists(directory):
            continue

        # Search by content or title in frontmatter
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check frontmatter
                    frontmatter = extract_frontmatter(content)
                    if frontmatter and 'title' in frontmatter and name.lower() in frontmatter['title'].lower():
                        return filepath

                    # Check content
                    if name.lower() in content.lower():
                        return filepath

    return None

def get_work_efforts_by_status(status):
    """Get all work efforts with the given status."""
    if status.lower() == 'active':
        directory = ACTIVE_DIR
    elif status.lower() == 'completed':
        directory = COMPLETED_DIR
    elif status.lower() == 'archived':
        directory = ARCHIVED_DIR
    else:
        print(f"Error: Unknown status '{status}'. Use 'active', 'completed', or 'archived'.")
        return []

    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return []

    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.md')]

def get_work_efforts_by_date(date_str):
    """Get all work efforts created on a specific date."""
    date_pattern = re.compile(rf'{date_str}\d*_.*\.md')
    result = []

    directories = [ACTIVE_DIR, COMPLETED_DIR, ARCHIVED_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            continue

        for filename in os.listdir(directory):
            if date_pattern.match(filename):
                result.append(os.path.join(directory, filename))

    return result

def get_latest_work_efforts(count=5):
    """Get the most recently created work efforts."""
    all_work_efforts = []

    directories = [ACTIVE_DIR, COMPLETED_DIR, ARCHIVED_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            continue

        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                filepath = os.path.join(directory, filename)
                creation_time = os.path.getctime(filepath)
                all_work_efforts.append((filepath, creation_time))

    # Sort by creation time (newest first)
    all_work_efforts.sort(key=lambda x: x[1], reverse=True)

    # Return only the filepaths
    return [filepath for filepath, _ in all_work_efforts[:count]]

def get_related_work_efforts(work_effort_path):
    """Get work efforts related to the given one."""
    related = []

    if not os.path.exists(work_effort_path):
        print(f"Error: Work effort {work_effort_path} not found.")
        return []

    with open(work_effort_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter for related_efforts
    frontmatter = extract_frontmatter(content)
    if frontmatter and 'related_efforts' in frontmatter:
        related_efforts = frontmatter['related_efforts']
        if isinstance(related_efforts, list):
            for related_effort in related_efforts:
                related_path = find_work_effort_by_name(related_effort)
                if related_path:
                    related.append(related_path)

    # Check for Obsidian-style links
    links = extract_links(content)
    for link in links:
        related_path = find_work_effort_by_name(link)
        if related_path:
            related.append(related_path)

    return list(set(related))  # Remove duplicates

def find_associated_script(work_effort_path):
    """Find scripts associated with this work effort."""
    if not work_effort_path:
        return []

    # Extract the base name of the work effort (without path and extension)
    work_effort_name = os.path.basename(work_effort_path).replace('.md', '')

    # Remove timestamp prefix like 202503160751_ if it exists
    if re.match(r'\d{12}_', work_effort_name):
        work_effort_name = work_effort_name[13:]

    # Look for scripts with the same name in the scripts directory
    associated_scripts = []
    if os.path.exists(SCRIPTS_DIR):
        for script in os.listdir(SCRIPTS_DIR):
            if work_effort_name.lower() in script.lower():
                associated_scripts.append(os.path.join(SCRIPTS_DIR, script))

    # Also look for scripts in the project root with the same name
    for script in os.listdir('.'):
        if script.endswith('.py') and work_effort_name.lower() in script.lower():
            associated_scripts.append(script)

    return associated_scripts

def display_work_effort(work_effort_path, show_associated=True, recursion_level=0):
    """Display a work effort and its associated files."""
    if not work_effort_path or not os.path.exists(work_effort_path):
        print(f"Work effort not found: {work_effort_path}")
        return

    indent = '  ' * recursion_level

    print(f"\n{indent}{'=' * 80}\n{indent}WORK EFFORT: {os.path.basename(work_effort_path)}\n{indent}{'=' * 80}\n")

    # Display the work effort content
    with open(work_effort_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"{indent}{content}")

    if show_associated:
        # Find and display associated scripts
        associated_scripts = find_associated_script(work_effort_path)
        if associated_scripts:
            print(f"\n{indent}{'=' * 80}\n{indent}ASSOCIATED SCRIPTS:\n{indent}{'=' * 80}\n")
            for script_path in associated_scripts:
                print(f"\n{indent}--- {os.path.basename(script_path)} ---\n")
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                        print(f"{indent}{script_content}")
                except Exception as e:
                    print(f"{indent}Error reading script: {e}")

def main():
    """Main function."""
    ensure_project_root()

    parser = argparse.ArgumentParser(description="Retrieve and display work effort content for AI context")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--name', help='Work effort name or part of name')
    group.add_argument('--status', help='Retrieve work efforts by status (active, completed, archived)')
    group.add_argument('--date', help='Retrieve work efforts by date (YYYYMMDD format)')
    group.add_argument('--latest', nargs='?', const=5, type=int, help='Get latest work efforts (default: 5)')
    group.add_argument('--related', help='Find work efforts related to the specified one')

    parser.add_argument('--no-associated', action='store_true', help='Do not show associated scripts')
    parser.add_argument('--recursive', action='store_true', help='Recursively display related work efforts')

    args = parser.parse_args()

    work_efforts = []

    if args.name:
        work_effort_path = find_work_effort_by_name(args.name)
        if work_effort_path:
            work_efforts = [work_effort_path]
        else:
            print(f"No work effort found matching '{args.name}'")
    elif args.status:
        work_efforts = get_work_efforts_by_status(args.status)
    elif args.date:
        work_efforts = get_work_efforts_by_date(args.date)
    elif args.latest is not None:
        work_efforts = get_latest_work_efforts(args.latest)
    elif args.related:
        related_base = find_work_effort_by_name(args.related)
        if related_base:
            work_efforts = get_related_work_efforts(related_base)
            # Include the base work effort as the first item
            work_efforts.insert(0, related_base)
        else:
            print(f"No work effort found matching '{args.related}'")

    if not work_efforts:
        print("No work efforts found.")
        return

    visited = set()
    for i, work_effort_path in enumerate(work_efforts):
        if work_effort_path in visited:
            continue

        visited.add(work_effort_path)
        display_work_effort(work_effort_path, not args.no_associated, 0)

        # If recursive and this is the first work effort, find and display related efforts
        if args.recursive and i == 0 and args.related:
            related = get_related_work_efforts(work_effort_path)
            for related_path in related:
                if related_path not in visited:
                    visited.add(related_path)
                    display_work_effort(related_path, not args.no_associated, 1)

if __name__ == "__main__":
    main()