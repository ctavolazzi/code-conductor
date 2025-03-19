#!/usr/bin/env python3
"""
List Active Work Efforts Script

This script scans the workspace for active work efforts and outputs them as a JSON object.
"""

import os
import json
import glob
import re
from pathlib import Path

def extract_metadata(file_path):
    """Extract metadata from a work effort file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract title
        title_match = re.search(r'title:\s*[\"\'](.*?)[\"\']', content) or re.search(r'title:\s*(.*?)(\n|$)', content)
        title = title_match.group(1).strip() if title_match else os.path.basename(file_path)

        # Extract status
        status_match = re.search(r'status:\s*[\"\'](.*?)[\"\']', content) or re.search(r'status:\s*(.*?)(\n|$)', content)
        status = status_match.group(1).strip() if status_match else 'unknown'

        # Skip completed items
        if status.lower() == 'completed':
            return None

        # Extract priority
        priority_match = re.search(r'priority:\s*[\"\'](.*?)[\"\']', content) or re.search(r'priority:\s*(.*?)(\n|$)', content)
        priority = priority_match.group(1).strip() if priority_match else 'medium'

        # Extract assignee
        assignee_match = re.search(r'assignee:\s*[\"\'](.*?)[\"\']', content) or re.search(r'assignee:\s*(.*?)(\n|$)', content)
        assignee = assignee_match.group(1).strip() if assignee_match else 'unassigned'

        # Extract created date
        created_match = re.search(r'created:\s*[\"\'](.*?)[\"\']', content) or re.search(r'created:\s*(.*?)(\n|$)', content)
        created = created_match.group(1).strip() if created_match else 'unknown'

        return {
            'path': file_path,
            'title': title,
            'status': status,
            'priority': priority,
            'assignee': assignee,
            'filename': os.path.basename(file_path),
            'created': created
        }
    except Exception as e:
        return {
            'path': file_path,
            'title': os.path.basename(file_path),
            'status': 'error',
            'priority': 'unknown',
            'assignee': 'unknown',
            'filename': os.path.basename(file_path),
            'error': str(e)
        }

def main():
    """Main function to scan for and output active work efforts."""
    # Get all markdown files in active directory
    active_files = []
    for ext in ['md', 'markdown']:
        active_files.extend(glob.glob(f'work_efforts/active/*.{ext}'))
        active_files.extend(glob.glob(f'_AI-Setup/work_efforts/active/*.{ext}'))

    # Track processed files to avoid duplicates
    processed_filenames = set()

    # Create a structured representation
    work_efforts = []
    for file_path in active_files:
        metadata = extract_metadata(file_path)
        filename = os.path.basename(file_path)

        # Skip if already processed or if status is completed
        if metadata and metadata['status'].lower() != 'completed' and filename not in processed_filenames:
            processed_filenames.add(filename)
            work_efforts.append(metadata)

    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
    work_efforts.sort(key=lambda x: priority_order.get(x['priority'].lower(), 5))

    # Output as JSON
    result = {
        'active_work_efforts': work_efforts,
        'count': len(work_efforts)
    }

    print(json.dumps(result, indent=2))

    # Also save to file
    with open('active_work_efforts.json', 'w') as f:
        json.dump(result, f, indent=2)

    return 0

if __name__ == "__main__":
    main()