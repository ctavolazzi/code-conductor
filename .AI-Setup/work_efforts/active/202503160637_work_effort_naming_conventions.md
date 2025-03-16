---
title: "Work Effort Naming Conventions"
status: "active" # options: active, paused, completed
priority: "medium" # options: low, medium, high, critical
assignee: "self"
created: "2025-03-16 06:37" # YYYY-MM-DD HH:mm
last_updated: "2025-03-16 06:42" # YYYY-MM-DD HH:mm
due_date: "2025-03-23" # YYYY-MM-DD
tags: [documentation, standards, organization]
related_efforts: [[001_sequential_naming_example, 550e8400-e29b-41d4-a716-446655440000, feature_obsidian_linking]]
---

# Work Effort Naming Conventions

## 🚩 Objectives
- Document different naming conventions for work efforts
- Create examples of each convention
- Analyze pros and cons of each approach
- Recommend best practices for different use cases

## 🛠 Tasks
- [x] Create timestamp-based naming example (current approach)
- [x] Create sequential numbered naming example
- [x] Create UUID-based naming example
- [x] Create semantic/categorical naming example
- [x] Document pros and cons of each approach

## 📝 Notes
- Different naming conventions may be appropriate for different teams and workflows
- Consistency is more important than the specific convention chosen
- Consider searchability, sortability, and human readability
- Some naming conventions may work better with Obsidian-style linking than others

## 🐞 Issues Encountered
- None yet

## ✅ Outcomes & Results
- Created example work efforts with different naming conventions:
  - Timestamp-based: `202503160637_work_effort_naming_conventions.md`
  - Sequential: `001_sequential_naming_example.md`
  - UUID-based: `550e8400-e29b-41d4-a716-446655440000.md`
  - Semantic/categorical: `feature_obsidian_linking.md`

### Naming Convention Comparison

| Convention | Example | Pros | Cons | Best For |
|------------|---------|------|------|----------|
| Timestamp-based | `202503160637_work_effort_naming_conventions.md` | Automatic uniqueness, sortable by creation date, includes timing info | Long filenames, timestamps not human-friendly | Default approach, teams with parallel work streams |
| Sequential | `001_sequential_naming_example.md` | Simple, orderly, easy to reference | Manual tracking needed, no timestamp info | Small projects, sequential/ordered workflows |
| UUID-based | `550e8400-e29b-41d4-a716-446655440000.md` | Guaranteed uniqueness, works across systems | Not human-readable, difficult to reference | Automated systems, database integration, distributed teams |
| Semantic/Categorical | `feature_obsidian_linking.md` | Clearly communicates purpose, easy to reference | No uniqueness guarantee, limited categories | Project categorization, domain-specific organization |

### Recommendations

1. **For Most Teams**: Use timestamp-based naming with descriptive suffixes
2. **For Small, Ordered Projects**: Consider sequential numbering
3. **For Large, Distributed Systems**: Consider UUID with good metadata/tagging
4. **For Topic/Category Organization**: Use semantic prefixes combined with timestamps

## 📌 Linked Items
- [[202503160633_obsidian_style_document_linking]]
- [[001_sequential_naming_example]]
- [[550e8400-e29b-41d4-a716-446655440000]]
- [[feature_obsidian_linking]]
- [[templates/work-effort-template.md]]

## 📅 Timeline & Progress
- **Started**: 2025-03-16 06:37
- **Updated**: 2025-03-16 06:42
- **Target Completion**: 2025-03-23