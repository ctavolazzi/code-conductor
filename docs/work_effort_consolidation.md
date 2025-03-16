# Work Effort Consolidation

This document explains how to use the `consolidate_work_efforts.py` script to consolidate work efforts from multiple directories into a centralized location with Obsidian-style document linking.

## Overview

The script automates the process of:

1. Finding all work effort directories in a project
2. Copying work effort files to the centralized `.AI-Setup/work_efforts` location
3. Preserving directory structure (active, archived, completed, etc.)
4. Optionally adding Obsidian-style links between related documents
5. Cleaning up original directories after confirmation
6. Updating documentation (changelog and devlog)

## Usage

```bash
python consolidate_work_efforts.py [options]
```

### Options

- `--root-dir PATH` - Root directory to search for work efforts (default: current directory)
- `--dest-dir PATH` - Destination directory for consolidated work efforts (default: .AI-Setup/work_efforts)
- `--dry-run` - Don't actually copy or delete files, just show what would be done
- `--no-delete` - Copy files but don't delete the original directories
- `--force` - Don't ask for confirmation before deleting original directories
- `--add-links` - Scan for related documents and add Obsidian-style links
- `--verbose` - Enable verbose logging
- `--help` - Show help message and exit

### Examples

Run a dry run to see what would happen:
```bash
python consolidate_work_efforts.py --dry-run
```

Consolidate work efforts and add Obsidian-style links between related documents:
```bash
python consolidate_work_efforts.py --add-links
```

Consolidate work efforts from a specific project:
```bash
python consolidate_work_efforts.py --root-dir /path/to/project
```

## Obsidian-Style Document Linking

The script supports two types of document linking:

1. **Frontmatter linking** - Adds a `related_efforts` field in the frontmatter metadata of each document, containing references to related documents
   ```yaml
   ---
   title: "Document Title"
   related_efforts: [[another_document.md]], [[third_document.md]]
   ---
   ```

2. **Wiki-style links** - Detects and preserves `[[document]]` links within the content of each document

The `--add-links` option will scan document content for mentions of other document titles and automatically add appropriate links.

## Safety Features

- The script will ask for confirmation before deleting original directories
- All operations are logged to `consolidate_work_efforts.log`
- The `--dry-run` option allows previewing what would happen without making changes
- Error handling prevents catastrophic failures

## Workflow Integration

This script is designed to be part of a larger workflow for managing work efforts:

1. Use it when migrating from an older work effort structure
2. Run it to consolidate scattered work efforts across a project
3. Integrate it with CI/CD to maintain centralized work efforts
4. Use it as a step in setting up Obsidian-style navigation between work efforts

## Troubleshooting

If you encounter issues:

1. Try running with `--verbose` to see detailed logging
2. Check the `consolidate_work_efforts.log` file for errors
3. Use `--dry-run` to diagnose what might be going wrong
4. Ensure you have write permissions to the destination directory