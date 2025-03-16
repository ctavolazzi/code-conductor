# Development Log

## 2025-03-16: Obsidian-Style Document Linking Implementation Plan

### Feature: Obsidian-Style Wiki Links Between Work Efforts

**Goal:** Implement a system to allow work efforts to link to each other using Obsidian-style wiki links.

#### Plan:

1. **Modify Work Effort Model**
   - Add `related_efforts` field to the `WorkEffort` class
   - Update constructor, getters, and setters to handle this new field
   - Update JSON serialization methods

2. **Update Markdown Conversion**
   - Modify `to_markdown()` to include related_efforts in frontmatter
   - Update `from_markdown()` to parse related_efforts from frontmatter
   - Add support for detecting and parsing [[wiki-style]] links in document content

3. **Update Templates**
   - Update work effort template to include related_efforts field in frontmatter
   - Add example wiki links in the template

4. **Documentation**
   - Update documentation to explain how to use the linking feature
   - Document syntax and best practices

5. **Enhancement Tools**
   - Create utility functions to find related work efforts
   - Add functionality to suggest relevant links

This implementation will enable both structured linking (in frontmatter) and unstructured linking (via wiki-style links within document content), creating a networked structure of work efforts and enhancing navigation and context.

Work is tracked in [[202503160633_obsidian_style_document_linking.md]]

## 2025-03-16: Work Effort Naming Conventions Documentation

**Goal:** Document different possible naming conventions for work efforts and create examples of each.

#### Completed:

1. **Created Example Work Efforts**
   - Timestamp-based: Current approach (`202503160637_work_effort_naming_conventions.md`)
   - Sequential numbered: Simple ordered approach (`001_sequential_naming_example.md`)
   - UUID-based: Technical unique identifiers (`550e8400-e29b-41d4-a716-446655440000.md`)
   - Semantic/categorical: Type-prefixed naming (`feature_obsidian_linking.md`)

2. **Documented Comparison**
   - Created detailed comparison of pros and cons for each approach
   - Added recommendations for different team sizes and workflows
   - Used the new Obsidian-style linking to connect all related work efforts

This documentation provides teams with options for standardizing their work effort naming based on their specific needs and workflows.

Work is tracked in [[202503160637_work_effort_naming_conventions.md]]

## 2025-03-16: Work Effort Consolidation

**Goal:** Consolidate all work efforts into a single location for better organization and accessibility.

#### Completed:

1. **Centralized Work Effort Location**
   - Moved all work efforts from various locations to `.AI-Setup/work_efforts`
   - Preserved directory structure (active, archived, completed, etc.)
   - Maintained all Python modules, scripts, and support files

2. **Cleaned Up Duplicate Work Efforts**
   - Removed redundant work effort directories from the codebase
   - Resolved conflicts with duplicate file names
   - Preserved all unique work effort content

3. **Established Standard Location**
   - All work efforts now stored in `.AI-Setup/work_efforts`
   - Consistent structure makes scripts and commands more reliable
   - Better organization improves findability and reduces confusion

This consolidation simplifies maintenance, reduces duplication, and creates a consistent experience for all team members. The centralized location also allows for better integration with Obsidian-style linking by providing a known base path for all work effort documents.

Works with: [[202503160637_work_effort_naming_conventions.md]] and [[202503160633_obsidian_style_document_linking.md]]