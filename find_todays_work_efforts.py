#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Today's Work Efforts

This script searches the work efforts directory for documents created today
and displays them with their titles and creation times.

Usage:
    python find_todays_work_efforts.py [--directory DIR] [--format FORMAT]

Options:
    --directory DIR    The work efforts directory to search (default: .AI-Setup/work_efforts)
    --format FORMAT    Output format: 'simple', 'detailed', or 'json' (default: simple)
"""

import os
import re
import sys
import json
import argparse
import datetime
from pathlib import Path

# Regular expression for frontmatter extraction
FRONTMATTER_RE = re.compile(r'^---\s*$(.*?)^---\s*$', re.MULTILINE | re.DOTALL)
TITLE_RE = re.compile(r'title:\s*"([^"]+)"')
CREATED_RE = re.compile(r'created:\s*"([^"]+)"')
TIMESTAMP_RE = re.compile(r'(\d{10})')  # Match timestamp in filename like 2025031607

def extract_frontmatter(content):
    """Extract and parse frontmatter from the content."""
    match = FRONTMATTER_RE.search(content)
    if not match:
        return {}

    frontmatter = match.group(1)

    # Extract title
    title_match = TITLE_RE.search(frontmatter)
    title = title_match.group(1) if title_match else "Untitled"

    # Extract created timestamp
    created_match = CREATED_RE.search(frontmatter)
    created = created_match.group(1) if created_match else ""

    return {
        "title": title,
        "created": created
    }

def is_created_today(created_str):
    """Check if the created timestamp is from today."""
    if not created_str:
        return False

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return today in created_str

def has_today_timestamp(filename):
    """Check if the filename contains today's timestamp (YYYYMMDD)."""
    today = datetime.datetime.now().strftime("%Y%m%d")
    return today in filename

def find_todays_work_efforts(directory):
    """Find work efforts created today."""
    today_files = []

    # Walk through the work_efforts directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, directory)

                # Check if filename contains today's date
                if has_today_timestamp(file):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        metadata = extract_frontmatter(content)
                        metadata["file"] = relpath
                        metadata["path"] = filepath

                        # Double-check with created field if available
                        if "created" in metadata and not is_created_today(metadata["created"]):
                            print(f"Warning: File {relpath} has today's date in name but created field is different")

                        today_files.append(metadata)
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
                # If no timestamp in filename, check frontmatter
                else:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        metadata = extract_frontmatter(content)

                        # If created today based on frontmatter
                        if is_created_today(metadata.get("created", "")):
                            metadata["file"] = relpath
                            metadata["path"] = filepath
                            today_files.append(metadata)
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")

    return today_files

def format_output(work_efforts, format_type):
    """Format the output based on specified format."""
    if format_type == "json":
        return json.dumps(work_efforts, indent=2)

    if not work_efforts:
        return "No work efforts found for today."

    if format_type == "simple":
        output = f"Found {len(work_efforts)} work efforts for today:\n"
        for i, work in enumerate(work_efforts):
            output += f"{i+1}. {work.get('title', 'Untitled')} - {work.get('file', '')}\n"
        return output

    # Detailed format
    output = f"Found {len(work_efforts)} work efforts for today:\n"
    output += "=" * 80 + "\n"
    for i, work in enumerate(work_efforts):
        output += f"[{i+1}] {work.get('title', 'Untitled')}\n"
        output += f"File: {work.get('file', '')}\n"
        output += f"Created: {work.get('created', 'Unknown')}\n"
        output += f"Path: {work.get('path', '')}\n"
        output += "-" * 80 + "\n"
    return output

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Find work efforts created today")
    parser.add_argument("--directory", "-d",
                        default=".AI-Setup/work_efforts",
                        help="The work efforts directory to search")
    parser.add_argument("--format", "-f",
                        choices=["simple", "detailed", "json"],
                        default="simple",
                        help="Output format")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()

    # Ensure the directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory {args.directory} does not exist.")
        return 1

    # Find today's work efforts
    work_efforts = find_todays_work_efforts(args.directory)

    # Display results
    output = format_output(work_efforts, args.format)
    print(output)

    return 0

if __name__ == "__main__":
    sys.exit(main())