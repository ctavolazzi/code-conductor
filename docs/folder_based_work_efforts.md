# Folder-Based Work Efforts in Code Conductor

## Overview

Starting with version 0.4.5, Code Conductor implements a **folder-based work effort system** that improves organization and makes it easier to manage files related to specific work efforts. This document explains the new system and provides guidance on taking advantage of it.

## Key Features

- Each work effort now gets its own dedicated folder
- The main markdown file is stored inside the folder
- Additional files can be stored alongside the work effort markdown file
- All existing commands continue to work with this new structure
- Backward compatibility is maintained for older work efforts

## Benefits

### Better Organization

The folder-based approach allows you to keep all files related to a specific work effort together in one place:

```
.AI-Setup/work_efforts/active/
  └── 202503092130_project_name/
      ├── 202503092130_project_name.md   # Main work effort file
      ├── notes.txt                      # Additional notes
      ├── research.md                    # Research findings
      └── resources/                     # Sub-folders are supported
          └── data.json
```

### Improved Workflow

This structure facilitates better workflows:

- Keep design documents with implementation plans
- Store research findings alongside task tracking
- Include related code snippets or examples
- Maintain resources like data files or images

### Future Expandability

The folder-based approach allows for future enhancements:
- Additional metadata files
- Integration with other tools
- Dependency tracking between work efforts
- Enhanced reporting capabilities

## Using Folder-Based Work Efforts

### Creating New Work Efforts

All existing commands for creating work efforts now automatically use folders:

```bash
# Create a new work effort (creates a folder with the markdown file inside)
code-conductor work --title "My New Project"

# Shorthand command also creates a folder
cc-work-e --title "Quick Task"
```

### Adding Files to Work Efforts

You can add files to a work effort folder using your regular file system tools:

```bash
# Example: Add a notes file to a work effort
cd .AI-Setup/work_efforts/active/202503092130_my_new_project/
touch notes.txt
```

Or programmatically:

```python
import os

# Get the work effort folder path (dirname of the markdown file path)
work_effort_path = "/path/to/work_effort.md"
folder_path = os.path.dirname(work_effort_path)

# Add a file to the work effort folder
notes_path = os.path.join(folder_path, "notes.txt")
with open(notes_path, "w") as f:
    f.write("These are my notes for this work effort.")
```

### Migrating Existing Work Efforts

A conversion script is provided to migrate existing work efforts to the folder-based structure:

```bash
# Run in dry-run mode first to see what would happen
python convert_to_folders.py --dry-run

# Then run the actual conversion
python convert_to_folders.py
```

## Technical Details

### File Naming

The folder name follows the same pattern as the markdown file:
- Timestamp prefix (YYYYMMDDHHMM)
- Underscore separator
- Lowercase title with spaces replaced by underscores

Example:
```
202503092130_my_new_project/
└── 202503092130_my_new_project.md
```

### Special Character Handling

The folder-based system handles:
- Special characters (@, $, &, !, ?)
- Unicode characters (emoji, international scripts)
- Long titles (automatically sanitized)

### Implementation Notes

- The primary implementation is in `work_efforts/scripts/work_effort_manager.py`
- A centralized approach ensures consistent behavior across all entry points
- Backward compatibility is maintained with existing file-based work efforts
- Conversion utilities help transition to the folder-based structure

## Troubleshooting

### Work Efforts Not Creating Folders

If your work efforts aren't creating folders, make sure:
1. You have the latest version of Code Conductor (0.4.5+)
2. Run `pip install -e .` in the code_conductor directory
3. If issues persist, run the converter: `python convert_to_folders.py`

### Permission Issues

If you encounter permission issues:
- Ensure you have write permissions for the target directory
- Check that no files are locked by other processes
- Try running the command with appropriate permissions