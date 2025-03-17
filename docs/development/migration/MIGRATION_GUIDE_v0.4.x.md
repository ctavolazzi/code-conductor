# Migration Guide for Code Conductor v0.4.x

This guide is intended to help developers migrate their code and workflows to the new structure introduced in Code Conductor v0.4.x. The codebase has undergone significant streamlining and structural changes to establish a more maintainable and consistent foundation.

## 🔄 Overview of Changes

The following major changes have been implemented:

1. **Package Structure Standardization**
   - Moved from a flat directory structure to a proper package-based structure
   - Consolidated duplicate functionality into `src/code_conductor` package

2. **Import Path Standardization**
   - Updated all import paths to use the package structure
   - Added compatibility modules for backward compatibility

3. **Consolidated Duplicate Directories**
   - Merged duplicate directories (utils, creators, providers, templates)
   - Standardized utility function locations

4. **Improved Validation**
   - Enhanced error handling for edge cases
   - Added proper validation for titles, dates, and paths

5. **Work Effort Structure Changes**
   - Each work effort is now in its own directory
   - Standardized work effort naming and organization

## 📦 Package Structure Changes

### Old Structure (Pre-v0.4.x)
```
code_conductor/
├── utils/
├── creators/
├── providers/
├── templates/
├── various Python modules
└── tests/
```

### New Structure (v0.4.x)
```
code_conductor/
├── src/
│   └── code_conductor/
│       ├── utils/
│       ├── creators/
│       ├── providers/
│       ├── templates/
│       └── various Python modules
├── tests/
└── legacy compatibility modules (transitional)
```

## 🛠️ Migration Steps

### 1. Updating Import Paths

#### Before:
```python
from utils import helper_function
from creators import create_work_effort
```

#### After:
```python
from src.code_conductor.utils import helper_function
from src.code_conductor.creators import create_work_effort
```

### 2. Using WorkEffortManager

#### Before:
```python
from work_effort_manager import create_work_effort

create_work_effort("Title", "Description")
```

#### After:
```python
from src.code_conductor.work_effort_manager import WorkEffortManager

manager = WorkEffortManager()
manager.create_work_effort("Title", "Description")
```

### 3. Validation of Inputs

The system now has more robust validation. Be sure to handle these cases:

#### Before:
```python
def process_title(title):
    # No validation
    return title
```

#### After:
```python
from src.code_conductor.utils.validation import validate_title

def process_title(title):
    try:
        validated_title = validate_title(title)
        return validated_title
    except ValueError as e:
        # Handle validation error
        print(f"Invalid title: {e}")
        return None
```

### 4. Working with Work Efforts

#### Before:
Work efforts were often stored as loose files in the work_efforts directory.

#### After:
Each work effort is now in its own directory, following the naming pattern:
```
work_efforts/[status]/[timestamp]_[title]/[timestamp]_[title].md
```

To work with these files:
```python
from src.code_conductor.work_effort_manager import WorkEffortManager

manager = WorkEffortManager()
work_efforts = manager.list_work_efforts()
```

## 🚨 Common Issues and Solutions

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'utils'`

**Solution**: Update import to use the package path:
```python
from src.code_conductor.utils import module_name
```

### Path Resolution Errors

**Issue**: Files not found at expected paths

**Solution**: Use the package's path resolution utilities:
```python
from src.code_conductor.utils.path_helpers import get_project_root

project_root = get_project_root()
file_path = project_root / "relative" / "path" / "to" / "file"
```

### Edge Case Handling

**Issue**: Functions fail with unexpected input values

**Solution**: Use the new validation functions and add proper error handling:
```python
from src.code_conductor.utils.validation import validate_title, validate_date

try:
    valid_title = validate_title(title)
    valid_date = validate_date(date)
except ValueError as e:
    # Handle validation error
    print(f"Validation error: {e}")
```

## 📋 Transitional Support

For backward compatibility, some transitional modules have been added that re-export functionality from the new location. These will be removed in a future version, so it's recommended to update your code to use the new structure:

```python
# Transitional support (will be deprecated)
import utils  # Re-exports from src.code_conductor.utils

# Recommended approach
from src.code_conductor.utils import function_name
```

## 🔮 Future Changes

In future versions, we plan to:

1. Remove transitional compatibility modules
2. Further consolidate and standardize the API
3. Add more comprehensive documentation

For questions or issues with this migration, please file an issue on GitHub or contact the development team.