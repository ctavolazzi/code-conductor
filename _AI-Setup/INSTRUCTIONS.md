# AI Setup Instructions

This directory contains instructions and resources for AI assistants working with this codebase.

## Work Effort Management

### Familiarize First, Then Use Scripts

1. **First Interaction**: When first working with this codebase, familiarize yourself with the Code Conductor workflow process by reviewing:
   - The workflow steps in the workflow_runner.py script
   - The structure of work efforts in .AI-Setup/work_efforts/
   - The templates used in .AI-Setup/work_efforts/templates/

2. **Prioritize Existing Scripts**: After initial familiarity, ALWAYS prefer using existing scripts for work effort management:
   - Use `workflow_runner.py` for the complete workflow process
   - Use `update_status.py` for changing work effort status
   - Use `.AI-Setup/work_efforts/scripts/work_effort_manager.py` for specific work effort operations
   - Use `.AI-Setup/work_efforts/scripts/run_work_effort_manager.py` for interactive work effort management
   - Use `.AI-Setup/work_efforts/scripts/new_work_effort.py` for creating individual work efforts
   - Use `retrieve_work_effort.py` to gather comprehensive context for AI assistants

3. **Only Manual Creation When Necessary**: Only create work efforts manually if:
   - The existing scripts do not support the specific operation needed
   - There's a technical issue with the scripts that prevents their use
   - The user specifically requests manual creation

## Workflow Scripts Quick Reference

### Complete Workflow Process
```bash
./workflow_runner.py --feature-name "Feature Name" [--non-interactive]
```

### Work Effort Status Management
```bash
./update_status.py --work-effort path/to/work_effort.md --status completed
```

### Retrieving Work Effort Context
```bash
./retrieve_work_effort.py --name "feature-name"
./retrieve_work_effort.py --status active
./retrieve_work_effort.py --latest 3
./retrieve_work_effort.py --related "feature-name" --recursive
```

### Creating a New Work Effort
```bash
python .AI-Setup/work_efforts/scripts/new_work_effort.py --title "Feature Title" --description "Description" [--priority high]
```

## Documentation

When using scripts, always:
1. Update the devlog with appropriate entries
2. Ensure work efforts have complete metadata
3. Link related work efforts using Obsidian-style `[[links]]`
4. Update the main README.md and CHANGELOG.md for significant features

## Context Gathering Workflow

When beginning a new task:
1. Use `retrieve_work_effort.py` to gather context on related efforts
2. Check recent changes with `git diff` or `diff_history`
3. Review existing scripts in `.AI-Setup/work_efforts/scripts/`
4. THEN proceed with the workflow process using `workflow_runner.py`
