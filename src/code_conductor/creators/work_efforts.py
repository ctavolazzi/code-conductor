import os

def create_work_efforts_structure(project_dir):
    """
    Create the work_efforts folder structure in the project directory.

    Args:
        project_dir: Project directory path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Define paths
        work_efforts_dir = os.path.join(project_dir, "work_efforts")
        active_dir = os.path.join(work_efforts_dir, "active")
        completed_dir = os.path.join(work_efforts_dir, "completed")
        templates_dir = os.path.join(work_efforts_dir, "templates")
        scripts_dir = os.path.join(work_efforts_dir, "scripts")

        # Create directories
        os.makedirs(active_dir, exist_ok=True)
        os.makedirs(completed_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(scripts_dir, exist_ok=True)

        # Create template file
        create_template_file(templates_dir)

        # Create script file
        create_script_file(scripts_dir)

        # Create work efforts rule
        create_cursor_rule(project_dir)

        print(f"✅ Created work_efforts folder structure")
        return True
    except Exception as e:
        print(f"❌ Failed to create work_efforts structure: {str(e)}")
        return False

def create_template_file(templates_dir):
    """
    Create the work effort template file.

    Args:
        templates_dir: Templates directory path
    """
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

    template_path = os.path.join(templates_dir, "work-effort-template.md")
    with open(template_path, "w") as f:
        f.write(template_content)

def create_script_file(scripts_dir):
    """
    Create the work effort script file.

    Args:
        scripts_dir: Scripts directory path
    """
    script_content = """import os
from datetime import datetime

TEMPLATE_PATH = "../templates/work-effort-template.md"
ACTIVE_PATH = "../active/"

def create_work_effort(title, assignee, priority, due_date):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename_timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"{filename_timestamp}_{title.lower().replace(' ', '_')}.md"
    file_path = os.path.join(ACTIVE_PATH, filename)

    with open(TEMPLATE_PATH, "r") as template_file:
        content = template_file.read()

    content = content.replace("{{title}}", title)
    content = content.replace("{{status}}", "active")
    content = content.replace("{{priority}}", priority)
    content = content.replace("{{assignee}}", assignee)
    content = content.replace("{{created}}", timestamp)
    content = content.replace("{{last_updated}}", timestamp)
    content = content.replace("{{due_date}}", due_date)

    with open(file_path, "w") as new_file:
        new_file.write(content)

    print(f"🚀 New work effort created at: {file_path}")

if __name__ == "__main__":
    print("Create a New Work Effort:")
    title = input("Enter title: ")
    assignee = input("Enter assignee: ")
    priority = input("Enter priority (low, medium, high, critical): ")
    due_date = input("Enter due date (YYYY-MM-DD): ")

    create_work_effort(title, assignee, priority, due_date)
"""

    script_path = os.path.join(scripts_dir, "new_work_effort.py")
    with open(script_path, "w") as f:
        f.write(script_content)

def create_cursor_rule(project_dir):
    """
    Create a Cursor rule for work efforts.

    Args:
        project_dir: Project directory path
    """
    # Create .cursor/rules directory
    cursor_rules_dir = os.path.join(project_dir, ".cursor", "rules")
    os.makedirs(cursor_rules_dir, exist_ok=True)

    # Create rule file
    rule_content = """# Work Efforts Management
# Apply rules to work-efforts/**/*.md

- Enforce complete frontmatter on every file creation and update.
- Include timestamps (created, last_updated, due_date) in consistent format (YYYY-MM-DD HH:mm).
- Require consistent use of tags for categorization (feature, bugfix, refactor, documentation, testing, devops).
- Ensure clear linking between related work efforts and GitHub Issues/Pull Requests.
"""

    rule_path = os.path.join(cursor_rules_dir, "work-efforts.mdc")
    with open(rule_path, "w") as f:
        f.write(rule_content)

def update_readme_with_work_efforts(project_dir):
    """
    Update the README.md with information about the work efforts system.

    Args:
        project_dir: Project directory path
    """
    readme_path = os.path.join(project_dir, "README.md")

    if not os.path.exists(readme_path):
        return

    # Read existing content
    with open(readme_path, "r") as f:
        content = f.read()

    # Add work efforts section if it doesn't exist
    if "Work Efforts Tracking System" not in content:
        work_efforts_section = """
## Work Efforts Tracking System

Manage development clearly and effectively with this Obsidian-inspired Work Efforts system.

### Creating New Work Efforts

Navigate to `work_efforts/scripts/` and run:
```bash
python new_work_effort.py
```

### Folder Structure

- `active/`: Current ongoing work efforts.
- `completed/`: Finished or archived work efforts.
- `templates/`: Markdown templates used to create new work efforts.
- `scripts/`: Automation scripts for ease of use.

This ensures consistent formatting, tracking, and visibility into your project's development workflow.
"""

        # Append to content or insert before Usage section
        if "## Usage" in content:
            content = content.replace("## Usage", work_efforts_section + "\n\n## Usage")
        else:
            content += "\n" + work_efforts_section

        # Write updated content
        with open(readme_path, "w") as f:
            f.write(content)