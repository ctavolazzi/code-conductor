# Retrieve Work Effort Script

The `retrieve_work_effort.py` script is designed to gather comprehensive context about work efforts for AI assistants and developers. It locates work efforts by various criteria and displays their content along with associated files and scripts.

## Features

- **Multiple Search Options**: Find work efforts by name, status, date, or recency
- **Related Work Effort Discovery**: Identify and display linked work efforts
- **Associated Script Display**: Show implementation scripts related to a work effort
- **Recursive Exploration**: Traverse related work efforts to build a complete context
- **Comprehensive Output**: Display all relevant information in a structured format

## Usage

### Basic Commands

```bash
# Find a work effort by name or part of name
./retrieve_work_effort.py --name "feature-name"

# Find work efforts by status
./retrieve_work_effort.py --status active
./retrieve_work_effort.py --status completed
./retrieve_work_effort.py --status archived

# Find work efforts by date (YYYYMMDD format)
./retrieve_work_effort.py --date 20250316

# Get the most recent work efforts (default: 5)
./retrieve_work_effort.py --latest
./retrieve_work_effort.py --latest 10

# Find work efforts related to a specific one
./retrieve_work_effort.py --related "feature-name"
```

### Additional Options

```bash
# Don't show associated scripts, only work effort content
./retrieve_work_effort.py --name "feature-name" --no-associated

# Recursively display related work efforts
./retrieve_work_effort.py --related "feature-name" --recursive
```

## AI Assistant Usage

This script is particularly useful for AI assistants working with the codebase as it provides comprehensive context:

1. **Starting a Task**: When beginning work, use `--latest` to see recent work efforts
   ```bash
   ./retrieve_work_effort.py --latest 3
   ```

2. **Working on an Existing Feature**: Use `--name` to find the specific work effort
   ```bash
   ./retrieve_work_effort.py --name "search-functionality"
   ```

3. **Understanding Related Features**: Use `--related` with `--recursive` to see the full context
   ```bash
   ./retrieve_work_effort.py --related "user-authentication" --recursive
   ```

4. **Checking Project Status**: Use `--status` to see all active work efforts
   ```bash
   ./retrieve_work_effort.py --status active
   ```

## Example Output

The script produces formatted output that includes:

1. **Work Effort Content**: The full content of the work effort markdown file, including frontmatter
2. **Associated Scripts**: The content of any implementation scripts related to the work effort
3. **Related Work Efforts**: When using the `--recursive` flag, related work efforts are also displayed

Example output structure:

```
================================================================================
WORK EFFORT: 202503160751_enhanced_workflow_runner.md
================================================================================

---
title: "Enhanced Workflow Runner"
status: "completed"
priority: "high"
assignee: "Development Team"
created: "2025-03-16 07:51:00"
last_updated: "2025-03-16 14:30:00"
due_date: "2025-03-23"
tags: [workflow, automation, template]
---

# Enhanced Workflow Runner

... (content of the work effort) ...

================================================================================
ASSOCIATED SCRIPTS:
================================================================================

--- enhanced_workflow_runner.py ---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Workflow Runner
... (content of the script) ...
```

## Integration with Workflow

The retrieve_work_effort.py script is designed to be used as part of the Code Conductor workflow:

1. **Before Creating a Work Effort**: Use it to gather context on related efforts
2. **During Implementation**: Use it to review the requirements and details
3. **For AI Assistance**: Use it to provide comprehensive context to AI assistants

## Technical Details

- The script searches for work efforts in `.AI-Setup/work_efforts/active/`, `.AI-Setup/work_efforts/completed/`, and `.AI-Setup/work_efforts/archived/` directories
- Associated scripts are searched for in `.AI-Setup/work_efforts/scripts/` and the project root
- Relationships between work efforts are determined by:
  - Frontmatter `related_efforts` field
  - Obsidian-style links (`[[link]]`) in the content
- The script handles both timestamp-prefixed filenames (e.g., `202503160751_feature.md`) and regular filenames