# Improved Sequential Work Effort Numbering

This module provides an improved counter system for work effort naming that supports sequential numbering and handles numbers exceeding 9999.

## Features

- **Sequential Numbering**: Automatically maintains sequential numbers for work efforts (0001, 0002, etc.)
- **Number Overflow Handling**: Gracefully transitions from 4-digit numbers (9999) to 5+ digits (10000+)
- **Dual Naming Support**:
  - Standard sequential numbering: `0042_example_name.md`
  - Date-prefixed numbering: `20250317042_example_name.md`
- **Persistent Counter**: Maintains counter state across system reboots
- **Integrity Protection**: Includes checksums and auto-repair capabilities
- **Thread/Process Safety**: Uses file locking to prevent conflicts

## Implementation Details

### Sequential Numbering

The system uses a persistent counter to assign sequential numbers to work efforts. Numbers from 1 to 9999 are formatted as 4-digit numbers with leading zeros (e.g., "0001", "0042", "9999").

### Handling Numbers Beyond 9999

When the counter exceeds 9999, the system transitions to a variable-length format without leading zeros:
- 10000, 10001, 10002, ...
- 12345, 23456, 100000, ...

This approach allows for a seamless transition without disrupting the ordering of work efforts.

### Regex Pattern Changes

To support both 4-digit numbers and larger numbers, the regex pattern used to identify work efforts was updated from:

```python
# Old pattern (only matched 4-digit numbers)
pattern = r"^(\d{4})_"
```

to:

```python
# New pattern (matches any number at start)
pattern = r"^(\d+)_"
```

### Filename Formatting

Work effort filenames can be formatted in two ways:

1. **Standard Sequential**: `{formatted_number}_{title}.md`
   - Examples: `0001_example.md`, `9999_test.md`, `10000_beyond_limit.md`

2. **Date-Prefixed**: `{date}{formatted_number}_{title}.md`
   - Examples: `202503170001_example.md`, `202503179999_test.md`

## Usage

### Basic Usage

```python
from improved_counter import get_counter, format_work_effort_filename

# Get the next sequential number
counter = get_counter()
next_number = counter.get_next_count()  # e.g., 42

# Format a work effort filename (standard sequential)
filename = format_work_effort_filename("My Work Effort", next_number)
# Result: "0042_my_work_effort"

# Format with date prefix
date_filename = format_work_effort_filename("My Work Effort", next_number, use_date_prefix=True)
# Result: "202503170042_my_work_effort"
```

### Creating Work Efforts

```bash
# Create standard sequential work efforts
python create_demo_work_efforts.py --work-dir ./work_efforts

# Create date-prefixed work efforts
python create_demo_work_efforts.py --work-dir ./work_efforts --use-date-prefix

# Demonstrate large number handling
python create_demo_work_efforts.py --work-dir ./work_efforts --demo-large-numbers
```

### Testing

The implementation includes comprehensive tests:

```bash
# Test counter functionality
python test_large_counter_numbers.py
```

## Benefits

1. **Maintainability**: Consistent naming system makes it easier to manage work efforts
2. **Scalability**: Works well for projects with any number of work efforts
3. **Reliability**: Counter is persistent, thread-safe, and includes integrity verification
4. **Flexibility**: Supports both sequential and date-based naming as needed

## Recommendations

- For new projects, start with sequential numbering
- For very large projects, consider using date-prefixed numbering
- If your project is anticipated to have more than 9999 work efforts, the system will handle it automatically