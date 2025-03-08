# AI-Setup

AI-Setup is a toolkit for setting up AI-assisted development environments and managing work efforts.

## Version

Current version: 0.2.1

## Features

- AI-assisted development setup
- Work efforts tracking and management
- Project templates
- CLI tools for AI integration

## Installation

### Local Development

Clone the repository and install:

```bash
git clone https://github.com/username/ai_setup.git
cd ai_setup
pip install -e .
```

## Usage

### Basic Commands

```bash
# Set up AI assistance in current directory
ai-setup init

# Create a new work effort
ai-setup work

# List all work efforts
ai-setup list

# Select directories to set up
ai-setup select
```

### Creating Work Efforts

```bash
# Interactive mode
ai-setup work -i

# With specific details
ai-setup work "New Feature" --description "Implement the new feature X" --priority high
```

Note: AI content generation is OFF by default. Use the `--use-ai` flag to enable it.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and latest changes.

## License

MIT