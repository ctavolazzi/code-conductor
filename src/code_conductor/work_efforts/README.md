# Work Efforts Module

This directory contains code for managing work efforts in the Code Conductor system.

## Counter System

The `counter.py` module provides a durable, persistent counter system for work effort numbering that:

1. Maintains a single source of truth for work effort numbering
2. Survives system shutdowns and crashes
3. Handles sequential numbering with proper padding
4. Gracefully transitions from 4-digit numbers (0001-9999) to 5+ digits (10000+)
5. Can initialize from existing work efforts in the filesystem
6. Optionally supports date-prefixed numbering format

### Usage in Code

```python
from code_conductor.work_efforts.counter import get_counter, format_work_effort_filename

# Get a counter instance
counter = get_counter()

# Get the next count
count = counter.get_next_count()

# Format a filename with the count
filename = format_work_effort_filename("My Work Effort", count)
# Result: "0001_my_work_effort.md"

# With date prefix
filename = format_work_effort_filename("My Work Effort", count, use_date_prefix=True)
# Result: "202303170001_my_work_effort.md"
```

### Creating Work Efforts with Sequential Numbering

When creating work efforts using the `WorkEffortManager`, you can control the numbering format:

```python
from code_conductor.manager import WorkEffortManager

manager = WorkEffortManager()

# Create with sequential numbering (default)
path = manager.create_work_effort("My Work Effort")

# Create with timestamp-based naming instead
path = manager.create_work_effort(
    "My Work Effort",
    use_sequential_numbering=False
)

# Create with date-prefixed sequential numbering
path = manager.create_work_effort(
    "My Work Effort",
    use_sequential_numbering=True,
    use_date_prefix=True
)
```