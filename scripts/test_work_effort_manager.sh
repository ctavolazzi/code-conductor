#!/bin/bash

# Test script for work effort manager
set -e  # Exit on error

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Work Effort Manager Implementation${NC}"

# Create a test directory
TEST_DIR=$(mktemp -d)
echo -e "${YELLOW}Test directory: ${TEST_DIR}${NC}"

# Clean up on exit
function cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Set up the test environment
echo -e "${YELLOW}Setting up test environment...${NC}"
mkdir -p "$TEST_DIR"
mkdir -p "$TEST_DIR/_AI-Setup"
mkdir -p "$TEST_DIR/work_efforts/active"
mkdir -p "$TEST_DIR/work_efforts/completed"
mkdir -p "$TEST_DIR/work_efforts/archived"
mkdir -p "$TEST_DIR/work_efforts/templates"

# Create a default template
cat > "$TEST_DIR/work_efforts/templates/default.md" << EOF
# {{title}}

**Status:** {{status}}
**Priority:** {{priority}}
**Assignee:** {{assignee}}
**Created:** {{created}}
**Last Updated:** {{last_updated}}
**Due Date:** {{due_date}}

## Objectives
- Clearly define goals for this work effort.

## Tasks
- [ ] Task 1
- [ ] Task 2

## Notes
- Context, links to relevant code, designs, references.
EOF

# Create the config.json file
cat > "$TEST_DIR/_AI-Setup/config.json" << EOF
{
  "work_efforts": {
    "use_manager": true,
    "manager_script": "$(pwd)/work_efforts/scripts/work_effort_manager.py",
    "runner_script": "$(pwd)/work_efforts/scripts/run_work_effort_manager.py",
    "project_dir": "$TEST_DIR",
    "auto_start": true,
    "default_settings": {
      "assignee": "Test User",
      "priority": "medium",
      "due_date": "+7d"
    },
    "directories": {
      "active": "work_efforts/active",
      "completed": "work_efforts/completed",
      "archived": "work_efforts/archived",
      "templates": "work_efforts/templates"
    },
    "work_effort_manager": {
        "enabled": true,
        "path": "$TEST_DIR/work_efforts",
        "work_effort_managers": {
            "default": {
                "name": "Default Work Effort Manager",
                "path": "$TEST_DIR/work_efforts"
            }
        },
        "default_work_manager": "default"
    }
  },
  "ai_settings": {
    "preferred_model": "phi3",
    "timeout": 60
  }
}
EOF

echo -e "${GREEN}Test environment setup complete.${NC}"

# Test the CLI
echo -e "${YELLOW}Testing CLI with work effort manager...${NC}"
cd "$TEST_DIR"

# Test creating a work effort
echo -e "${YELLOW}Creating a work effort...${NC}"
python "$(pwd)/cli.py" work --title "Test Work Effort" --assignee "Tester" --priority "high" --due-date "+3d"

# Check if the work effort was created
if ls "$TEST_DIR/work_efforts/active/"*"Test Work Effort"* 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Work effort created successfully${NC}"
else
    echo -e "${RED}✗ Work effort creation failed${NC}"
    exit 1
fi

# Test listing work efforts
echo -e "${YELLOW}Listing work efforts...${NC}"
python "$(pwd)/cli.py" list

# Test the work effort manager directly
echo -e "${YELLOW}Testing work effort manager directly...${NC}"
python "$(pwd)/work_efforts/scripts/run_work_effort_manager.py" --list-active

# Success
echo -e "${GREEN}All tests passed!${NC}"
exit 0