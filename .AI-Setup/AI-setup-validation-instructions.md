## 🚀 **Cursor AI Comprehensive Setup Verification Prompt**
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
This is peak setup quality assurance—let's lock it in and launch! 🔥🚀