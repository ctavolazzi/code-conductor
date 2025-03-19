# Migration Guide to v0.5.x

## Major Changes

### WorkEffortManager Consolidation

The `WorkEffortManager` implementation has been consolidated into a single core module. This change improves code maintainability and reduces duplication.

#### New Location
The `WorkEffortManager` is now located at:
```python
from code_conductor.core.work_effort.manager import WorkEffortManager
```

#### Changes Required
1. Update imports in your code:
   ```python
   # Old imports (no longer valid)
   from src.code_conductor.work_efforts.scripts.work_effort_manager import WorkEffortManager
   from work_efforts.scripts.work_effort_manager import WorkEffortManager
   from src.code_conductor.work_effort_manager import WorkEffortManager

   # New import
   from code_conductor.core.work_effort.manager import WorkEffortManager
   ```

2. The core implementation now includes:
   - Improved error handling
   - Better support for concurrent operations
   - Enhanced validation of inputs
   - Consistent file locking mechanism

### Additional Changes

- The package's `__init__.py` now exposes `WorkEffortManager`, `EventEmitter`, and `Event`
- Version updated to 0.5.0
- Improved test coverage for edge cases and internationalization

## Backward Compatibility

The new implementation maintains backward compatibility with existing work efforts and configurations. No changes to your existing work efforts or their structure are required.

## New Features

1. Enhanced error handling for:
   - Invalid input data
   - File system edge cases
   - Concurrent operations
   - Special characters in titles

2. Improved support for:
   - Unicode characters in titles and content
   - Extremely long titles
   - Invalid date formats
   - Missing directories

## Upgrading

1. Update your code to use the new import path
2. Test your existing work efforts to ensure they continue to work as expected
3. Take advantage of the new features and improvements

For any issues during migration, please refer to the test files in the `tests/` directory for examples of proper usage.