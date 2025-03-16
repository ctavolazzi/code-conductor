---
title: "Multi-Work-Manager Implementation"
status: "active"
priority: "high"
assignee: "AI Assistant"
created: "2025-03-09 14:28"
last_updated: "2025-03-09 14:28"
due_date: "2025-03-15"
tags: ["enhancement", "usability", "configuration", "multi-manager"]
---

# Multi-Work-Manager Implementation

## 🚩 Objectives
- Create a system that allows multiple work effort managers within a single project
- Support creating work efforts in different subdirectories of a project
- Implement a central registry for all work effort managers
- Provide commands to add/manage work effort managers and set defaults
- Maintain backward compatibility with existing projects

## 🛠 Tasks
- [x] Design a configuration system that supports multiple work managers
- [x] Implement a central registry in config.json
- [x] Create a command to add new work effort managers: `new-work-manager`
- [x] Update work effort location discovery to use manager information
- [x] Add command-line options to specify which manager to use
- [x] Implement command to set the default manager: `set-default`
- [x] Create command to list all available managers: `list-managers`
- [x] Update help messages to document the new functionality
- [x] Create test script to validate multi-manager functionality

## 📝 Notes
- The configuration system now uses a central registry in `.AI-Setup/config.json` to track all work effort managers
- Multiple work managers can exist within a project in different directories
- Each manager has a name, path, and configuration settings
- The system can intelligently determine which manager to use based on current directory
- Users can explicitly specify a manager to use with the `--manager` flag
- A default manager can be set for the project

### Configuration Structure
The updated configuration system stores multiple work managers:

```json
{
  "version": "0.4.3",
  "project_root": "/path/to/project",
  "created_at": "2025-03-09 14:28:00",
  "updated_at": "2025-03-09 14:28:00",
  "default_work_manager": "main",
  "work_managers": [
    {
      "name": "main",
      "path": ".",
      "work_efforts_dir": ".AI-Setup/work_efforts",
      "use_manager": true,
      "manager_script": ".AI-Setup/work_efforts/scripts/work_effort_manager.py",
      "runner_script": ".AI-Setup/work_efforts/scripts/run_work_effort_manager.py",
      "auto_start": true
    },
    {
      "name": "frontend",
      "path": "frontend",
      "work_efforts_dir": "work_efforts",
      "use_manager": true,
      "manager_script": "work_efforts/scripts/work_effort_manager.py",
      "runner_script": "work_efforts/scripts/run_work_effort_manager.py",
      "auto_start": true
    }
  ],
  "default_settings": {
    "assignee": "AI Assistant",
    "priority": "medium",
    "due_date": "+7d"
  }
}
```

### New Commands
The implementation adds these new commands:

1. **new-work-manager**: Create a new work effort manager
   ```
   code-conductor new-work-manager --target-dir /path/to/dir --manager-name Name
   ```

2. **set-default**: Set the default work effort manager
   ```
   code-conductor set-default --manager-name ManagerName
   ```

3. **list-managers**: List all registered work effort managers
   ```
   code-conductor list-managers
   ```

### Manager Selection Logic
When creating or listing work efforts:

1. If `--manager` is specified, use that manager
2. If no manager is specified but in a subdirectory with a manager, use that
3. If no manager is specified and not in a manager subdirectory, use the default manager
4. If no default is set, use the first manager (usually the main one)

## 🐞 Issues Encountered
- Needed to ensure work efforts would be created in the correct location based on manager
- Had to add proper path resolution for relative paths in the configuration
- Needed to prevent name collisions when adding new managers
- Updating command-line flags to support manager selection

## ✅ Outcomes & Results
- Multiple work effort managers can be created throughout a project
- Work efforts can be created in specific directories with `--manager` flag
- Work efforts are intelligently routed to the most appropriate manager
- All managers are tracked in a central registry in the config.json
- Commands are available to manage and list all work effort managers
- Test scripts validate the multi-manager functionality

## 📌 Linked Items
- [Config System Implementation](../active/202503091416_config_system_implementation.md)
- [Test script for multi-manager system](../../test_multi_manager.sh)

## 📅 Timeline & Progress
- **Started**: 2025-03-09 14:28
- **Updated**: 2025-03-09 14:28
- **Target Completion**: 2025-03-15
- **Completed**: 2025-03-09 14:28