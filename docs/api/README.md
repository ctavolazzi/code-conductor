# API Documentation

This directory contains documentation for the Code Conductor API.

## Package Structure

The Code Conductor API is organized in a structured package layout:

```
src/code_conductor/
├── cli.py                 # Command-line interface
├── work_effort_manager.py # Work effort management
├── utils/                 # Utility functions
│   ├── validation.py      # Input validation
│   ├── path_helpers.py    # Path handling utilities
│   └── ...                # Other utility modules
├── creators/              # Creation functions
├── providers/             # Provider functionality
└── templates/             # Template files
```

## Core Modules

### WorkEffortManager

The `WorkEffortManager` class handles all operations related to work efforts:

```python
from src.code_conductor.work_effort_manager import WorkEffortManager

manager = WorkEffortManager()

# Create a work effort
manager.create_work_effort(title="Example Work Effort", description="This is an example.")

# List work efforts
work_efforts = manager.list_work_efforts()

# Update work effort status
manager.update_work_effort_status(work_effort_path, new_status="completed")
```

### CLI Module

The CLI module provides the command-line interface for Code Conductor:

```python
from src.code_conductor.cli import main

# Run directly from Python
main()
```

## Utility Functions

### Validation

The validation module provides functions for validating user inputs:

```python
from src.code_conductor.utils.validation import validate_title, validate_date

# Validate a title
valid_title = validate_title("Example Title")

# Validate a date
valid_date = validate_date("2025-03-16")
```

### Path Helpers

The path_helpers module provides utilities for working with file paths:

```python
from src.code_conductor.utils.path_helpers import get_project_root, find_work_efforts_dir

# Get the project root
project_root = get_project_root()

# Find the work efforts directory
work_efforts_dir = find_work_efforts_dir()
```

## Migration from Legacy API

If you're using the legacy API (pre-v0.4.x), see the [Migration Guide](../development/migration/MIGRATION_GUIDE_v0.4.x.md) for details on updating your code to use the new API structure.