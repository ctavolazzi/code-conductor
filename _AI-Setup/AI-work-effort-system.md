## 🚀 **Cursor AI Work Effort Tracking Initialization Prompt**
### **Obsidian-style Markdown | Frontmatter Metadata | Python Automation**

You’re an expert AI Project Initialization Agent. Immediately execute the following:

## 📂 **Step 1: Create "Work Efforts" Folder Structure**

- At the root of your repository, create this exact folder structure:

```
work-efforts/
├── active/
├── completed/
├── templates/
│   └── work-effort-template.md
└── scripts/
    └── new_work_effort.py
```

---

## 📋 **Step 2: Generate Obsidian-Style Markdown Template**

- Automatically populate `templates/work-effort-template.md` with this content:

```markdown
---
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
```

---

## 🐍 **Step 3: Generate Python Automation Script**

- Populate `scripts/new_work_effort.py` with this fully functioning automation script:

```python
import os
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
```

- This script instantly generates a new, fully-formed Work Effort Markdown file based on your template, pre-filled with all necessary metadata and timestamping.

---

## 🛡 **Step 4: Define Rules in `.cursor/rules/work-efforts.mdc`**

- Create and populate `.cursor/rules/work-efforts.mdc` with:

```markdown
# Work Efforts Management
# Apply rules to work-efforts/**/*.md

- Enforce complete frontmatter on every file creation and update.
- Include timestamps (created, last_updated, due_date) in consistent format (YYYY-MM-DD HH:mm).
- Require consistent use of tags for categorization (feature, bugfix, refactor, documentation, testing, devops).
- Ensure clear linking between related work efforts and GitHub Issues/Pull Requests.
```

---

## 📖 **Step 5: Add Usage Documentation in README.md**

- Clearly document how to use the system:

```markdown
## Work Efforts Tracking System

Manage development clearly and effectively with this Obsidian-inspired Work Efforts system.

### Creating New Work Efforts

Navigate to `scripts/` and run:
```bash
python new_work_effort.py
```

### Folder Structure

- `active/`: Current ongoing work efforts.
- `completed/`: Finished or archived work efforts.
- `templates/`: Markdown templates used to create new work efforts.
- `scripts/`: Automation scripts for ease of use.

This ensures consistent formatting, tracking, and visibility into your project's development workflow.
```

---

## ✅ **Final Verification Checklist**

After execution, verify:

- [ ] Directory structure exists exactly as specified.
- [ ] Markdown template is fully complete, accurate, and Obsidian-compatible.
- [ ] Python automation script works seamlessly, creating properly formatted Markdown files.
- [ ] `.cursor/rules` rules are properly implemented and enforced.

---

## 🚀 **Final Instructions**

Execute this immediately, thoroughly document the process, and ensure 100% compliance with all requirements above. This setup must achieve peak clarity, comprehensive tracking, and easy management of your development work efforts.

Get it, Cursor—let’s make magic happen! 🌟✨