# Work Effort: Johnny Decimal Work Efforts Reorganization

## Status: In Progress
**Started:** 2025-01-27
**Last Updated:** 2025-01-27

## Objective
Reorganize the entire work efforts system using the Johnny Decimal methodology with proper Obsidian markdown formatting and index files. Also update the CLI tool to apply this structure to new projects.

## Tasks
1. [ ] Analyze current work efforts structure
2. [ ] Design Johnny Decimal categories:
   - [ ] 00_system (system/infrastructure)
   - [ ] 10_development (development tasks)
   - [ ] 20_debugging (debugging specific - user requested)
   - [ ] 30_documentation (docs/guides)
   - [ ] 40_testing (testing efforts)
   - [ ] 50_maintenance (maintenance tasks)
3. [ ] Create new directory structure with .00 index files
4. [ ] Create Obsidian-style index.md files for each category
5. [ ] Migrate existing work efforts to appropriate categories
6. [ ] Update CLI tool (cli.py) to generate Johnny Decimal structure
7. [ ] Update work effort templates to support Johnny Decimal
8. [ ] Test new structure functionality

## Progress
- Created devlog for tracking changes
- Created this work effort document
- Ready to begin analysis and implementation

## Next Steps
1. Analyze existing work efforts to understand categorization needs
2. Create the 00-90 category structure
3. Begin migration of existing work efforts

## Notes
- User specifically requested debugging category (20_debugging)
- Index files must be .00 format (00.00_index.md, 10.00_index.md, etc.)
- Need proper Obsidian markdown cross-references
- System must be applied to new project setups via CLI tool