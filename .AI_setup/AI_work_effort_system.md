# AI Work Effort System - Johnny Decimal

This file describes the Johnny Decimal work effort system used in this project.
It helps AI assistants understand how to manage and track work efforts using categories and status.

## Work Effort Structure

Each work effort is a markdown file that contains structured information about a task, feature, bug fix, or any other unit of work. Work efforts are organized by **category** (Johnny Decimal) and managed by **status** (in frontmatter).

### Document Format

```markdown
---
title: "Title of the Work Effort"
status: "active" # options: active, paused, completed, cancelled
priority: "medium" # options: low, medium, high, critical
assignee: "username"
created: "YYYY-MM-DD HH:mm" # Creation date and time
last_updated: "YYYY-MM-DD HH:mm" # Last update date and time
due_date: "YYYY-MM-DD" # Expected completion date
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# Title of the Work Effort

## 🚩 Objectives
- Clearly define goals for this work effort

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references

## 🐞 Issues Encountered
- Document issues and obstacles clearly

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD
- **Target Completion**: YYYY-MM-DD
```

## Johnny Decimal Categories

Work efforts are organized into the following categories:

- **00_system** - System and infrastructure work
- **10_development** - Feature development and code improvements
- **20_debugging** - Bug fixes and troubleshooting
- **30_documentation** - Documentation and guides
- **40_testing** - Testing and validation
- **50_maintenance** - Maintenance and updates

## Status Management

Status is managed within each document's frontmatter:
- **active** - Currently being worked on
- **paused** - Temporarily on hold
- **completed** - Finished successfully
- **cancelled** - Abandoned or no longer needed

## Commands

### Creating Work Efforts
```bash
# Interactive mode with category selection
cc-ai work_effort -i
cc-ai wei  # shorthand

# Non-interactive mode (defaults to 10_development)
cc-ai work_effort --title "Feature Name" --priority high
cc-ai we --title "Bug Fix" --priority critical  # shorthand
```

### Listing Work Efforts
```bash
# List all work efforts organized by status
cc-ai list
cc-ai l  # shorthand
```

### Setup
```bash
# Set up Johnny Decimal structure in current directory
cc-ai setup
cc-ai s  # shorthand
```

## Directory Structure

```
work_efforts/
├── 00.00_work_efforts_index.md    # Main index
├── 00_system/
│   ├── 00.00_index.md            # Category index
│   └── YYYYMMDDHHMM_work_effort.md
├── 10_development/
│   ├── 00.00_index.md
│   └── YYYYMMDDHHMM_work_effort.md
├── 20_debugging/
│   ├── 00.00_index.md
│   └── YYYYMMDDHHMM_work_effort.md
├── 30_documentation/
│   ├── 00.00_index.md
│   └── YYYYMMDDHHMM_work_effort.md
├── 40_testing/
│   ├── 00.00_index.md
│   └── YYYYMMDDHHMM_work_effort.md
├── 50_maintenance/
│   ├── 00.00_index.md
│   └── YYYYMMDDHHMM_work_effort.md
├── templates/
│   └── work-effort-template.md
├── archived/                     # Permanently archived work
└── scripts/                     # Helper scripts
```

## Benefits

1. **Clear Organization**: Work efforts are categorized by type, not just status
2. **Flexible Status**: Status can be changed by editing frontmatter
3. **Better Navigation**: Johnny Decimal numbering provides logical structure
4. **Obsidian Compatible**: Works seamlessly with Obsidian markdown linking
5. **AI-Friendly**: Clear structure for AI assistants to understand and manage

## Best Practices

1. Choose the appropriate category when creating work efforts
2. Update status regularly in the frontmatter
3. Use descriptive titles and clear objectives
4. Link related work efforts using Obsidian-style links
5. Document outcomes and lessons learned
6. Archive completed work efforts when appropriate

## Integration with AI Assistants

The Johnny Decimal Work Effort system is designed to work seamlessly with AI assistants:

1. AI assistants can read and understand the category structure
2. They can parse frontmatter status to organize work efforts
3. They can suggest appropriate categories for new work efforts
4. They can help prioritize and organize tasks within categories
5. They can provide insights based on documented issues and outcomes