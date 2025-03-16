---
title: "Work Effort Context Retrieval"
status: "active"
priority: "high"
assignee: "Developer Team"
created: "2025-03-16 08:05:00"
last_updated: "2025-03-16 08:25:00"
due_date: "2025-03-23"
tags: [context, retrieval, ai-assistance, scripts]
related_efforts: ["enhanced_workflow_runner", "workflow_runner_update"]
---

# Work Effort Context Retrieval

## 🚩 Objectives
- Create a script that efficiently retrieves and displays work effort content for AI context
- Implement multiple search options (name, status, date, recency)
- Support recursive exploration of related work efforts
- Display associated implementation scripts alongside work efforts
- Enhance AI instructions to prioritize using scripts for work effort management

## 🛠 Tasks
- [x] Create retrieve_work_effort.py script with comprehensive command-line options
- [x] Implement functions to find work efforts by various criteria
- [x] Add support for detecting and following relationships between work efforts
- [x] Implement recursive exploration of related work efforts
- [x] Add detection and display of associated scripts
- [x] Create comprehensive documentation in docs/retrieve_work_effort.md
- [x] Update README.md to include context retrieval features
- [x] Update CHANGELOG.md with the new context retrieval features
- [x] Update docs/README.md to include link to context retrieval documentation
- [x] Update AI instructions to prioritize using scripts over manual work effort creation
- [x] Add PyYAML to requirements.txt as it's needed for frontmatter parsing
- [x] Test error handling for non-existent work efforts, invalid status, and empty results

## 💡 Implementation Details

The implementation focuses on providing comprehensive context for AI assistants when working with the Code Conductor codebase. The script provides multiple ways to find and display work efforts:

1. **Search by name**: Find work efforts matching a specific name or part of a name
   ```bash
   ./retrieve_work_effort.py --name "feature-name"
   ```

2. **Search by status**: Find all work efforts with a specific status
   ```bash
   ./retrieve_work_effort.py --status active
   ```

3. **Search by date**: Find work efforts created on a specific date
   ```bash
   ./retrieve_work_effort.py --date 20250316
   ```

4. **Get latest work efforts**: Find the most recently created work efforts
   ```bash
   ./retrieve_work_effort.py --latest 5
   ```

5. **Find related work efforts**: Find work efforts related to a specific one
   ```bash
   ./retrieve_work_effort.py --related "feature-name"
   ```

The script also supports:
- Recursive exploration of related work efforts
- Display of associated implementation scripts
- Comprehensive output formatting for AI consumption
- Graceful error handling for various edge cases

## 🧪 Testing

Testing for this feature included:
- Finding work efforts by name, status, date, and recency
- Recursive exploration of related work efforts
- Proper handling of missing or invalid work efforts (returns clear error messages)
- Correct display of associated scripts
- Proper handling of command-line arguments
- Error handling for invalid inputs (non-existent work efforts, invalid status values)
- Handling of dates with no associated work efforts

## 📌 Dependencies
- Python 3.6+
- PyYAML for frontmatter parsing (added to requirements.txt)
- Standard library modules (os, re, argparse, etc.)

## 📚 Documentation
- Comprehensive documentation created in docs/retrieve_work_effort.md
- Updates to README.md to include context retrieval features
- Updates to CHANGELOG.md with the new features
- Updates to docs/README.md to link to context retrieval documentation
- Updated AI instructions to prioritize using scripts

## 📝 Notes
- This script enhances the AI assistant workflow by providing comprehensive context
- The script is designed to be used before engaging with the workflow process
- The updated AI instructions guide assistants to use the existing scripts instead of manual work effort creation
- Error handling was designed to be user-friendly with clear messages when things go wrong
- The script gracefully handles edge cases like non-existent work efforts, invalid statuses, and dates with no work efforts