# WorkEfforts Modular Architecture

## Overview

The WorkEfforts system has been refactored from a monolithic design to a modular architecture. This document provides a comprehensive guide to the new structure, explaining the purpose of each module, how they interact, and how to extend the system.

## Design Philosophy

The refactoring was guided by these principles:

- **Single Responsibility Principle**: Each module has a clear, focused purpose
- **Separation of Concerns**: Functionality is separated into logical domains
- **Dependency Management**: Minimizing coupling between modules
- **Testability**: Each component can be tested independently
- **Extensibility**: New features can be added without modifying existing code

## Directory Structure

```
work_efforts/
├── core/           # Core functionality and coordination
├── models/         # Data structures and transformations
├── filesystem/     # File I/O operations
├── events/         # Event handling system
├── utils/          # Utility functions and helpers
├── scripts/        # Command-line tools
└── templates/      # Template files
```

## Module Descriptions

### 1. Core Module (`work_efforts/core/`)

The core module serves as the central coordination point for the WorkEfforts system.

#### `manager.py`

The `WorkEffortManager` class is the main entry point for working with work efforts. It:

- Coordinates between other modules
- Maintains state of work efforts
- Provides a façade for common operations
- Manages event distribution

```python
# Example usage
from work_efforts.core.manager import WorkEffortManager

# Create a manager
manager = WorkEffortManager(project_dir="/path/to/project")

# Create a work effort
manager.create_work_effort(
    title="Example Task",
    assignee="developer",
    priority="high",
    due_date="2025-04-01"
)

# Get all active work efforts
active_efforts = manager.get_work_efforts("active")
```

### 2. Models Module (`work_efforts/models/`)

The models module contains data structures and transformation logic.

#### `work_effort.py`

Defines the `WorkEffort` class and related functionality:

- Data structure representing a work effort
- Methods for converting between formats (Markdown, JSON)
- Status and priority enumerations
- Filename generation logic

```python
# Example usage
from work_efforts.models.work_effort import WorkEffort, WorkEffortStatus

# Create a work effort
work_effort = WorkEffort(
    title="Example Task",
    assignee="developer",
    priority="high",
    due_date="2025-04-01"
)

# Convert to markdown
markdown = work_effort.to_markdown()

# Update the status
work_effort.update_status(WorkEffortStatus.COMPLETED)
```

### 3. Filesystem Module (`work_efforts/filesystem/`)

The filesystem module handles all file I/O operations.

#### `operations.py`

Provides functions for:

- Creating directory structures
- Reading/writing work effort files
- Moving work efforts between directories
- Loading work effort metadata
- Managing templates

```python
# Example usage
from work_efforts.filesystem.operations import (
    ensure_directory_structure,
    save_work_effort,
    load_work_efforts
)

# Create directories
paths = ensure_directory_structure("/path/to/project")

# Load all work efforts
work_efforts = load_work_efforts("/path/to/project")
```

### 4. Events Module (`work_efforts/events/`)

The events module implements an event system for tracking changes and triggering actions.

#### `event_system.py`

Contains:

- `EventEmitter` class for managing events
- Event handling mechanisms
- Event loop management
- Event data structures

```python
# Example usage
from work_efforts.events.event_system import EventEmitter, Event

# Create an emitter
emitter = EventEmitter()

# Register a handler
def on_work_effort_created(event):
    print(f"Work effort created: {event.data['title']}")

emitter.register_handler("work_effort_created", on_work_effort_created)

# Emit an event
emitter.emit_event("work_effort_created", {"title": "Example Task"})
```

### 5. Utils Module (`work_efforts/utils/`)

The utils module provides helper functions and utilities.

#### `config.py`

Provides configuration-related utilities:

- Loading/saving configuration
- JSON parsing/writing
- Default configuration management
- Configuration path resolution

```python
# Example usage
from work_efforts.utils.config import load_config, save_config, get_config

# Load configuration
config = load_config("/path/to/project")

# Get a specific setting
check_interval = get_config("/path/to/project", "check_interval", default=1.0)

# Update configuration
config["check_interval"] = 2.0
save_config(config, "/path/to/project")
```

## Module Interactions

The modules interact in the following ways:

1. **Core Manager → Models**: The manager creates and manipulates `WorkEffort` objects
2. **Core Manager → Filesystem**: The manager uses filesystem operations to read/write work efforts
3. **Core Manager → Events**: The manager emits events when work efforts change
4. **Core Manager → Utils**: The manager uses utilities for configuration management
5. **Filesystem → Models**: Filesystem operations create `WorkEffort` objects from file content
6. **Models ↔ Utils**: Models use utilities for JSON parsing and data handling

## Common Workflows

### Creating a Work Effort

1. `WorkEffortManager.create_work_effort()` is called
2. A `WorkEffort` object is created with the provided data
3. `save_work_effort()` writes the work effort to disk
4. The manager emits a "work_effort_created" event
5. The work effort is added to the manager's internal state

### Updating Work Effort Status

1. `WorkEffortManager.update_work_effort_status()` is called
2. The work effort is loaded from disk
3. The status is updated in the work effort object
4. `move_work_effort()` moves the file to the appropriate directory
5. The manager emits a "work_effort_status_changed" event
6. The work effort's status is updated in the manager's internal state

## Extension Guidelines

### Adding a New Feature

To add a new feature:

1. Identify which module is most appropriate for the feature
2. Implement the feature in that module
3. If the feature spans multiple modules:
   - Implement the core logic in the most appropriate module
   - Add an interface method to the manager to coordinate the operation
   - Use events to notify interested components

### Creating a New Module

To create a new module:

1. Create a new directory in the `work_efforts/` package
2. Add an `__init__.py` file with version information
3. Implement the module's functionality in appropriately named files
4. Update the manager to use the new module if necessary
5. Add tests for the new module

## Testing

Each module has its own test file in the `tests/` directory:

- `tests/test_modular_implementation.py`: Tests for all modules
- `tests/test_workflow_and_performance.py`: Tests for workflows and performance
- `tests/test_modular_architecture.py`: Tests for the architecture design

To run the tests:

```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests/test_modular_implementation.py

# Run all tests with the test runner
python tests/run_tests.py
```

## Command-Line Interface

The command-line interface is implemented in `work_efforts/scripts/`.

### cc-work-e

The `cc-work-e` command creates work efforts:

```bash
# Create a work effort in the current directory
cc-work-e --title "Example Task" --assignee "developer" --priority "high" --due-date "2025-04-01"

# Create a work effort in the package directory
cc-work-e --title "Example Task" --package-dir

# Create a work effort interactively
cc-work-e -i
```

## Conclusion

The modular architecture provides a solid foundation for managing work efforts. By separating concerns into focused modules, the system is more maintainable, testable, and extensible. Developers can understand and modify individual components without having to understand the entire system.