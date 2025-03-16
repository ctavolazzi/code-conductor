# Work Node Feature

## Overview

Work Node is a powerful knowledge management feature for Code Conductor that enables you to create specialized connection documents between related work efforts. Unlike traditional wiki links that create simple one-to-one connections, work nodes serve as semantic hubs that establish multi-directional relationships between documents, forming a rich knowledge graph.

## Key Features

- **Centralized Knowledge Nodes**: Create specialized documents that connect multiple related work efforts
- **Bidirectional Linking**: Automatically update all connected documents with links to the node
- **Relationship Discovery**: Automatically discover related documents based on content similarity
- **Knowledge Visualization**: Generate visualization data for exploring your document network
- **Flexible Categorization**: Organize nodes into different relationship types and categories

## Installation

The work node feature is included in Code Conductor v0.5.0 and above. No additional installation steps are required.

## Usage

### Creating Work Nodes Manually

```bash
# Create a node connecting specific documents
./create_work_node.py --title "Feature Planning" --documents doc1.md doc2.md doc3.md --category "planning"

# Add a description of the relationship
./create_work_node.py --title "Implementation Details" --documents impl1.md impl2.md --description "Technical implementation notes"
```

### Automatic Relationship Discovery

```bash
# Automatically discover and create nodes for related documents
./create_work_node.py --auto-discover

# Customize similarity threshold and limit the number of nodes
./create_work_node.py --auto-discover --min-similarity 0.7 --max-nodes 5
```

### Generating Visualizations

```bash
# Generate knowledge graph visualization data
./create_work_node.py --visualize

# Specify custom output location
./create_work_node.py --visualize --output knowledge_map.json
```

### Testing

```bash
# Run the test suite
./test_work_node.py
```

## Node Structure

Work nodes are stored as markdown files in the `.AI-Setup/work_effort/node/` directory with frontmatter metadata:

```markdown
---
title: "Feature Implementation"
created: "2025-03-17 13:22:00"
category: "implementation"
connected_document:
  - "[[doc1.md]]"
  - "[[doc2.md]]"
description: "Documents related to feature implementation"
---

# Feature Implementation

## Connected Document

- [[doc1.md]]
- [[doc2.md]]

## Description

Documents related to feature implementation

## Connection Map

```
    Feature Implementation
       |
       ├── doc1.md
       └── doc2.md
```
```

## Benefits

1. **Enhanced Knowledge Organization**: Create semantic networks of related documents
2. **Improved Navigation**: Easily move between related documents through central nodes
3. **Context Preservation**: Node documents provide context for how documents are related
4. **Structured Metadata**: Frontmatter fields enforce consistent relationship documentation
5. **Visualization**: Generate graph visualizations to explore your knowledge network

## Integration with Other Features

Work nodes integrate seamlessly with other Code Conductor features:

- **Obsidian-Style Linking**: Work nodes extend the basic wiki linking with semantic connection points
- **Work Effort Structure**: Nodes are stored in a dedicated `.AI-Setup/work_effort/node/` directory
- **Markdown Workflow**: Everything is stored as simple markdown files with yaml frontmatter

## Contributing

To contribute to the work node feature:

1. Submit issues for bugs or enhancement ideas
2. Follow the [development workflow](.AI-Setup/work_efforts/active/202503171244_work_node_creation_workflow.md)
3. Add tests for any new functionality
4. Ensure all tests pass before submitting changes

## License

This feature is part of Code Conductor and is licensed under MIT license terms.