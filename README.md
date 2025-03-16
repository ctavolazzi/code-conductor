# Code Conductor

Code Conductor is a lightweight, text-based system for creating powerful AI work circuits. Build contextual workflows using markdown files with Obsidian-style linking that scale infinitely. Works with any LLM on any hardware, delivering human-readable, durable knowledge management without complexity.

## Version

Current version: 0.4.5

## Features

- **AI-powered workflows that scale with your needs**
- **Markdown-based knowledge management**
  - **New: Folder-based work efforts for better organization**
  - **New: Obsidian-style document linking between work efforts**
  - **New: Consolidated work effort management**
- **Hardware-agnostic performance** - works on any machine
- **Universal LLM compatibility** - use your preferred AI models

## Installation

```bash
pip install code-conductor
```

### Local Development

Clone the repository and install:

```bash
git clone https://github.com/ctavolazzi/code-conductor.git
cd code-conductor
pip install -e .
```

### Global Installation on macOS

To install the package globally on macOS so you can use it from any directory:

```bash
# Install the package system-wide (requires administrator privileges)
sudo pip3 install -e /path/to/code-conductor

# Or install for the current user only
pip3 install -e /path/to/code-conductor --user
```

If you install with `--user`, you may need to add the Python user bin directory to your PATH:

```bash
# Add this line to your ~/.zshrc or ~/.bash_profile
export PATH=$PATH:$HOME/Library/Python/<version>/bin

# Then reload your shell configuration
source ~/.zshrc  # or source ~/.bash_profile
```

> **Tip**: If you're having trouble with global installation, ask your preferred AI model (like Claude, ChatGPT, etc.) for help specific to your system. They can provide customized installation instructions based on your operating system and environment.

## What's New in 0.4.5

### Folder-Based Work Efforts

Work efforts now create dedicated folders instead of single files, allowing you to:
- Store related files alongside your work effort tracking
- Better organize project documents and resources
- Keep implementation files with planning documents

[Read the full documentation](docs/folder_based_work_efforts.md)

### Obsidian-Style Document Linking

Work efforts now support Obsidian-style wiki links using the `[[document]]` syntax:
- Link related work efforts using double bracket notation
- Navigate between connected documents
- Create knowledge networks across your project
- Automatically track related efforts in frontmatter

[Read the full documentation](docs/obsidian_style_linking.md)

### Work Effort Consolidation

A new script makes it easy to organize all work efforts into a centralized location:
- Consolidate scattered work efforts into `.AI-Setup/work_efforts`
- Preserve directory structure (active, archived, completed)
- Add Obsidian-style links between related documents
- Clean up duplicate directories

[Read the full documentation](docs/work_effort_consolidation.md)

## Usage

### Basic Commands

```bash
# Set up AI assistance in current directory
code-conductor setup

# Create a new work effort
code-conductor work_effort

# List all work efforts
code-conductor list

# Select directories to set up
code-conductor select

# Consolidate work efforts into a central location
python consolidate_work_efforts.py
```

### Creating Work Efforts

```bash
# Interactive mode
code-conductor work_effort -i

# With specific details
code-conductor work_effort --title "New Feature" --priority high

# Using the work effort creator (quick shorthand)
cc-work-e -i

# Create in current directory explicitly
cc-work-e --current-dir

# Create in package directory explicitly
cc-work-e --package-dir

# With AI content generation (requires Ollama)
cc-work-e --use-ai --description "Implement authentication system" --model phi3
```

Note:
- AI content generation is OFF by default. Use the `--use-ai` flag to enable it.
- `cc-work-e` creates work efforts in the current directory by default when using no parameters.
- Use `--current-dir` or `--package-dir` to explicitly specify where to create work efforts.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and latest changes.

## License

MIT