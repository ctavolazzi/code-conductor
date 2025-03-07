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
python cli.py

# Create a new work effort interactively
python cli.py work

# List all work efforts
python cli.py list

# Select directories to set up
python cli.py select
```

You can also use the thought process simulator for AI-generated content by providing a description:

```bash
python cli.py work --description "Implement new feature X with responsive UI"
```