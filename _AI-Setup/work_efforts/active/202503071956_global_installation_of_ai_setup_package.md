---
title: "Global Installation of AI Setup Package"
status: "active" # options: active, paused, completed
priority: "medium" # options: low, medium, high, critical
assignee: "self"
created: "2025-03-07 19:56" # YYYY-MM-DD HH:mm
last_updated: "2025-03-07 20:15" # YYYY-MM-DD HH:mm
due_date: "2025-03-07" # YYYY-MM-DD
tags: [installation, global, package, setup]
---

# Global Installation of AI Setup Package

## 🚩 Objectives
- Install the AI Setup package globally on the system
- Ensure the `ai_setup` command is available from anywhere
- Include all necessary _AI-Setup files in the installation
- Add the advanced AI-powered work effort creation script
- Verify successful installation and functionality

## 🛠 Tasks
- [x] Check if the package is already installed globally
- [x] Uninstall previous versions if necessary
- [x] Update setup.py to include package data
- [x] Include all necessary _AI-Setup files in the installation
- [x] Create MANIFEST.in to ensure proper file inclusion
- [x] Add a new ai_work_effort_creator.py script with Ollama integration
- [x] Update setup.py to include the script as an entry point
- [x] Install the package globally using pip with setuptools
- [x] Verify the installation by running commands from different directories
- [x] Update shell configuration to include the package's bin directory in PATH
- [x] Update INSTRUCTIONS.md to document the new features
- [x] Test global installation with pip
- [x] Verify that installed package includes all required files
- [x] Update documentation to reflect global installation process

## 📝 Notes
- The `setup.py` file defines entry points `ai_setup=cli:main_entry` and `ai_work_effort=work_efforts.scripts.ai_work_effort_creator:main`
- Package version is 0.2.1
- Installing globally will make the commands available in any directory
- On macOS, the `pip install --user` command installs packages to `$HOME/Library/Python/[version]/bin`
- This directory must be added to the PATH to access the commands from any terminal
- The ai_work_effort script provides AI-powered content generation using Ollama with animated thought process
- [x] Update setup.py to include _AI-Setup files

## 🐞 Issues Encountered
- When installing with `pip3 install -e . --user`, the installation directory `/Users/ctavolazzi/Library/Python/3.10/bin` is not in PATH by default
- This causes the command to be unavailable in terminals unless the PATH is updated
- PATH changes made with `export` are only temporary and affect only the current terminal session
- Setup needed proper package structure with __init__.py files to ensure scripts are properly included
- Entry points in setup.py needed both sync and async versions for the AI work effort creator

## ✅ Outcomes & Results
- Successfully enhanced the package to include:
  - All _AI-Setup files (INSTRUCTIONS.md, AI-setup-validation-instructions.md, etc.)
  - A new ai_work_effort command with Ollama integration for AI-powered content generation
- Updated INSTRUCTIONS.md with documentation for both commands
- Successfully installed the package using `pip3 install -e . --user`
- Added the Python user bin directory to PATH permanently by adding it to `.zshrc`
- After sourcing `.zshrc` or restarting terminals, both commands are available globally

## 📋 Files to Include
- All Python modules and packages
- All _AI-Setup files (INSTRUCTIONS.md, AI-setup-validation-instructions.md, etc.)
- All work effort templates and scripts
- README.md, LICENSE, and other documentation

## 📌 Linked Items
- [[setup.py]]
- [[cli.py]]
- [[work_efforts/scripts/ai_work_effort_creator.py]]
- [[_AI-Setup/INSTRUCTIONS.md]]

## 📅 Timeline & Progress
- **Started**: 2025-03-07 19:56
- **Updated**: 2025-03-07 20:15
- **Target Completion**: 2025-03-07