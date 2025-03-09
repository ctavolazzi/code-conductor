import os
import sys
import shutil
import argparse
import asyncio
from datetime import datetime

# Update version references
VERSION = "0.4.1"

# Re-import the necessary AI setup modules
try:
    from utils.directory_scanner import select_directories, is_ai_setup_installed, create_ai_setup, install_ai_setup
    from utils.thought_process import generate_content_with_ollama, get_available_ollama_models
except ImportError:
    print("Warning: Required modules not found. Some functionality will be limited.")

    # Fallback directory scanner functions if import fails
    def select_directories(base_dir=None):
        """Fallback directory selector if import fails"""
        if base_dir is None:
            base_dir = os.getcwd()

        print(f"\nScanning for directories in: {base_dir}")
        # Get directories and ensure they are unique
        all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]
        dirs = sorted(set(all_dirs))

        if len(dirs) != len(all_dirs):
            print(f"Note: Removed {len(all_dirs) - len(dirs)} duplicate directory entries")

        if not dirs:
            print("No directories found.")
            return []

        print("\nAvailable directories:")
        for i, d in enumerate(dirs):
            print(f"{i+1}. {d}")

        selections = input("\nEnter directory numbers separated by space (e.g., '1 3 4') or 'all': ")

        if selections.lower() == 'all':
            return [os.path.join(base_dir, d) for d in dirs]

        try:
            selected_indexes = [int(i)-1 for i in selections.split()]
            return [os.path.join(base_dir, dirs[i]) for i in selected_indexes if 0 <= i < len(dirs)]
        except:
            print("Invalid selection. Please provide valid numbers.")
            return []

    def is_ai_setup_installed(directory):
        return os.path.exists(os.path.join(directory, ".AI-Setup"))

    def create_ai_setup(root_dir=None):
        """Create the .AI-setup folder structure with all necessary files."""
        if root_dir is None:
            root_dir = os.getcwd()

        # Define the AI setup folder
        setup_folder = os.path.join(root_dir, ".AI-Setup")

        # Create .AI-Setup folder
        if not os.path.exists(setup_folder):
            os.makedirs(setup_folder)

        # Create all other files first
        # 1. Create INSTRUCTIONS.md
        instructions_file = os.path.join(setup_folder, "INSTRUCTIONS.md")
        with open(instructions_file, "w") as f:
            f.write("""# AI-Setup Instructions

This directory contains setup files for AI-assisted development.

## Usage

This setup enables your AI assistants to better understand your project structure
and provide more contextual help and recommendations.

### Commands

The AI-Setup package provides two main commands:

1. `ai_setup` - Main command for setting up AI assistance and basic work efforts
   - `ai_setup help` - Show help information
   - `ai_setup setup` - Set up AI assistance in the current directory
   - `ai_setup work_effort` - Create a new work effort
   - `ai_setup list` - List all work efforts

2. `ai_work_effort` - Enhanced work effort creator with AI content generation capabilities
   - `ai_work_effort -i` - Create a work effort interactively
   - `ai_work_effort --use-ai --description "Your description"` - Use AI to generate content
   - `ai_work_effort --help` - Show help information

No action is required from you - the AI tools will automatically utilize these files.
""")

        # 2. Create AI-setup-validation-instructions.md
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
   - work_efforts/ directory with:
     - templates/
     - active/
     - completed/
     - archived/
     - scripts/

2. Root level `work_efforts` directory (maintained for backward compatibility)

## Testing Commands

You can test that the AI setup is working correctly by running:

```
ai-setup list
```

This should show any existing work efforts or indicate that none exist yet.
""")

        # 3. Create AI-work-effort-system.md
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
created: "YYYY-MM-DD HH:mm" # Creation date and time
last_updated: "YYYY-MM-DD HH:mm" # Last update date and time
due_date: "YYYY-MM-DD" # Expected completion date
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# Title of the Work Effort

## 🚩 Objectives
- Clearly define goals for this work effort

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references

## 🐞 Issues Encountered
- Document issues and obstacles clearly

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD
- **Target Completion**: YYYY-MM-DD
```

## Directory Structure

Work efforts are organized in the following directories:

- **templates/** - Contains templates for creating new work efforts
- **active/** - Current, ongoing work efforts
- **completed/** - Successfully completed work efforts
- **archived/** - Deprecated or abandoned work efforts
- **scripts/** - Helper scripts for managing work efforts

## Using the Work Effort System

1. Create a new work effort using the CLI:
```
ai-setup work_effort --title "Feature Name" --priority high
```

2. Or use the interactive mode:
```
ai-setup work_effort -i
```

3. Update work effort status as it progresses:
```
ai-setup update-status "Feature Name" --status completed
```

4. List all work efforts:
```
ai-setup list
```

## Best Practices

1. Use descriptive titles that clearly indicate the task
2. Break down complex work efforts into manageable tasks
3. Update the status regularly
4. Document issues and blockers immediately
5. Keep the timeline updated
6. Move completed work efforts to the 'completed' directory
7. Archive work efforts that are no longer relevant

## AI Integration

The Work Effort system is designed to work seamlessly with AI assistants:

1. AI assistants can read and understand the structure of work efforts
2. They can suggest updates and improvements
3. They can help prioritize and organize tasks
4. They can provide insights based on the documented issues and outcomes

## Advanced Features

1. Work efforts can be linked to form a network of related tasks
2. Dependencies between work efforts can be specified
3. Complex projects can be broken down into multiple linked work efforts
4. AI models can analyze patterns across work efforts to provide insights
""")

        # 4. Create AI-setup-instructions.md
        ai_setup_instructions_file = os.path.join(setup_folder, "AI-setup-instructions.md")
        with open(ai_setup_instructions_file, "w") as f:
            f.write("""# AI Setup Instructions

This file contains detailed instructions for setting up AI assistance in this project.
It helps AI assistants understand the structure and purpose of the project.

## Project Structure

This project follows a standard structure:

1. `src/` - Source code directory
2. `tests/` - Test files
3. `docs/` - Documentation
4. `.AI-Setup/` - AI assistant setup files

## Setting Up AI Assistance

To set up AI assistance in a project:

1. Install the AI-Setup package:
```
pip install ai_setup
```

2. Run the setup command in your project directory:
```
ai-setup setup
```

3. This will create the necessary files and directories:
   - `.AI-Setup/` directory with configuration files
   - `work_efforts/` directory for tracking tasks

## Using AI Assistance

Once set up, AI assistants can:

1. Better understand your project structure
2. Provide more contextual recommendations
3. Help manage and track work efforts
4. Offer insights based on project patterns

## Work Efforts

Work efforts are structured documents for tracking tasks. To create a new work effort:

```
ai-setup work_effort -i
```

This will create a new file in the `work_efforts/active/` directory.

## Commands

The AI-Setup package provides the following commands:

1. `ai-setup setup` - Set up AI assistance in the current directory
2. `ai-setup work-effort` - Create a new work effort
3. `ai-setup list` - List all work efforts
4. `ai-setup update-status` - Update the status of a work effort
5. `ai-setup help` - Show help information

## Configuration

AI assistance can be configured by modifying the files in the `.AI-Setup/` directory.

## Best Practices

1. Keep work efforts updated
2. Use descriptive titles for work efforts
3. Document issues and blockers
4. Update the status of work efforts regularly
5. Move completed work efforts to the 'completed' directory
6. Archive work efforts that are no longer relevant
7. Use AI assistants to help manage and track work efforts
8. Provide feedback to improve AI assistance

## Troubleshooting

If you encounter issues with AI assistance:

1. Ensure the AI-Setup package is installed correctly
2. Verify the `.AI-Setup/` directory exists
3. Check that work efforts are created in the correct directory
4. Ensure the files in the `.AI-Setup/` directory are properly formatted
5. Try running `ai-setup setup` again to recreate the files and directories
6. Check for error messages in the console
7. Report issues to the AI-Setup team

## Advanced Features

1. AI models can be customized for specific projects
2. Work efforts can be linked to form a network of related tasks
3. Complex projects can be broken down into multiple linked work efforts
4. AI models can analyze patterns across work efforts to provide insights

## Roadmap

Planned future features include:

1. Integration with issue tracking systems
2. Enhanced AI analysis of work efforts
3. Visualization of work effort networks
4. Automatic prioritization of tasks based on AI analysis
""")

        # Create work_efforts directory inside .AI-Setup using our structured function
        ai_work_dir, ai_template_path, _, _, _ = setup_work_efforts_structure(root_dir, create_dirs=True, in_ai_setup=True)

        # Ensure template file exists in .AI-Setup/work_efforts/templates
        create_template_if_missing(ai_template_path)

        print(f"✅ Created AI-Setup in: {root_dir}")
        return setup_folder

    def install_ai_setup(target_dirs):
        """Install AI-Setup in target directories."""
        # Create a temporary .AI-Setup in the current directory
        temp_dir = os.getcwd()
        setup_folder = create_ai_setup(temp_dir)

        # Copy to selected directories
        for directory in target_dirs:
            # Skip if directory doesn't exist
            if not os.path.exists(directory) or not os.path.isdir(directory):
                print(f"❌ Directory not found: {directory}")
                continue

            # Skip if already installed
            if is_ai_setup_installed(directory):
                print(f"⚠️ AI-Setup already installed in: {directory}")
                continue

            # Create .AI-Setup in target directory
            target_setup = os.path.join(directory, ".AI-Setup")
            if not os.path.exists(target_setup):
                os.makedirs(target_setup)

            # Copy all files from temporary .AI-Setup to target
            for item in os.listdir(setup_folder):
                source = os.path.join(setup_folder, item)
                target = os.path.join(target_setup, item)
                if os.path.isfile(source):
                    shutil.copy2(source, target)

            print(f"✅ Installed AI-Setup in: {directory}")

        # Clean up temporary .AI-Setup if it was created for this operation
        if os.path.dirname(setup_folder) == temp_dir:
            shutil.rmtree(setup_folder)

    # Fallback for the thought process simulator
    async def generate_content_with_ollama(description, model="phi3"):
        print("⚠️ Content generation not available: utils.thought_process module not found")
        return None

    def get_available_ollama_models():
        return ["phi3", "llama3", "mistral"]  # Default fallbacks


def setup_work_efforts_structure(base_dir=None, create_dirs=True, in_ai_setup=False):
    """
    Set up the work_efforts directory structure in the specified directory
    If no directory is specified, use the current directory
    If create_dirs is False, just return the paths without creating directories
    If in_ai_setup is True, create within the .AI-Setup folder

    Returns a tuple of (work_efforts_dir, template_path, active_path, completed_path, archived_path)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Define the work_efforts directory and its subdirectories
    if in_ai_setup:
        # Create inside .AI-Setup folder
        ai_setup_dir = os.path.join(base_dir, ".AI-Setup")
        if not os.path.exists(ai_setup_dir):
            if create_dirs:
                os.makedirs(ai_setup_dir)
                print(f"Created .AI-Setup directory: {ai_setup_dir}")
            else:
                print(f"Warning: .AI-Setup directory does not exist at {ai_setup_dir}")

        work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
    else:
        # Create at the root level (original behavior)
        work_efforts_dir = os.path.join(base_dir, "work_efforts")

    templates_dir = os.path.join(work_efforts_dir, "templates")
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")
    scripts_dir = os.path.join(work_efforts_dir, "scripts")

    if create_dirs:
        # Create all directories
        for directory in [work_efforts_dir, templates_dir, active_dir, completed_dir, archived_dir, scripts_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

        # Create a README in the work_efforts directory
        readme_path = os.path.join(work_efforts_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write("""# Work Efforts

This directory contains structured documentation for tracking tasks, features, and bug fixes.

## Structure

- **templates/** - Templates for work effort documents
- **active/** - Current, ongoing work efforts
- **completed/** - Successfully completed work efforts
- **archived/** - Deprecated or abandoned work efforts
- **scripts/** - Helper scripts for managing work efforts

## Usage

Create a new work effort:
```
ai-setup work_effort --title "Feature Name" --priority high
```

Or use the interactive mode:
```
ai-setup work_effort -i
```

For enhanced features like AI content generation:
```
cc-worke -i
```

List all work efforts:
```
ai-setup list
```
""")
            print(f"Created README at: {readme_path}")

        # Create an __init__.py file in the scripts directory
        init_py_path = os.path.join(scripts_dir, "__init__.py")
        if not os.path.exists(init_py_path):
            with open(init_py_path, "w") as f:
                f.write("# work_efforts scripts package")
            print(f"Created __init__.py at: {init_py_path}")

        # Create an __init__.py file in the work_efforts directory
        work_efforts_init_py_path = os.path.join(work_efforts_dir, "__init__.py")
        if not os.path.exists(work_efforts_init_py_path):
            with open(work_efforts_init_py_path, "w") as f:
                f.write("# work_efforts package")
            print(f"Created __init__.py at: {work_efforts_init_py_path}")

        # Copy script files from the package
        try:
            # Try to find the scripts in the installed package
            package_dir = os.path.dirname(os.path.abspath(__file__))
            package_scripts_dir = os.path.join(package_dir, "work_efforts", "scripts")

            # If not found, try looking in the development directory structure
            if not os.path.exists(package_scripts_dir):
                package_scripts_dir = os.path.join(os.path.dirname(package_dir), "work_efforts", "scripts")

            if os.path.exists(package_scripts_dir):
                for script_file in os.listdir(package_scripts_dir):
                    if script_file.endswith(".py"):
                        source = os.path.join(package_scripts_dir, script_file)
                        target = os.path.join(scripts_dir, script_file)
                        if os.path.isfile(source) and not os.path.exists(target):
                            shutil.copy2(source, target)
                            print(f"Copied script: {script_file} to {scripts_dir}")
        except Exception as e:
            print(f"Note: Could not copy script files: {str(e)}")

    # Define the template_path
    template_path = os.path.join(templates_dir, "work-effort-template.md")

    return work_efforts_dir, template_path, active_dir, completed_dir, archived_dir

def create_template_if_missing(template_path):
    """Copy the main template to the work efforts template directory if it doesn't exist"""
    if not os.path.exists(template_path):
        # First check if we have a template in the project root
        source_template = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "templates", "work-effort-template.md")

        if os.path.exists(source_template):
            # Copy the template from the project
            shutil.copy2(source_template, template_path)
            print(f"Copied template file to: {template_path}")
        else:
            # Create a default template if source not found
            template_content = """---
title: "{{title}}"
status: "{{status}}" # options: active, paused, completed
priority: "{{priority}}" # options: low, medium, high, critical
assignee: "{{assignee}}"
created: "{{created}}" # YYYY-MM-DD HH:mm
last_updated: "{{last_updated}}" # YYYY-MM-DD HH:mm
due_date: "{{due_date}}" # YYYY-MM-DD
tags: [feature, bugfix, refactor, documentation, testing, devops]
---

# {{title}}

## 🚩 Objectives
- Clearly define goals for this work effort.

## 🛠 Tasks
- [ ] Task 1
- [ ] Task 2

## 📝 Notes
- Context, links to relevant code, designs, references.

## 🐞 Issues Encountered
- Document issues and obstacles clearly.

## ✅ Outcomes & Results
- Explicitly log outcomes, lessons learned, and code changes.

## 📌 Linked Items
- [[Related Work Effort]]
- [[GitHub Issue #]]
- [[Pull Request #]]

## 📅 Timeline & Progress
- **Started**: {{created}}
- **Updated**: {{last_updated}}
- **Target Completion**: {{due_date}}
"""
            with open(template_path, "w") as f:
                f.write(template_content)
            print(f"Created template file at: {template_path}")

def validate_priority(priority):
    """Validate that priority is one of the allowed values"""
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority.lower() not in valid_priorities:
        print(f"Warning: '{priority}' is not a recognized priority level. Using 'medium' instead.")
        return "medium"
    return priority.lower()

def validate_date(date_str):
    """Validate the date format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Warning: Invalid date format. Using today's date ({today}) instead.")
        return today

def create_work_effort(title, assignee, priority, due_date, template_path, target_dir, content=None, create_in_root=False):
    """
    Create a new work effort file

    If create_in_root is True, create the file in the parent directory of target_dir
    If content is provided, use it to populate the objectives, tasks, and notes
    """
    try:
        # Validate inputs
        priority = validate_priority(priority)
        due_date = validate_date(due_date)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        filename_timestamp = datetime.now().strftime("%Y%m%d%H%M")

        # Generate a safe filename
        safe_title = ''.join(c if c.isalnum() or c == ' ' else '_' for c in title)
        filename = f"{filename_timestamp}_{safe_title.lower().replace(' ', '_')}.md"

        # Determine the target file path
        file_path = os.path.join(target_dir, filename) if not create_in_root else os.path.join(os.path.dirname(target_dir), filename)

        # Create target directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Read template file
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        # Replace template variables
        filled_content = template_content.replace("{{title}}", title)
        filled_content = filled_content.replace("{{status}}", "active")
        filled_content = filled_content.replace("{{priority}}", priority)
        filled_content = filled_content.replace("{{assignee}}", assignee)
        filled_content = filled_content.replace("{{created}}", timestamp)
        filled_content = filled_content.replace("{{last_updated}}", timestamp)
        filled_content = filled_content.replace("{{due_date}}", due_date)

        # If AI-generated content is provided, replace the placeholders
        if content and isinstance(content, dict):
            if "objectives" in content:
                filled_content = filled_content.replace("- Clearly define goals for this work effort.", content["objectives"])
            if "tasks" in content:
                filled_content = filled_content.replace("- [ ] Task 1\n- [ ] Task 2", content["tasks"])
            if "notes" in content:
                filled_content = filled_content.replace("- Context, links to relevant code, designs, references.", content["notes"])

        # Write new file
        with open(file_path, "w") as new_file:
            new_file.write(filled_content)

        print(f"🚀 New work effort created at: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error creating work effort: {str(e)}")
        return None

async def setup_selected_directories():
    """Use the interactive directory scanner to select and set up directories"""
    current_dir = os.getcwd()
    print(f"\n📍 Current directory: {current_dir}")
    print("Select directories to set up with AI-Setup:")

    # Use the interactive directory scanner
    selected_dirs = select_directories(current_dir)

    if not selected_dirs:
        print("No directories selected for setup.")
        return 1

    # Set up work efforts in each selected directory
    for directory in selected_dirs:
        dir_name = os.path.basename(directory)
        print(f"\n🔄 Setting up {dir_name}...")

        # Create work efforts structure
        work_efforts_dir, template_path, active_dir, _, _ = setup_work_efforts_structure(directory)
        create_template_if_missing(template_path)

        # Create default work effort
        create_work_effort(
            title="Getting Started",
            assignee="self",
            priority="medium",
            due_date=datetime.now().strftime("%Y-%m-%d"),
            template_path=template_path,
            target_dir=active_dir
        )

        # Install AI-Setup in the directory
        install_ai_setup([directory])

    print("\n✅ Setup completed for all selected directories")
    return 0

async def setup_ai_in_current_dir():
    """Set up AI and work efforts in the current directory"""
    current_dir = os.getcwd()
    print(f"\n📍 Checking current directory: {current_dir}")

    # Check if .AI-Setup already exists
    ai_setup_dir = os.path.join(current_dir, ".AI-Setup")
    ai_setup_exists = os.path.exists(ai_setup_dir) and os.path.isdir(ai_setup_dir)

    # Check if work_efforts already exists in the root
    work_efforts_dir = os.path.join(current_dir, "work_efforts")
    work_efforts_exists = os.path.exists(work_efforts_dir) and os.path.isdir(work_efforts_dir)

    # Check if work_efforts already exists inside .AI-Setup
    ai_setup_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts") if ai_setup_exists else None
    ai_setup_work_efforts_exists = ai_setup_work_efforts_dir and os.path.exists(ai_setup_work_efforts_dir) and os.path.isdir(ai_setup_work_efforts_dir)

    # If all exist, inform the user and exit
    if ai_setup_exists and work_efforts_exists and ai_setup_work_efforts_exists:
        print("\n✅ AI-Setup is already completely installed in this directory")
        print(f"- .AI-Setup folder exists at: {ai_setup_dir}")
        print(f"- Root work_efforts folder exists at: {work_efforts_dir}")
        print(f"- .AI-Setup/work_efforts folder exists at: {ai_setup_work_efforts_dir}")
        print("\nYou can use the following commands:")
        print("  ai-setup work_effort -i        - Create a new work effort interactively")
        print("  ai-setup list                  - List existing work efforts")
        return 0

    # Report what will be installed
    if not ai_setup_exists:
        print("\n🔍 No .AI-Setup folder found. Will install:")
        print("- .AI-Setup folder for AI contextual information")
        print("- .AI-Setup/work_efforts directory for tracking tasks")

    if not work_efforts_exists:
        print("- Root work_efforts directory for backward compatibility")

    if ai_setup_exists and not ai_setup_work_efforts_exists:
        print("\n🔍 Found existing .AI-Setup folder but no work_efforts directory inside it.")
        print("- Will install .AI-Setup/work_efforts directory for tracking tasks")

    print("\n📦 Installing missing components...")

    # Create the root work_efforts folder structure if needed (for backward compatibility)
    if not work_efforts_exists:
        root_work_efforts_dir, root_template_path, root_active_dir, _, _ = setup_work_efforts_structure(current_dir)
        create_template_if_missing(root_template_path)

        # Create a default work effort in the active directory
        file_path = create_work_effort(
            title="Getting Started",
            assignee="self",
            priority="medium",
            due_date=datetime.now().strftime("%Y-%m-%d"),
            template_path=root_template_path,
            target_dir=root_active_dir
        )
        print(f"✅ Root work efforts directory created at: {root_work_efforts_dir}")
        if file_path:
            print(f"✅ Default work effort created at: {file_path}")
    else:
        print(f"ℹ️ Using existing root work efforts directory at: {work_efforts_dir}")

    # Create the AI-Setup folder if needed
    if not ai_setup_exists:
        try:
            create_ai_setup(current_dir)
            print(f"✅ AI-Setup folder created at: {ai_setup_dir}")

            # Verify the work_efforts folder was created and create it if missing
            ai_setup_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
            if not os.path.exists(ai_setup_work_efforts_dir):
                _, template_path, _, _, _ = setup_work_efforts_structure(current_dir, in_ai_setup=True)
                create_template_if_missing(template_path)
                print(f"✅ Work efforts directory created inside .AI-Setup folder")
        except Exception as e:
            print(f"⚠️ AI setup encountered an issue: {str(e)}")
    else:
        print(f"ℹ️ Using existing AI-Setup folder at: {ai_setup_dir}")

        # If .AI-Setup exists but doesn't have work_efforts, create it
        if not ai_setup_work_efforts_exists:
            _, template_path, _, _, _ = setup_work_efforts_structure(current_dir, in_ai_setup=True)
            create_template_if_missing(template_path)
            print(f"✅ Work efforts directory created inside .AI-Setup folder")

    # Final verification
    ai_setup_work_efforts_dir = os.path.join(ai_setup_dir, "work_efforts")
    if not os.path.exists(ai_setup_work_efforts_dir):
        _, template_path, _, _, _ = setup_work_efforts_structure(current_dir, in_ai_setup=True)
        create_template_if_missing(template_path)
    else:
        # Ensure template exists
        ai_template_path = os.path.join(ai_setup_work_efforts_dir, "templates", "work-effort-template.md")
        if not os.path.exists(ai_template_path):
            create_template_if_missing(ai_template_path)

    print(f"\n✅ Setup completed in: {current_dir}")
    print("\nYou can now use the following commands:")
    print("  ai-setup work_effort -i        - Create a new work effort interactively")
    print("  ai-setup list                  - List existing work efforts")

    return 0

async def interactive_mode(template_path, active_dir):
    """Get user input with defaults to create a work effort"""
    print("\n📝 Create a New Work Effort")
    print("=========================")
    print("A work effort is a task or project you want to track with objectives, tasks, and notes.")
    print("You can create a new work effort by filling in the details below.")
    print("Press Enter to accept the default values shown in brackets.\n")

    # Get user input with defaults
    title_input = input("Title (name of your work effort) [Untitled]: ")
    title = title_input if title_input.strip() else "Untitled"

    assignee_input = input("Assignee (who is responsible) [self]: ")
    assignee = assignee_input if assignee_input.strip() else "self"

    print("\nPriority levels:")
    print("  low      - Can be done when time permits")
    print("  medium   - Important but not urgent")
    print("  high     - Urgent and should be done soon")
    print("  critical - Requires immediate attention")
    priority_input = input("Priority [medium]: ")
    priority = priority_input if priority_input.strip() else "medium"

    today = datetime.now().strftime("%Y-%m-%d")
    due_date_input = input(f"Due date (YYYY-MM-DD) [{today}]: ")
    due_date = due_date_input if due_date_input.strip() else today

    # Explicitly ask if user wants to use AI content generation
    print("\nAI Content Generation:")
    print("This feature can automatically generate objectives, tasks, and notes based on a description.")
    use_ai_input = input("Use AI to generate content? (y/N): [default: NO] ")
    use_ai = use_ai_input.lower() in ('y', 'yes')

    content = None
    if use_ai:
        # Ask for description for AI content generation
        print("\nProvide a description of what this work effort is about.")
        print("Example: \"Implement user authentication with email verification and password reset\"")
        description_input = input("\nDescription: ")

        if description_input.strip():
            available_models = get_available_ollama_models()

            if available_models:
                default_model = "phi3" if "phi3" in available_models else available_models[0]
                print(f"\nAvailable AI models: {', '.join(available_models)}")
                model_input = input(f"Choose a model [{default_model}]: ")
                model = model_input if model_input.strip() and model_input in available_models else default_model

                # Show timeout options
                print("\nTimeout is how long to wait for AI to generate content before aborting.")
                timeout_input = input(f"Timeout in seconds [30]: ")
                timeout = int(timeout_input) if timeout_input.strip().isdigit() else 30

                print("\nGenerating content... (Press Ctrl+C to abort)")
                content = await generate_content_with_ollama(description_input, model, timeout)
            else:
                print("⚠️ No Ollama models available. Using template defaults.")

    print("\nCreating work effort...")
    file_path = create_work_effort(title, assignee, priority, due_date, template_path, active_dir, content)

    print(f"\n✅ Work effort created successfully!")
    print(f"📂 Location: {file_path}")
    print("\nYou can now edit this file to add more details or track your progress.")

def list_work_efforts(work_efforts_dir):
    """List all work efforts in the work_efforts directory"""
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")

    print("\n📋 Work Efforts:")

    # Check if work_efforts directory exists
    if not os.path.exists(work_efforts_dir):
        print("❌ Work efforts directory not found. Run 'python cli.py' to set up.")
        return

    # List active work efforts
    print("\nActive Work Efforts:")
    if os.path.exists(active_dir):
        active_files = [f for f in os.listdir(active_dir) if f.endswith(".md")]
        if active_files:
            for file in sorted(active_files):
                print(f"  - {file}")
        else:
            print("  No active work efforts found.")
    else:
        print("  Active directory not found.")

    # List completed work efforts
    print("\nCompleted Work Efforts:")
    if os.path.exists(completed_dir):
        completed_files = [f for f in os.listdir(completed_dir) if f.endswith(".md")]
        if completed_files:
            for file in sorted(completed_files):
                print(f"  - {file}")
        else:
            print("  No completed work efforts found.")
    else:
        print("  Completed directory not found.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Setup and Work Effort Tracker")
    parser.add_argument("--title", default="Untitled", help="Title of the work effort (default: Untitled)")
    parser.add_argument("--assignee", default="self", help="Assignee of the work effort (default: self)")
    parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "critical"],
                        help="Priority of the work effort (default: medium)")
    parser.add_argument("--due-date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Due date in YYYY-MM-DD format (default: today)")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode (prompt for values)")
    parser.add_argument("--use-ai", action="store_true",
                        help="Use AI to generate content (OFF by default)")
    parser.add_argument("--description", help="Description of the work effort (for content generation with --use-ai)")
    parser.add_argument("--model", default="phi3", help="Ollama model to use for content generation (with --use-ai)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Timeout in seconds for AI content generation (default: 30)")
    parser.add_argument("-v", "--version", action="store_true", help="Show the version number and exit")
    parser.add_argument("command", nargs="?", help="Command to run (setup, work, list, select)")
    return parser.parse_args()

async def main():
    args = parse_arguments()

    # Handle version flag
    if args.version:
        print(f"Code Conductor version {VERSION}")
        return 0

    # If run with no args, automatically check for existing components and set up as needed
    if not args.command and not args.interactive:
        print("\n🤖 AI-Setup and Work Effort Tracker")
        print("==============================")
        # Skip the confirmation prompt and directly check for components
        await setup_ai_in_current_dir()
        return 0

    # Check for commands
    if args.command:
        if args.command.lower() in ['-h', '--help', 'help']:
            print("\nCode Conductor - AI Development Environment Setup Tool")
            print(f"Version: {VERSION}")
            print("\nCommands:")
            print("  code-conductor setup              - Set up AI assistance in the current directory")
            print("  code-conductor work_effort        - Create a new work effort")
            print("  code-conductor work_effort -i     - Create a new work effort interactively")
            print("  code-conductor list               - List existing work efforts")
            print("  code-conductor update-status      - Update the status of a work effort")
            print("  code-conductor help               - Show this help text")
            print("  code-conductor version            - Show the version number")
            print("\nFor more information, visit: https://github.com/ctavolazzi/code-conductor")
            return 0

        # Current directory check
        current_dir = os.getcwd()
        work_efforts_dir = os.path.join(current_dir, "work_efforts")

        if args.command.lower() in ['work_effort', 'work', 'create']:
            if not os.path.exists(work_efforts_dir):
                print(f"\n📋 Work Effort Management")
                print("======================")
                print(f"⚠️ Work efforts directory not found in {current_dir}")
                setup_first = input("Would you like to set up work efforts first? (y/n): ")
                if setup_first.lower() == 'y':
                    await setup_ai_in_current_dir()
                else:
                    return 1

            work_efforts_dir, template_path, active_dir, _, _ = setup_work_efforts_structure(current_dir)
            create_template_if_missing(template_path)

            # Interactive or command-line work creation
            if args.interactive:
                await interactive_mode(template_path, active_dir)
            else:
                print(f"\n📋 Creating Work Effort: {args.title}")
                print("======================")
                print(f"Assignee: {args.assignee}")
                print(f"Priority: {args.priority}")
                print(f"Due Date: {args.due_date}")

                # Check if we need to generate content
                content = None
                if args.description:
                    if args.use_ai:
                        print("\n🧠 Using AI to generate content based on your description...")
                        content = await generate_content_with_ollama(args.description, args.model, args.timeout)
                    else:
                        print("\nNote: To generate content with AI, you must use the --use-ai flag.")
                        print("Example: python cli.py work_effort --description \"Your description\" --use-ai")

                file_path = create_work_effort(
                    args.title,
                    args.assignee,
                    args.priority,
                    args.due_date,
                    template_path,
                    active_dir,
                    content
                )

                print(f"\n✅ Work effort created at: {file_path}")
            return 0

        elif args.command.lower() == 'list':
            if not os.path.exists(work_efforts_dir):
                print(f"⚠️ Work efforts directory not found in {current_dir}")
                return 1
            list_work_efforts(work_efforts_dir)
            return 0

        elif args.command.lower() == 'select':
            return await setup_selected_directories()

        elif args.command.lower() == 'setup':
            return await setup_ai_in_current_dir()

        else:
            print(f"Unknown command: {args.command}")
            print("Run 'python cli.py help' for usage information")
            return 1

    # Interactive mode without a specific command
    if args.interactive:
        current_dir = os.getcwd()
        work_efforts_dir = os.path.join(current_dir, "work_efforts")

        if not os.path.exists(work_efforts_dir):
            print(f"⚠️ Work efforts directory not found in {current_dir}")
            setup_first = input("Would you like to set up work efforts first? (y/n): ")
            if setup_first.lower() == 'y':
                await setup_ai_in_current_dir()
                return 0
            else:
                return 1

        work_efforts_dir, template_path, active_dir, _, _ = setup_work_efforts_structure(current_dir)
        create_template_if_missing(template_path)
        await interactive_mode(template_path, active_dir)
        return 0

def main_entry():
    """Entry point for console_scripts"""
    return asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())

def print_version():
    """Print the version number."""
    print(f"Code Conductor version {VERSION}")

def show_instructions():
    """Show usage instructions."""
    print("\nUsage Instructions:")
    print("  code-conductor work_effort -i        - Create a new work effort interactively")
    print("  code-conductor list                  - List existing work efforts")
    print("  code-conductor setup                 - Set up AI assistance in the current directory")
    print("  cc-worke -i                         - Create a work effort with enhanced features")
    print("\nFor more details, run: code-conductor help")