# AI Setup Instructions

This file contains detailed instructions for setting up AI assistance in this project.
It helps AI assistants understand how to configure and use the AI tools.

## Installation

The AI_Setup package can be installed globally using:

```bash
sudo pip3 install ai_setup
```

After installation, the following commands will be available:
- `ai_setup` - Main command for AI setup and work effort management
- `ai_work_effort` - Enhanced work effort creator with AI features

## Setting Up a Project

To set up a new or existing project with AI assistance:

1. Navigate to the project directory:
   ```bash
   cd /path/to/your/project
   ```

2. Run the setup command:
   ```bash
   ai_setup setup
   ```

This will:
- Create a `.AI_setup` folder with all necessary files
- Set up a `work_efforts` directory structure
- Create an initial default work effort

## Creating Work Efforts

Basic work effort creation:
```bash
ai_setup work_effort --title "Feature Name" --priority high
```

Enhanced work effort creation with more features:
```bash
ai_work_effort -i
```

With AI-powered content generation (requires Ollama):
```bash
ai_work_effort --use_ai --description "Create a user authentication system" --model phi3
```

## Managing Work Efforts

List all work efforts:
```bash
ai_setup list
```

## Directory Structure

A properly configured project will have:

```
your_project/
├── .AI_setup/
│   ├── INSTRUCTIONS.md
│   ├── AI_setup_validation_instructions.md
│   ├── AI_work_effort_system.md
│   └── AI_setup_instructions.md
└── work_efforts/
    ├── templates/
    │   └── work_effort_template.md
    ├── active/
    ├── completed/
    ├── archived/
    └── README.md
```

## Advanced Features

The `ai_work_effort` command supports integration with Ollama for AI-powered content generation. When using the `--use_ai` flag, it can:

1. Connect to a local Ollama instance
2. Generate structured content based on your description
3. Provide an interactive console experience with animated typing
4. Allow for timeout configuration and graceful interruption
