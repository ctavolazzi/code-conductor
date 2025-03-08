# AI-Setup

AI-Setup is a toolkit for setting up AI-assisted development environments and managing work efforts.

## Version

Current version: 0.2.3

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

### Global Installation on macOS

To install the package globally on macOS so you can use it from any directory:

```bash
# Install the package system-wide (requires administrator privileges)
sudo pip3 install -e /path/to/ai_setup

# Or install for the current user only
pip3 install -e /path/to/ai_setup --user
```

If you install with `--user`, you may need to add the Python user bin directory to your PATH:

```bash
# Add this line to your ~/.zshrc or ~/.bash_profile
export PATH=$PATH:$HOME/Library/Python/<version>/bin

# Then reload your shell configuration
source ~/.zshrc  # or source ~/.bash_profile
```

> **Tip**: If you're having trouble with global installation, ask your preferred AI model (like Claude, ChatGPT, etc.) for help specific to your system. They can provide customized installation instructions based on your operating system and environment.

## Usage

### Basic Commands

```bash
# Set up AI assistance in current directory
ai-setup setup

# Create a new work effort
ai-setup work_effort

# List all work efforts
ai-setup list

# Select directories to set up
ai-setup select
```

### Creating Work Efforts

```bash
# Interactive mode
ai-setup work_effort -i

# With specific details
ai-setup work_effort --title "New Feature" --priority high

# Using the enhanced AI work effort creator
ai-work-effort -i

# With AI content generation (requires Ollama)
ai-work-effort --use-ai --description "Implement authentication system" --model phi3
```

Note: AI content generation is OFF by default. Use the `--use-ai` flag to enable it.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and latest changes.

## License

MIT