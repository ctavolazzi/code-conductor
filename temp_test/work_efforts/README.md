# Work Efforts - Johnny Decimal System

This directory contains structured documentation for tracking tasks, features, and bug fixes using the Johnny Decimal methodology.

## Johnny Decimal Structure

### Major Categories
- **00_system** - System and infrastructure work
- **10_development** - Feature development and code improvements
- **20_debugging** - Debugging and troubleshooting
- **30_documentation** - Documentation and guides
- **40_testing** - Testing and validation
- **50_maintenance** - Maintenance and updates

### Navigation
Start with the main index: `00.00_work_efforts_index.md`

Each category has its own index file (e.g., `00_system/00.00_index.md`)

## Status Management
Work effort status is managed within each document's frontmatter:
- **status: "active"** - Currently being worked on
- **status: "paused"** - Temporarily on hold
- **status: "completed"** - Finished successfully
- **status: "cancelled"** - Abandoned or no longer needed

## Essential Directories
- **templates/** - Templates for work effort documents
- **archived/** - Deprecated or abandoned work efforts (for permanent archive)
- **scripts/** - Helper scripts for managing work efforts

## Usage

Create a new work effort:
```
cc-ai work_effort --title "Feature Name" --priority high
```

Or use the interactive mode:
```
cc-ai work_effort -i
```

List all work efforts:
```
cc-ai list
```
