# AI Setup Validation Instructions

This file contains instructions for validating the AI setup in this project.
It helps AI assistants understand how to verify that everything is working correctly.

## Validation Steps

1. Check that the `.AI_setup` folder exists and contains all required files
2. Verify that the `work_efforts` directory structure is properly set up
3. Confirm that the AI_setup commands are working as expected

## Required Components

1. `.AI_setup` folder with:
   - INSTRUCTIONS.md
   - AI_setup_validation_instructions.md
   - AI_work_effort_system.md
   - AI_setup_instructions.md

2. `work_efforts` directory with:
   - templates/
   - active/
   - completed/
   - archived/

## Testing Commands

You can test that the AI setup is working correctly by running:

```
ai_setup list
```

This should show any existing work efforts or indicate that none exist yet.
