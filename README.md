# Code Conductor

Code Conductor is a lightweight, text-based system for creating powerful AI work circuits. Build contextual workflows using markdown files with Obsidian-style linking that scale infinitely. Works with any LLM on any hardware, delivering human-readable, durable knowledge management without complexity.

## Version

Current version: 0.4.6

## Features

- **AI-powered workflows that scale with your needs**
  - **NEW: Automated Workflow Runner for guided development process**
  - **NEW: Work effort status management and lifecycle tracking**
  - **NEW: Work effort context retrieval for enhanced AI assistance**
- **Markdown-based knowledge management**
  - **New: Folder-based work efforts for better organization**
  - **New: Obsidian-style document linking between work efforts**
  - **New: Consolidated work effort management**
- **Hardware-agnostic performance** - works on any machine
- **Universal LLM compatibility** - use your preferred AI models
- **NEW: Improved directory handling**
  - **New: Works with your current directory by default**
  - **New: Clear messaging about file locations**
  - **New: No need to set PYTHONPATH manually**
  - **New: Better work effort discovery and listing**

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

## Recommended Usage with Cursor and Obsidian

For the optimal Code Conductor experience, we recommend using it with:

### Cursor IDE + Obsidian Setup

1. **Install [Cursor](https://cursor.sh/)** - An AI-powered code editor based on VS Code
2. **Install [Obsidian](https://obsidian.md/)** - A powerful knowledge base that works on top of a local folder of plain text Markdown files

### Setup Process

1. **Open your project in Obsidian**:
   - Open Obsidian and select "Open folder as vault"
   - Navigate to your project directory and select it
   - This allows you to visualize work efforts and their connections

2. **Open your project in Cursor**:
   - Launch Cursor and open your project folder
   - Install Code Conductor:
     ```bash
     pip install code-conductor
     ```
   - Run the setup command:
     ```bash
     code-conductor setup
     ```

3. **Working with both tools**:
   - Use Cursor for coding and AI assistance
   - Use Obsidian for viewing, navigating, and editing the work effort documentation
   - The _AI-Setup folder will contain all your work efforts and documentation

4. **Configure Obsidian to use your Code Conductor directory**
   - Open Obsidian and create a new vault pointing to your Code Conductor project directory
   - This allows you to navigate and edit your work efforts with Obsidian's powerful markdown editor and graph view

## How to Use Work Efforts Properly

Code Conductor's work effort system provides a structured way to manage AI-assisted development tasks while maintaining a comprehensive knowledge base. Here's how to use it effectively:

### Work Effort Creation

You can create work efforts in several ways:

```bash
# Create a new work effort in the default location with timestamp naming
cc-new "My Work Effort Title"

# Create a work effort with sequential numbering (recommended)
cc-new "My Work Effort Title" --sequential

# Create a work effort in a specific status
cc-new "My Work Effort Title" --status active|completed|archived
```

### Work Effort Organization

Work efforts can be stored in different locations:

- `/work_efforts/` - The default directory for work efforts
- `/_AI-Setup/work_efforts/` - Alternative directory for system-level work efforts
- Custom directories can also contain work efforts, which will be found by the indexing system

Within these directories, work efforts are organized by status:
- `/active/` - Currently in-progress work efforts
- `/completed/` - Finished work efforts
- `/archived/` - Historical or inactive work efforts

### Naming Conventions

Code Conductor supports multiple naming conventions for work efforts:

1. **Sequential Numbering (Recommended)**: `0001_my_work_effort.md`
   - Simple, clean, and easy to reference
   - Automatically increments based on existing files
   - Use `--sequential` flag with `cc-new`

2. **Timestamp-based**: `202503170001_my_work_effort.md`
   - Default behavior
   - Includes date and time information
   - Good for chronological organization

3. **Free-form**: `my_work_effort.md`
   - Supported by the indexing system
   - Good for specific use cases
   - Less structured but more flexible

### Indexing and Discovery

The indexing system helps you find work efforts across your project:

```bash
# Basic indexing of work efforts
cc-index

# Comprehensive indexing that finds non-standard work efforts
cc-index --thorough

# Display a summary of all indexed work efforts
cc-index --summary

# Filter work efforts by content or title
cc-index --filter "keyword"
```

### Document Linking

Connect related work efforts using Obsidian-style wiki links:

```markdown
# My Work Effort

This work effort is related to [[Another Work Effort]].
```

### Best Practices

1. **Use Sequential Numbering**: Makes work efforts easy to reference and organize
2. **Keep Status Current**: Move work efforts between active/completed/archived as they progress
3. **Link Related Documents**: Create a knowledge graph by linking related work efforts
4. **Run Regular Indexing**: Use `cc-index --thorough --summary` periodically to maintain an overview
5. **Follow Templates**: Use the built-in templates to ensure consistent structure
6. **Include Metadata**: Add relevant metadata like assignee, due date, and status
7. **Use Folders for Complex Work**: For larger efforts, use folder-based work efforts with supporting files

## Quick Start

Code Conductor now works with your current directory by default. Just run:

```bash
# Set up AI assistance in the current directory:
code-conductor setup

# Create a new work effort:
code-conductor work

# List all work efforts:
code-conductor list
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

## What's New in 0.4.6

### Work Effort Indexing

New comprehensive work effort indexing system:
- Scans the entire project for work efforts regardless of their location
- Identifies work efforts in both `work_efforts` and `_AI-Setup` directories
- Creates a structured JSON index for easy tracking and referencing
- Includes command-line tool for convenient access and visualization
- Provides statistical summary of work effort distribution

```bash
# Scan project and show work efforts as a table
python src/code_conductor/scripts/index_work_efforts.py

# Show summary statistics
python src/code_conductor/scripts/index_work_efforts.py --summary

# Output as JSON
python src/code_conductor/scripts/index_work_efforts.py --format json
```

### Sequential Work Effort Numbering

Work efforts now support sequential numbering for better organization:
- Automatic sequential numbering (e.g., 0001, 0002, 0003)
- Graceful transition to 5+ digits when needed (9999 → 10000)
- Option to use date-prefixed numbering (e.g., 202304250001)
- Intelligent initialization from existing work efforts
- Durable counter system that survives system shutdowns

```python
# Create work effort with sequential numbering (default)
code-conductor work

# Create work effort with date-prefixed numbering
code-conductor work --date-prefix

# Use timestamp-based naming instead of sequential numbering
code-conductor work --no-sequential-numbering
```

### Automated Workflow Runner

The new Workflow Runner automates the entire Code Conductor development process:
- Step-by-step guidance through the 8 phases of feature development
- Automatic script generation with proper structure and testing
- Document validation to ensure complete documentation
- Support for both interactive and non-interactive modes
- Template integration with the official project templates

[Read the full documentation](docs/workflow_runner.md)

### Work Effort Status Management

Work efforts now support complete lifecycle management:
- Move work efforts between active, completed, and archived states
- Automatic file organization based on status
- Programmatic and interactive status changes
- Enhanced metadata tracking for work efforts

[Read the full documentation](docs/workflow_runner.md#status-management)

### Work Effort Context Retrieval

The new retrieve_work_effort.py script provides comprehensive context for AI assistants:
- Find work efforts by name, status, date, or recency
- Display related work efforts and associated scripts
- Recursive exploration of linked work efforts
- Comprehensive output format for AI context gathering

[Read the full documentation](docs/retrieve_work_effort.md)

### Folder-Based Work Efforts

Work efforts now create dedicated folders instead of single files, allowing you to:
- Store related files alongside your work effort tracking
- Better organize project documents and resources
- Keep implementation files with planning documents

[Read the full documentation](docs/folder_based_work_efforts.md)

### Obsidian-Style Document Linking

Work efforts now support Obsidian-style wiki links using the `

## Command Line Tools

### Creating Work Efforts

The simplest way to create a new work effort is with the `cc-new` command:

```bash
# Basic usage:
cc-new "Title of Work Effort"

# With options:
cc-new "Bug Fix" -p high -a "Developer Name" -d 2023-12-31

# Show verbose output:
cc-new "Feature Implementation" -v
```

This command creates a properly formatted work effort using the WorkEffortManager.

#### Options:

- `-a, --assignee`: Person assigned to the work (default: unassigned)
- `-p, --priority`: Priority level (low, medium, high, critical) (default: medium)
- `-d, --due-date`: Due date in YYYY-MM-DD format (default: today)
- `-l, --location`: Project directory to create work effort in (default: current directory)
- `-v, --verbose`: Show detailed output

Other available commands include:

- `code-conductor`: The main CLI for the project
- `cc-work-e`: Interactive work effort creator with AI capabilities
- `cc-index`: Index and list all work efforts in the project