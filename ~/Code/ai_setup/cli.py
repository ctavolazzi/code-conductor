import os

def create_ai_setup(root_dir=None):
    """Create the .AI-setup folder structure with all necessary files."""
    if root_dir is None:
        root_dir = os.getcwd()

    # Define the AI setup folder
    setup_folder = os.path.join(root_dir, ".AI-Setup")

    # Create .AI-Setup folder
    if not os.path.exists(setup_folder):
        os.makedirs(setup_folder)

    # Create all necessary files with embedded content
    # 1. INSTRUCTIONS.md
    instructions_file = os.path.join(setup_folder, "INSTRUCTIONS.md")
    with open(instructions_file, "w") as f:
        f.write("""# AI-Setup Instructions

This directory contains setup files for AI-assisted development.

## Usage

This setup enables your AI assistants to better understand your project structure
and provide more contextual help and recommendations.

### Commands

The AI-Setup package provides two main commands:

1. `ai-setup` - Main command for setting up AI assistance and basic work efforts
   - `ai-setup help` - Show help information
   - `ai-setup setup` - Set up AI assistance in the current directory
   - `ai-setup work_effort` - Create a new work effort
   - `ai-setup list` - List all work efforts

2. `ai-work-effort` - Enhanced work effort creator with AI content generation capabilities
   - `ai-work-effort -i` - Create a work effort interactively
   - `ai-work-effort --use-ai --description "Your description"` - Use AI to generate content
   - `ai-work-effort --help` - Show help information

No action is required from you - the AI tools will automatically utilize these files.
""")

    # 2. AI-setup-validation-instructions.md
    validation_file = os.path.join(setup_folder, "AI-setup-validation-instructions.md")
    with open(validation_file, "w") as f:
        f.write("""# AI Setup Validation Instructions

This file contains instructions for validating the AI setup in this project.
It helps AI assistants understand how to verify that everything is working correctly.

## Validation Steps

1. Check that the `.AI-Setup` folder exists and contains all required files
2. Verify that the `work_efforts` directory structure is properly set up
3. Confirm that the AI-setup commands are working as expected

## Required Components

1. `.AI-Setup` folder with:
   - INSTRUCTIONS.md
   - AI-setup-validation-instructions.md
   - AI-work-effort-system.md
   - AI-setup-instructions.md

2. `work_efforts` directory with:
   - templates/
   - active/
   - completed/
   - archived/

## Testing Commands

You can test that the AI setup is working correctly by running:

```
ai-setup list
```

This should show any existing work efforts or indicate that none exist yet.
""")

    # 3. AI-work-effort-system.md
    work_effort_file = os.path.join(setup_folder, "AI-work-effort-system.md")
    with open(work_effort_file, "w") as f:
        f.write("""# AI Work Effort System

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
""")

    # 4. AI-setup-instructions.md
    setup_instructions_file = os.path.join(setup_folder, "AI-setup-instructions.md")
    with open(setup_instructions_file, "w") as f:
        f.write("""# AI Setup Instructions

This file contains detailed instructions for setting up AI assistance in this project.
It helps AI assistants understand how to configure and use the AI tools.

## Installation

The AI-Setup package can be installed globally using:

```bash
sudo pip3 install ai-setup
```

After installation, the following commands will be available:
- `ai-setup` - Main command for AI setup and work effort management
- `ai-work-effort` - Enhanced work effort creator with AI features

## Setting Up a Project

To set up a new or existing project with AI assistance:

1. Navigate to the project directory:
   ```bash
   cd /path/to/your/project
   ```

2. Run the setup command:
   ```bash
   ai-setup setup
   ```

This will:
- Create a `.AI-Setup` folder with all necessary files
- Set up a `work_efforts` directory structure
- Create an initial default work effort

## Creating Work Efforts

Basic work effort creation:
```bash
ai-setup work_effort --title "Feature Name" --priority high
```

Enhanced work effort creation with more features:
```bash
ai-work-effort -i
```

With AI-powered content generation (requires Ollama):
```bash
ai-work-effort --use-ai --description "Create a user authentication system" --model phi3
```

## Managing Work Efforts

List all work efforts:
```bash
ai-setup list
```

## Directory Structure

A properly configured project will have:

```
your-project/
├── .AI-Setup/
│   ├── INSTRUCTIONS.md
│   ├── AI-setup-validation-instructions.md
│   ├── AI-work-effort-system.md
│   └── AI-setup-instructions.md
└── work_efforts/
    ├── templates/
    │   └── work-effort-template.md
    ├── active/
    ├── completed/
    ├── archived/
    └── README.md
```

## Advanced Features

The `ai-work-effort` command supports integration with Ollama for AI-powered content generation. When using the `--use-ai` flag, it can:

1. Connect to a local Ollama instance
2. Generate structured content based on your description
3. Provide an interactive console experience with animated typing
4. Allow for timeout configuration and graceful interruption
""")

    print(f"✅ Created AI-Setup in: {root_dir}")
    return setup_folder