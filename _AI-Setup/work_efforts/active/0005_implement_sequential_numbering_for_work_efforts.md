---
title: Implement Sequential Numbering for Work Efforts
assignee:
priority: medium
status: active
due_date:
created_at: 2023-03-17 14:05
---

# Implement Sequential Numbering for Work Efforts

## Overview

This feature adds a sequential numbering system to work efforts for better organization and tracking. Work efforts now use a consistent numbering scheme that starts at 0001 and increments with each new work effort, making them easier to sort and reference.

## Implementation Details

- Created a durable counter system in `counter.py`
- Integrated counter with `WorkEffortManager.create_work_effort()`
- Added support for sequential numbering with proper padding (0001, 0002, etc.)
- Implemented graceful transition from 4 to 5+ digits (9999 → 10000)
- Added optional date-prefixed format (e.g., 202303170001)
- Created system to initialize counter from existing work efforts

## Key Features

1. **Persistent Counting** - The counter system maintains state between sessions and survives system shutdowns
2. **Smart Padding** - Uses 4 digits by default (0001) but transitions to more digits when needed (10000)
3. **Date Prefixing** - Optional YYYYMMDD prefix for time-sensitive tracking
4. **Backwards Compatible** - Works with existing work efforts by analyzing their current numbering
5. **File Safe** - Handles all file naming sanitization automatically

## Usage

```python
# In Python code:
from code_conductor.manager import WorkEffortManager

manager = WorkEffortManager()

# Create with sequential numbering (default)
path = manager.create_work_effort("My Work Effort")

# Create with date-prefixed sequential numbering
path = manager.create_work_effort(
    "My Work Effort",
    use_sequential_numbering=True,
    use_date_prefix=True
)

# Use traditional timestamp-based naming instead
path = manager.create_work_effort(
    "My Work Effort",
    use_sequential_numbering=False
)
```

```bash
# Using command-line interface:
# Create work effort with sequential numbering (default)
code-conductor work

# Create work effort with date-prefixed numbering
code-conductor work --date-prefix

# Use timestamp-based naming instead
code-conductor work --no-sequential-numbering
```

## Files Modified

- `src/code_conductor/manager.py` - Added sequential numbering support to work effort creation
- `src/code_conductor/work_efforts/counter.py` - Implemented durable counter system
- `src/code_conductor/work_efforts/README.md` - Added counter system documentation
- `README.md` - Updated feature list and usage examples

## Testing

The counter system has been tested for:
- Sequential number generation and persistence
- Proper handling of transitions from 4 to 5+ digits
- Recovery from corrupt counter files
- Thread-safety for multi-threaded access
- Proper initialization from existing work efforts

## Future Improvements

- Add ability to reset counter sequence
- Support for custom numbering schemes
- Support for branch-specific counters in Git workflows