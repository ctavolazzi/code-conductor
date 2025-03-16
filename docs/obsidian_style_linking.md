# Obsidian-Style Document Linking

Code Conductor now supports Obsidian-style wiki links for connecting related work efforts.

## Overview

Obsidian-style document linking allows you to:

1. Create connections between related work efforts
2. Navigate between documents using wiki-style links
3. Build a knowledge graph of your project's work
4. Automatically maintain relationships between documents

## Link Syntax

### Basic Links

The basic syntax uses double square brackets:

```markdown
[[document_name]]
```

When rendered in compatible markdown viewers like Obsidian, these become clickable links.

### Link Examples

```markdown
See [[authentication_system]] for related work.

This builds on work from [[2023-12-05-database-schema]].

Related efforts: [[user_profile]], [[login_page]], [[password_reset]].
```

## Frontmatter Integration

Work efforts can specify related documents in their frontmatter:

```yaml
---
title: "User Authentication System"
status: "in-progress"
priority: "high"
related_efforts:
  - [[user_profile]]
  - [[login_page]]
  - [[session_management]]
---
```

## Benefits

### Knowledge Networking

- Create a web of connected ideas and implementations
- Discover relationships between different parts of your project
- Navigate through your project documentation intuitively

### Workflow Improvements

- Quickly find related documents when working on a feature
- Reference previous work without copying/pasting
- Build on existing knowledge rather than reinventing

### Documentation Enhancement

- Make documentation more navigable
- Create a more coherent project narrative
- Help newcomers understand relationships between components

## Implementation Details

### How Links Are Processed

1. When creating or updating a work effort, you can include `[[document]]` links in the content
2. These links are preserved in the markdown files
3. The system also allows adding a `related_efforts` field in the frontmatter
4. Links can reference documents by name, with or without the file extension

### Automatic Link Generation

You can use the `consolidate_work_efforts.py` script with the `--add-links` option to automatically:

1. Scan all work effort documents
2. Find mentions of document titles in other documents
3. Add appropriate Obsidian-style links
4. Update frontmatter with related_efforts lists

```bash
python consolidate_work_efforts.py --add-links
```

## Integration with Obsidian

For the best experience:

1. Open your `.AI-Setup/work_efforts` directory as an Obsidian vault
2. Use Obsidian to navigate between linked documents
3. Leverage Obsidian's graph view to visualize your project's knowledge network
4. Continue adding links as you develop new work efforts

## Future Enhancements

Planned improvements include:

- Automatic link suggestions based on content similarity
- Export of knowledge graphs for visualization
- Enhanced templates with built-in link sections
- Integration with project management tools