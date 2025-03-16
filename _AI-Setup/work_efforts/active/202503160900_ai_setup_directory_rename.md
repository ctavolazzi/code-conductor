---
title: "AI Setup Directory Rename (_AI-Setup to _AI-Setup)"
status: "active" # options: active, paused, completed
priority: "high" # options: low, medium, high, critical
assignee: "AI Assistant"
created: "2025-03-16 09:00:00" # YYYY-MM-DD HH:mm
last_updated: "2025-03-16 10:30:00" # YYYY-MM-DD HH:mm
due_date: "2025-03-23" # YYYY-MM-DD
tags: [refactor, structure, visibility]
---

# AI Setup Directory Rename (_AI-Setup to _AI-Setup)

## 🚩 Objectives
- Replace all references to "_AI-Setup" with "_AI-Setup" throughout the codebase
- Make the AI-Setup directory visible in file systems that hide dotfiles by default
- Ensure backward compatibility for users transitioning from the old naming convention
- Update all documentation and code to reflect the new naming convention

## 🛠 Tasks
- [x] Update Python code references in core functionality (src/code_conductor)
- [x] Update utility scripts and helper functions
- [x] Update test files and test expectations
- [x] Update documentation (README.md, DEVLOG.md, etc.)
- [x] Create migration script for users to transition existing projects
- [x] Update version number and add changelog entry
- [ ] Test to ensure changes don't break existing functionality

## 📝 Notes
- The codebase has numerous references to "_AI-Setup" across many file types
- We already have a "_AI-Setup" directory with an established structure
- Test directories still use "_AI-Setup" in many places
- This change improves visibility and usability but requires careful coordination

## 🐞 Issues Encountered
- Some test directories still use "_AI-Setup" and will need to be updated during testing
- The migration script needs to handle cases where both "_AI-Setup" and "_AI-Setup" exist

## ✅ Outcomes & Results
- All core code now uses "_AI-Setup" instead of "_AI-Setup"
- Created a comprehensive migration script to help users transition
- Updated documentation to reflect the new naming convention
- Added changelog entry to document the change
- Improved visibility of the AI-Setup directory in file systems that hide dotfiles

## 📌 Linked Items
- [[202503160820_project_restructuring.md]]

## 📅 Timeline & Progress
- **Started**: 2025-03-16 09:00:00
- **Updated**: 2025-03-16 10:30:00
- **Target Completion**: 2025-03-23