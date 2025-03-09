# AI Work Effort System

This file describes the work effort system used in this project.
It helps AI assistants understand how to manage and track work efforts.

## Work Effort Structure

Each work effort is a markdown file that contains structured information about a task, feature, bug fix, or any other unit of work. The file follows this format:

```markdown
---
title: "Title of the Work Effort"
status: "active" # options: active, paused, completed
priority: "medium" # options: low, medium, high, critical
assignee: "username"
created: "YYYY-MM-DD HH:MM" # Date and time
last_updated: "YYYY-MM-DD HH:MM" # Date and time
due_date: "YYYY-MM-DD" # Date only
tags: [tag1, tag2, tag3]
---

# Title of the Work Effort

## 🚩 Objectives
- Clear goal 1
- Clear goal 2

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## 📝 Notes
- Context information
- Relevant details

## 🐞 Issues Encountered
- Obstacles or challenges

## ✅ Outcomes & Results
- Results achieved
- Lessons learned

## 📌 Linked Items
- [[Related File]]
- [[GitHub Issue #123]]

## 📅 Timeline & Progress
- **Started**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD
- **Target Completion**: YYYY-MM-DD
```

## Work Effort Commands

Creating work efforts:
```
ai-setup work_effort --title "Feature Name" --priority high
ai-work-effort -i  # Interactive mode with more features
```

Listing work efforts:
```
ai-setup list
```

## Work Effort Locations

Work efforts are organized into directories:
- `work_efforts/active/` - Current, in-progress work
- `work_efforts/completed/` - Successfully finished work
- `work_efforts/archived/` - Deprecated or abandoned work
