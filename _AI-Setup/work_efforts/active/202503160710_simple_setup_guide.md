---
title: "Simple Setup Guide"
created: "2025-03-16 07:10:00"
version: "0.0.1"
priority: "high"
status: "active"
tags: ["setup", "guide", "documentation", "quickstart"]
related_efforts:
  - "[[202503171315_versioned_workflow_process.md]]"
---

# Code Conductor Simple Setup Guide v0.0.1

## Quick Installation

```bash
# Install from PyPI
pip install code-conductor

# For development installation
git clone https://github.com/ctavolazzi/code-conductor.git
cd code-conductor
pip install -e .
```

## Basic Commands

```bash
# Initialize Code Conductor in the current directory
code-conductor setup

# Create a new work effort
code-conductor work_effort

# Create work effort with shorthand (current directory)
cc-work-e
```

## Directory Structure

Code Conductor creates the following structure:
```
_AI-Setup/
├── work_effort/               # Main storage for all work efforts
│   ├── active/                # In-progress work efforts
│   ├── archived/              # Historical work efforts
│   ├── completed/             # Finished work efforts
│   ├── node/                  # Work nodes connecting multiple documents
│   └── templates/             # Templates for work efforts
├── scripts/                   # Helper scripts
└── README.md                  # Local documentation
```

## Creating Your First Work Effort

1. Run `cc-work-e` in your project directory
2. Fill in the title, priority, and description
3. Edit the created markdown file with additional details
4. Reference it in your commits using the filename

## Using Work Nodes

```bash
# Create a node connecting multiple documents
./create_work_node.py --title "My Feature" --documents doc1.md doc2.md doc3.md

# Auto-discover related documents
./create_work_node.py --auto-discover
```

## Next Steps

1. Review the [Workflow Process](_AI-Setup/work_efforts/active/202503160710_versioned_workflow_process.md)
2. Explore the [Work Node Feature](./work_node_README.md)
3. Check out [Obsidian-style Linking](_AI-Setup/work_efforts/active/202503160633_obsidian_style_document_linking.md)

## Troubleshooting

- Ensure Python 3.8+ is installed
- Check that the Code Conductor package is in your PATH
- Work efforts should always be created in a directory with a `_AI-Setup` folder

For more detailed information, refer to the full documentation in the project README.md.