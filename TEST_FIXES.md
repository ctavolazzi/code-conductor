# Test Fixes Required

## API Parameter Mismatches

### 1. In test_05_error_handling.py - Corrupt Index Recovery, Concurrent Updates

Fix the code calling `WorkEffortManager` constructor with a `work_efforts_root` parameter. The constructor actually expects:

```python
def __init__(self,
           project_dir: str = None,
           config: Dict = None,
           config_json: str = None,
           config_file: str = None,
           auto_start: bool = False):
```

Change calls from:
```python
manager = WorkEffortManager(work_efforts_root=test_dir)
```

To:
```python
manager = WorkEffortManager(project_dir=test_dir)
```

### 2. In test_04_filtering_and_querying.py - Filter by Title/Content

The `filter_work_efforts` method does not support `content_contains` parameter. It only supports:

```python
def filter_work_efforts(self,
                      location: str = None,
                      status: str = None,
                      assignee: str = None,
                      priority: str = None,
                      title_contains: str = None,
                      created_after: str = None,
                      created_before: str = None,
                      due_after: str = None,
                      due_before: str = None,
                      tags: List[str] = None,
                      sort_by: str = None,
                      reverse: bool = False,
                      limit: int = None) -> List[Dict]:
```

Change calls from:
```python
filtered_efforts = manager.filter_work_efforts(content_contains=keyword)
```

To:
```python
filtered_efforts = manager.filter_work_efforts(title_contains=keyword)
```

## Validation Issues

### 1. Title validation in WorkEffortManager

The `_validate_title` method needs to be improved to reject invalid characters. Find the method around line 420 in `src/code_conductor/work_efforts/scripts/work_effort_manager.py` and ensure it properly rejects characters like '/'.

### 2. Priority validation in WorkEffortManager

Check how priorities are validated during work effort creation. The valid priorities should be enforced: "low", "medium", "high", "critical".

## Index Issues

### 1. Loading and Retrieving Work Efforts

The issue appears to be with loading work efforts from the index or filesystem. Check how the manager loads and retrieves work efforts:

1. Verify that the `_load_work_efforts` method (around line 213) correctly loads all work efforts
2. Check if `filter_work_efforts` method is correctly querying the loaded work efforts
3. Ensure that the work efforts index is being properly maintained

## Timestamp Update Issue

### 1. During Status Updates

The `update_work_effort_status` method should ensure that the `last_updated` field in the work effort metadata is updated with the current timestamp. Check the implementation around line 1112.