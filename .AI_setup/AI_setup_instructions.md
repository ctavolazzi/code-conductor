# AI_setup Instructions

This file contains detailed instructions for setting up AI assistance in this project.
It helps AI assistants understand the structure and purpose of the project.

## Project Structure

This project follows the Johnny Decimal Work Effort methodology:

1. `work_efforts/` - Main work efforts directory with Johnny Decimal categories
2. `.AI_setup/` - AI assistant setup files
3. `templates/` - Work effort templates
4. `archived/` - Permanently archived work efforts
5. `scripts/` - Helper scripts for managing work efforts

## Setting Up AI Assistance

To set up AI assistance in a project:

1. Install the Code Conductor package:
```bash
pip install -e .
```

2. Run the setup command in your project directory:
```bash
cc-ai setup  # or cc-ai s
```

3. This will create the necessary files and directories:
   - `.AI_setup/` directory with configuration files
   - `work_efforts/` directory with Johnny Decimal structure

## Using AI Assistance

Once set up, AI assistants can:

1. Better understand your project structure through the Johnny Decimal system
2. Provide more contextual recommendations based on work effort categories
3. Help manage and track work efforts organized by status
4. Offer insights based on project patterns and documented outcomes

## Work Efforts

Work efforts are structured documents for tracking tasks organized by category and status.

### Creating Work Efforts

Interactive mode (recommended):
```bash
cc-ai work_effort -i  # or cc-ai wei
```

Non-interactive mode:
```bash
cc-ai work_effort --title "Feature Name" --priority high  # or cc-ai we
```

### Listing Work Efforts

```bash
cc-ai list  # or cc-ai l
```

This shows work efforts organized by status (active, paused, completed, cancelled).

## Johnny Decimal Categories

Work efforts are organized into these categories:

- **00_system** - System and infrastructure work
- **10_development** - Feature development and code improvements
- **20_debugging** - Bug fixes and troubleshooting
- **30_documentation** - Documentation and guides
- **40_testing** - Testing and validation
- **50_maintenance** - Maintenance and updates

## Commands

The Code Conductor package provides these commands:

1. `cc-ai setup` (or `cc-ai s`) - Set up AI assistance in the current directory
2. `cc-ai work_effort` (or `cc-ai we`) - Create a new work effort
3. `cc-ai work_effort -i` (or `cc-ai wei`) - Create a work effort interactively
4. `cc-ai list` (or `cc-ai l`) - List all work efforts organized by status
5. `cc-ai help` - Show help information
6. `cc-ai version` - Show version number

## Configuration

AI assistance is configured through the files in the `.AI_setup/` directory:

- `INSTRUCTIONS.md` - Basic command usage
- `AI_setup_validation_instructions.md` - Validation procedures
- `AI_work_effort_system.md` - Detailed system documentation
- `AI_setup_instructions.md` - This file

## Best Practices

1. Keep work efforts updated with current status in frontmatter
2. Use descriptive titles for work efforts
3. Choose appropriate categories when creating work efforts
4. Document issues and blockers in the work effort files
5. Update the status of work efforts regularly (active → completed)
6. Archive work efforts that are no longer relevant
7. Use AI assistants to help manage and track work efforts
8. Provide feedback to improve AI assistance

## Work Effort Structure

Each work effort follows this structure:

```markdown
---
title: "Work Effort Title"
status: "active"  # active, paused, completed, cancelled
priority: "medium"  # low, medium, high, critical
assignee: "username"
created: "YYYY-MM-DD HH:mm"
last_updated: "YYYY-MM-DD HH:mm"
due_date: "YYYY-MM-DD"
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# Work Effort Title

## 🚩 Objectives
- Clear, measurable goals

## 🛠 Tasks
- [ ] Specific tasks to complete

## 📝 Notes
- Context and relevant information

## 🐞 Issues Encountered
- Problems and blockers

## ✅ Outcomes & Results
- Results and lessons learned

## 📌 Linked Items
- Links to related work, issues, PRs

## 📅 Timeline & Progress
- Important dates and milestones
```

## Troubleshooting

If you encounter issues with AI assistance:

1. Ensure the Code Conductor package is installed correctly
2. Verify the `.AI_setup/` directory exists and contains all required files
3. Check that work efforts directory has proper Johnny Decimal structure
4. Ensure work efforts have properly formatted frontmatter
5. Try running `cc-ai setup` again to recreate files and directories
6. Check for error messages in the console
7. Verify category directories are named correctly (XX_category format)

## Advanced Features

1. **Status-based Organization**: Work efforts are organized by status rather than folders
2. **Category Selection**: Interactive mode allows choosing appropriate categories
3. **Frontmatter Parsing**: Intelligent parsing of work effort metadata
4. **Obsidian Compatibility**: Full compatibility with Obsidian markdown linking
5. **AI Integration**: Seamless integration with AI assistants for enhanced productivity