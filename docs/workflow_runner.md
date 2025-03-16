# Workflow Runner

## Overview

The Workflow Runner is a powerful tool that automates the complete Code Conductor workflow process. It guides users through a standardized development workflow, ensuring consistent documentation, proper implementation, and comprehensive testing for every feature.

## Features

- **Guided Workflow Process**: Step-by-step guidance through the entire development workflow
- **Template Integration**: Uses official project templates for consistent documentation
- **Status Management**: Move work efforts between active, completed, and archived states
- **Documentation Validation**: Ensures all required documentation is created and updated
- **Script Generation**: Creates well-structured, executable Python scripts with tests
- **Interactive & Non-Interactive Modes**: Supports both guided interactive usage and automated execution

## Workflow Steps

The Workflow Runner guides you through 8 standardized steps:

1. **Create Work Effort Document**: Generate a properly structured work effort document
2. **Add Context & Requirements**: Document goals, requirements, and acceptance criteria
3. **Create Script or Code**: Generate executable script files with proper structure
4. **Execute & Test**: Run the script and document results
5. **Document Results**: Record testing outcomes and observations
6. **Refine Until Successful**: Iteratively improve the implementation
7. **Add Tests**: Create comprehensive test files with unittest framework
8. **Update All Documentation**: Ensure all documentation is complete and up-to-date

## Usage

### Basic Usage

```bash
# Run in interactive mode (default)
./workflow_runner.py

# Run in non-interactive mode with a specific feature name
./workflow_runner.py --feature-name "Enhanced Search Functionality" --non-interactive
```

### Interactive Mode

In interactive mode, the Workflow Runner prompts you for:

- Feature name and title
- Feature description
- Priority level
- Tags
- Testing results and observations
- Documentation status

### Non-Interactive Mode

Non-interactive mode is useful for automated processes or quick feature creation:

```bash
./workflow_runner.py --feature-name "Data Import Module" --non-interactive
```

This creates all necessary files with default values derived from the feature name.

## Status Management

The Workflow Runner includes functionality to manage the lifecycle of work efforts:

```python
# Example of changing status programmatically
runner = WorkflowRunner()
runner.work_effort_path = ".AI-Setup/work_efforts/active/my_feature.md"
runner.update_work_effort_status("completed")  # Moves to completed directory
```

Status changes automatically move work effort files to the appropriate directories:
- `active`: For in-progress work efforts
- `completed`: For finished work efforts
- `archived`: For deprecated or historical work efforts

## Directory Structure

The Workflow Runner uses the following directory structure:

```
.AI-Setup/
  └── work_efforts/
      ├── active/          # Active work efforts
      ├── completed/       # Completed work efforts
      ├── archived/        # Archived work efforts
      ├── scripts/         # Generated script files
      ├── templates/       # Document templates
      └── devlog.md        # Development log
```

## Template Integration

The Workflow Runner uses the official template file located at `.AI-Setup/work_efforts/templates/work-effort-template.md`, ensuring consistent formatting across all work efforts. If this template doesn't exist, the runner creates a default template with all required fields.

## Testing

The Workflow Runner creates and executes both implementation scripts and test scripts, using Python's unittest framework for test structure. Tests are created with appropriate class names and basic assertions that can be expanded for comprehensive testing.

## Best Practices

- **Start Early**: Create a work effort at the beginning of feature development
- **Document As You Go**: Fill in each section of the work effort as you progress
- **Review Tests**: Check and enhance the generated test files
- **Complete the Workflow**: Always finish all 8 steps for every feature
- **Update Status**: Move work efforts to the appropriate status when complete

## Example

Here's an example of a work effort, script, and test created by the Workflow Runner:

### Example Work Effort Document

```markdown
---
title: "Enhanced Search Functionality"
status: "active"
priority: "high"
assignee: "Developer Name"
created: "2025-03-16 08:15:00"
last_updated: "2025-03-16 08:15:00"
due_date: "2025-03-23"
tags: [feature, search, performance]
---

# Enhanced Search Functionality

## 🚩 Objectives
- Improve search speed for large datasets
- Add advanced filtering options
- Implement result highlighting

## 🛠 Tasks
- [ ] Optimize search algorithm
- [ ] Add filter interface
- [ ] Implement highlighting system

...
```

### Example Script

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Search Functionality

Implementation of enhanced search capabilities with improved performance

Usage:
    python enhanced_search_functionality.py [options]

Options:
    --help    Show this help message
"""

import os
import sys
import argparse


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Implementation of enhanced search capabilities")
    # Add your arguments here
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    print("Implementing Enhanced Search Functionality...")
    return 0


if __name__ == "__main__":
    sys.exit(main())