# Work Efforts

This directory contains work efforts for tracking tasks and progress.

## Directory Structure

- **active/**: Current work efforts in progress
- **completed/**: Finished work efforts
- **archived/**: Historical work efforts
- **templates/**: Templates for creating new work efforts

## Usage

Run the CLI tool to manage work efforts:

```bash
# Set up in current directory
code-conductor setup

# Create a new work effort interactively
code-conductor work_effort

# List all work efforts
code-conductor list

# Select directories to set up
code-conductor select
```

You can also use the thought process simulator for AI-generated content by providing a description:

```bash
cc-work-e --use-ai --description "Implement new feature X with responsive UI"
```