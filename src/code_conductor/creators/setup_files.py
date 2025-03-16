import os
import shutil

def create_ai_setup_folder(project_dir):
    """
    Create the .AI-Setup folder and its instruction files.

    Args:
        project_dir: Project directory path

    Returns:
        str: Path to the created .AI-Setup folder
    """
    # Define the AI setup folder
    setup_folder = os.path.join(project_dir, ".AI-Setup")

    # Create .AI-Setup folder
    os.makedirs(setup_folder, exist_ok=True)

    # Create instruction files
    create_instruction_files(setup_folder)

    print(f"✅ Created .AI-Setup folder with instruction files")
    return setup_folder

def create_instruction_files(setup_folder):
    """
    Create instruction files in the .AI-Setup folder.

    Args:
        setup_folder: Path to the .AI-Setup folder
    """
    files = {
        "AI-setup-instructions.md": """## **Cursor AI Project Initialization Prompt:**
### **Elite-Level Setup with TDD, Docstrings, and Comprehensive Logging**

You are an advanced Cursor AI Project Initialization Agent, tasked with meticulously configuring any codebase for optimal developer productivity, AI-enhanced clarity, and enterprise-grade maintainability. Execute each step methodically, autonomously, and thoroughly.

### **Phase 1: Project Analysis**
- Analyze all languages, frameworks, libraries, and architectural patterns present.
- Identify opportunities for applying standard, time-saving design patterns (Singleton, Factory, Observer, Decorator, Strategy) relevant to the codebase.
- Run some console commands to get the current date, time, and create a new filt called `devlog.md` in a 'devlog' folder at the root of the project.
- Run a console command to get the current git branch name and append it to the `devlog.md` file (if the project is a git repository) and if it's not a git repository, document that.
- Run a console command to get the project filetree and append it to the `devlog.md` file. Also, create a new file called `filetree.txt` at the root of the project and append the filetree to it.

---

## **Phase 2: Establish Optimized `.cursor/rules` Directory**
- Create a `.cursor/rules/` directory at the project's root.
- Clearly define rules in detailed Markdown (`.mdc`) files.

### **Sample Rule File (`typescript_react_rules.mdc`):**

```markdown
# File Patterns: **/*.tsx, **/*.ts

## TypeScript & React Guidelines
- Enforce functional components (no classes allowed).
- Explicitly prefer React Server Components (RSC).
- Utilize Suspense for client-side loading states.
- Enforce strict typing with interfaces; enums disallowed.

## Coding Practices
- Implement rigorous Test-Driven Development (TDD).
  - Write failing tests before implementing functionality.
  - Ensure minimum 80% unit test coverage.

- Include comprehensive docstrings for all functions and components.
  - Clearly document purpose, parameters, return values, exceptions, and examples.

- Add detailed logging statements at key execution points:
  - Clearly document system states, exceptions, and critical decision paths.
  - Use a consistent logging format (e.g., `[Timestamp][Module][Severity] Message`).

## Framework & Library Guidelines
- React with TypeScript and Tailwind CSS exclusively.
- Favor server components (RSC), with minimal `use client`.

## Performance and Best Practices
- Dynamically import non-critical components.
- Follow Next.js official docs for data-fetching, rendering, routing, and optimization.

@file ../tsconfig.json
@file ../tailwind.config.js
```

---

## **Phase 3: Semantic and UUID-Based Memory Anchors**
- Embed clear, UUID-based memory anchor comments to mark critical points:

```typescript
// [ANCHOR:550e8400-e29b-41d4-a716-446655440000]
// Reason: Critical authentication logic ensuring session consistency
function authenticateUser(token: string) { /* implementation */ }
```

---

## **Phase 4: Comprehensive `devlog.md` Documentation**
- Automatically maintain a detailed `devlog.md` file at the root, documenting:

```markdown
# Project Devlog

## Phase 1: Project Initialization (YYYY-MM-DD)
- Analyzed project structure, languages, and dependencies.
- Established `.cursor/rules` directory with comprehensive guidelines.

## Phase 2: TDD and Logging Implementation (YYYY-MM-DD)
- Integrated rigorous TDD process with minimum 80% coverage.
- Added comprehensive docstrings and logging to critical modules.

## Phase 2: Core Feature Development (YYYY-MM-DD)
- Developed initial features with test coverage and clear documentation.
- Established detailed logging strategy (info, warning, error).

## Phase 3: Optimization and Refinement (YYYY-MM-DD)
- Identified performance improvements using logs and testing metrics.
- Refactored for performance and scalability.

## Phase 4: Deployment and Continuous Integration (YYYY-MM-DD)
- Set up automated testing and logging pipelines in CI/CD workflows.

## Phase 4: Maintenance and Future Enhancements (YYYY-MM-DD)
- Logged common issues and implemented enhancements based on developer feedback and analytics.
```

---

## **Phase 5: Logging Strategy and Structure**
- Integrate structured logging at multiple log-levels (`INFO`, `WARN`, `ERROR`) across the entire codebase, especially:
  - API interactions, data flows, critical business logic
  - Error handling and edge cases
- Log entries must clearly indicate:
  - Timestamp
  - Function/component identifier
  - Input/output states
  - Execution duration (for performance-critical operations)

**Example Logging (Node.js):**
```typescript
import { Logger } from './utils/logger';

function fetchData(url: string): Promise<Data> {
  logger.info(`Fetching data from ${url}`);
  try {
    const response = await fetch(url);
    logger.info(`Fetch succeeded for ${url}`);
    return response.json();
  } catch (error) {
    logger.error(`Fetch failed for ${url}`, error);
    throw error;
  }
}
```

---

## **Phase 5: Rigorous Test-Driven Development (TDD)**
- Enforce mandatory TDD practices across the codebase.
- Every new feature or bug fix must start with writing failing tests first:

*Sample test (`feature.spec.tsx`):*

```typescript
describe('Auth Component', () => {
  test('renders login form initially', () => {
    render(<AuthComponent />);
    expect(screen.getByText('Log In')).toBeInTheDocument();
  });

  test('allows user login', async () => {
    render(<AuthComponent />);
    fireEvent.click(screen.getByText('Log In'));
    await waitFor(() => {
      expect(screen.getByText('Welcome')).toBeInTheDocument();
    });
  });
});
```

---

## **Phase 6: Time-Saving Design Patterns**
- Automatically identify and employ standard design patterns throughout the codebase, including:
  - **Singleton** for shared instances (logging, config).
  - **Factory Pattern** for object creation.
  - **Strategy Pattern** for interchangeable algorithms.
  - **Observer Pattern** for event-driven architectures.

*Example implementation snippet:*
```typescript
// Singleton Example
class Logger {
  private static instance: Logger;
  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  log(message: string): void {
    console.info(`[INFO]: ${message}`);
  }
}
```

---

## **Phase 6: Final Checks & Sanity Verification**
- Verify all configurations for consistency, clarity, and maintainability.
- Confirm that documentation, logging, testing, and rules are seamlessly integrated into the workflow.

---

## **Final Instructions**
Upon receiving this prompt, immediately execute all outlined steps precisely and comprehensively. Your goal is not only to set the standard but to surpass it—creating an impeccably structured project primed for rapid, scalable, reliable, and enjoyable development.

Make it happen, Cursor—let's redefine what's possible!""",

        "AI-setup-validation-instructions.md": """## 🚀 **Cursor AI Comprehensive Setup Verification Prompt**
### 📌 **Including Complete Work Efforts System Validation**

You are a meticulous Cursor AI Verification Agent tasked with rigorously confirming that the entire project setup—including rules, design patterns, TDD compliance, documentation, logging, devlog, CI/CD integration, and especially the comprehensive Obsidian-style Markdown Work Efforts system—has been executed flawlessly.

Immediately execute the following comprehensive testing procedure:

---

### 🗂 **Phase 1: Rules & Directory Structure Verification**

- ✅ **`.cursor/rules` directory**
  - Verify correct existence and location.
- ✅ **`.mdc` rule files**
  - Ensure each rule file exists, has correct formatting, and contains accurate glob-pattern rules.
- ✅ **UUID-based semantic anchors**
  - Confirm presence of properly formatted `[ANCHOR:UUID]` comments at critical points.

---

### 🧩 **Phase 2: Design Patterns Verification**

- ✅ **Singleton Pattern**
  - Validate Singleton pattern implementation and uniqueness of instances.
- ✅ **Factory Pattern**
  - Check for correctly implemented factories creating required objects.
- ✅ **Strategy Pattern**
  - Ensure strategies can be interchanged seamlessly.
- ✅ **Observer Pattern**
  - Confirm accurate event listener registrations and broadcasts.

---

### 🧪 **Phase 3: TDD Compliance & Tests**

- ✅ **Unit Test Coverage**
  - Verify minimum 80% code coverage.
- ✅ **Test-Driven Development**
  - Confirm tests are written first, then functionality.
- ✅ **Automated Test Suite**
  - Run tests (`npm test`) to ensure 100% passing.

---

### 📚 **Phase 4: Logging & Docstrings**

- ✅ **Logging Statements**
  - Ensure proper logging (`[Timestamp][Module][Severity] Message`) in all key paths, error handling, and API interactions.
- ✅ **Comprehensive Docstrings**
  - Validate thorough, accurate docstrings/documentation in all functions and components.

---

### 📖 **Phase 5: Devlog & Documentation**

- ✅ **`devlog.md`**
  - Confirm it exists and accurately documents every setup phase.
- ✅ **Documentation (`docs/` directory)**
  - Verify it includes complete architectural overviews, API docs, setup instructions, and guidelines.

---

### 📌 **Phase 6: Work Efforts System Verification**

- ✅ **Folder Structure (`work-efforts/`)**
  - Confirm exact presence and correctness of:
    ```
    work-efforts/
    ├── active/
    ├── completed/
    ├── templates/work-effort-template.md
    └── scripts/new_work_effort.py
    ```

- ✅ **Markdown Template (`work-effort-template.md`)**
  - Validate completeness and correctness of frontmatter (dates, statuses, priorities).
  - Ensure compatibility with Obsidian-style Markdown.
  - Confirm correct placeholders for template replacement.

- ✅ **Python Automation Script (`new_work_effort.py`)**
  - Test creation of new work efforts through the script:
    - Validate generated files in `active/` with correct timestamps.
    - Confirm template replacement accuracy (dates, titles, assignee, priority).

- ✅ **`.cursor/rules/work-efforts.mdc`**
  - Verify existence and accuracy:
    - Complete frontmatter enforcement
    - Timestamp consistency
    - Tagging and linking standards

---

### ⚙️ **Phase 7: CI/CD & Integration Checks**

- ✅ **CI/CD Pipeline**
  - Trigger pipeline, confirm builds, tests, and deployments run without issues.
- ✅ **Semantic & Structural Integrity**
  - Confirm directories/files exactly match defined guidelines.
- ✅ **Performance & Optimization**
  - Execute benchmarks and lint checks, ensuring optimal code efficiency without warnings or critical issues.

---

## 📊 **Automated Verification Results Report**

Upon completion, produce a clear, precise, actionable verification report (`verification-report.md`):

```markdown
# Cursor Project Setup Verification Report

## ✅ Summary of Results:
- [ ] `.cursor/rules` verification
- [ ] Design patterns implementation
- [ ] TDD compliance and test coverage
- [ ] Logging & docstrings accuracy
- [ ] Devlog completeness
- [ ] Documentation accuracy
- [ ] Work Efforts System (folders, templates, scripts)
- [ ] CI/CD and integration testing
- [ ] Performance and optimization

## 🚩 Issues Identified:
- Explicitly detail any issues or deviations found.
- Clearly state recommended resolutions.

## 🎯 Recommended Next Steps:
- Clearly prioritized action list for full compliance and optimization.

## 🛠 Final Remarks:
- Provide a concise summary of overall project quality and readiness.

Verification completed on: YYYY-MM-DD
```

---

**Execute these comprehensive tests immediately, document the results meticulously, and provide the final verification report.**
This is peak setup quality assurance—let's lock it in and launch! 🔥🚀""",

        "AI-work-effort-system.md": """## 🚀 **Cursor AI Work Effort Tracking Initialization Prompt**
### **Obsidian-style Markdown | Frontmatter Metadata | Python Automation**

You're an expert AI Project Initialization Agent. Immediately execute the following:

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

Get it, Cursor—let's make magic happen! 🌟✨"""
    }

    for filename, content in files.items():
        file_path = os.path.join(setup_folder, filename)
        with open(file_path, "w") as file:
            file.write(content)

def copy_ai_setup_to_dirs(source_dir, target_dirs):
    """
    Copy the .AI-Setup folder to target directories.

    Args:
        source_dir: Source directory with .AI-Setup folder
        target_dirs: List of target directory paths
    """
    source_setup = os.path.join(source_dir, ".AI-Setup")

    if not os.path.exists(source_setup):
        print(f"⚠️ Source .AI-Setup folder does not exist at: {source_setup}")
        return

    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"⚠️ Target directory does not exist, creating: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)

        target_setup = os.path.join(target_dir, ".AI-Setup")

        # Remove existing .AI-Setup if it exists
        if os.path.exists(target_setup):
            shutil.rmtree(target_setup)

        # Copy the .AI-Setup folder to the target directory
        shutil.copytree(source_setup, target_setup)
        print(f"✅ Installed .AI-Setup to: {target_dir}")

def create_devlog_folder(project_dir):
    """
    Create a devlog folder and initial devlog.md file.

    Args:
        project_dir: Project directory path
    """
    from datetime import datetime

    # Create devlog directory
    devlog_dir = os.path.join(project_dir, "devlog")
    os.makedirs(devlog_dir, exist_ok=True)

    # Create initial devlog.md file
    devlog_content = f"""# Project Devlog

## Phase 1: Initialization ({datetime.now().strftime('%Y-%m-%d')})
- Project initialized successfully.
- AI configuration setup.
"""

    devlog_path = os.path.join(devlog_dir, "devlog.md")
    with open(devlog_path, "w") as f:
        f.write(devlog_content)

    print(f"✅ Created devlog folder and initial devlog.md")

def create_docs_folder(project_dir):
    """
    Create a docs folder with a basic README.md.

    Args:
        project_dir: Project directory path
    """
    # Create docs directory
    docs_dir = os.path.join(project_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Create README.md in docs directory
    docs_readme_content = """# Project Documentation

This directory contains project documentation.

## Contents

- [Installation](./installation.md)
- [Usage](./usage.md)
- [API Reference](./api-reference.md)
"""

    docs_readme_path = os.path.join(docs_dir, "README.md")
    with open(docs_readme_path, "w") as f:
        f.write(docs_readme_content)

    print(f"✅ Created docs folder with README.md")