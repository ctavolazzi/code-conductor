# AI Setup Validation Instructions - Johnny Decimal System

This file contains instructions for validating the AI setup in this project.
It helps AI assistants understand how to verify that everything is working correctly.

## Validation Steps

1. Check that the `.AI_setup` folder exists and contains all required files
2. Verify that the `work_efforts` directory structure is properly set up with Johnny Decimal categories
3. Confirm that the cc-ai commands are working as expected
4. Validate that work efforts can be created and listed properly

## Required Components

### 1. `.AI_setup` folder with:
   - INSTRUCTIONS.md
   - AI-setup-validation-instructions.md
   - AI-work-effort-system.md
   - AI-setup-instructions.md

### 2. `work_efforts` directory with Johnny Decimal structure:
   ```
   work_efforts/
   ├── 00.00_work_efforts_index.md
   ├── 00_system/
   │   └── 00.00_index.md
   ├── 10_development/
   │   └── 00.00_index.md
   ├── 20_debugging/
   │   └── 00.00_index.md
   ├── 30_documentation/
   │   └── 00.00_index.md
   ├── 40_testing/
   │   └── 00.00_index.md
   ├── 50_maintenance/
   │   └── 00.00_index.md
   ├── templates/
   │   └── work-effort-template.md
   ├── archived/
   └── scripts/
   ```

## Testing Commands

Test that the AI setup is working correctly by running:

### Basic Setup Test
```bash
cc-ai setup  # or cc-ai s
```
Should create the Johnny Decimal directory structure.

### Work Effort Creation Test
```bash
cc-ai work_effort -i  # or cc-ai wei
```
Should prompt for category selection and create a work effort in the appropriate category.

### List Test
```bash
cc-ai list  # or cc-ai l
```
Should show work efforts organized by status (active, paused, completed, cancelled).

## Verification Checklist

- [ ] **Directory Structure**: Johnny Decimal categories (00_system through 50_maintenance) exist
- [ ] **Index Files**: Each category has a 00.00_index.md file
- [ ] **Main Index**: 00.00_work_efforts_index.md exists at root of work_efforts
- [ ] **Templates**: work-effort-template.md exists in templates/ directory
- [ ] **Commands Work**: cc-ai setup, cc-ai wei, cc-ai l all function properly
- [ ] **Status Parsing**: List command correctly parses frontmatter status
- [ ] **Category Selection**: Interactive mode allows category selection
- [ ] **File Creation**: Work efforts are created in correct category directories
- [ ] **Frontmatter**: Created work efforts have proper frontmatter with status, priority, etc.

## Expected Behavior

### When setting up (`cc-ai s`):
- Creates work_efforts directory if it doesn't exist
- Creates all 6 Johnny Decimal category directories
- Creates index files for each category
- Creates templates, archived, and scripts directories
- Creates a default "Getting Started" work effort in 00_system

### When creating work efforts (`cc-ai wei`):
- Prompts for title, assignee, priority, due date, and category
- Creates file with timestamp-based filename
- Places file in selected category directory
- Populates frontmatter with provided values and "active" status

### When listing work efforts (`cc-ai l`):
- Scans all category directories for .md files (excluding index files)
- Parses frontmatter to extract status
- Groups work efforts by status (Active, Paused, Completed, Cancelled)
- Shows category name for each work effort
- Displays total count

## Common Issues and Solutions

1. **No work efforts found**: Ensure work efforts exist and have proper frontmatter
2. **Wrong category**: Check that work efforts are in category directories, not root
3. **Status not parsed**: Verify frontmatter has proper `status:` field
4. **Commands not found**: Ensure cc-ai is installed globally with `pip install -e .`

## Troubleshooting

If validation fails:
1. Check that all required directories exist
2. Verify file permissions allow read/write
3. Ensure frontmatter is properly formatted with `---` delimiters
4. Check that status values are one of: active, paused, completed, cancelled
5. Verify category directories are named correctly (XX_category format)