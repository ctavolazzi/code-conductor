#!/bin/bash

# Test script for work effort manager configuration and integration
set -e  # Exit on error

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting work effort manager configuration tests...${NC}"

# Record the current directory
CURRENT_DIR=$(pwd)
PROJECT_ROOT=$(dirname "$CURRENT_DIR")
TEST_DIR=$(mktemp -d)

echo -e "${YELLOW}Test directory: ${TEST_DIR}${NC}"

# Initialize test status
TEST_STATUS=0

# Function to run a command and check its success
run_test() {
    local cmd="$1"
    local description="$2"

    echo -e "${YELLOW}Running test: ${description}${NC}"

    if eval "$cmd"; then
        echo -e "${GREEN}✓ Test Passed: ${description}${NC}"
    else
        echo -e "${RED}✗ Test Failed: ${description}${NC}"
        TEST_STATUS=1
    fi
}

# Setup test environment
setup_test_env() {
    echo -e "${YELLOW}Setting up test environment...${NC}"

    # Create necessary directories
    mkdir -p "$TEST_DIR/_AI-Setup"
    mkdir -p "$TEST_DIR/work_efforts/active"
    mkdir -p "$TEST_DIR/work_efforts/completed"
    mkdir -p "$TEST_DIR/work_efforts/archived"
    mkdir -p "$TEST_DIR/work_efforts/templates"

    # Create a sample template
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

    # Create config.json in _AI-Setup
    cat > "$TEST_DIR/_AI-Setup/config.json" << EOF
{
  "work_efforts": {
    "use_manager": true,
    "manager_script": "$TEST_DIR/work_efforts/scripts/work_effort_manager.py",
    "runner_script": "$TEST_DIR/work_efforts/scripts/run_work_effort_manager.py",
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
    }
  }
}
EOF

    echo -e "${GREEN}Test environment setup complete.${NC}"
}

# Run Python unit tests
run_python_tests() {
    echo -e "${YELLOW}Running Python unit tests...${NC}"
    cd "$PROJECT_ROOT"
    python -m unittest tests/test_work_effort_manager_config.py
}

# Test CLI command directly
test_cli_command() {
    echo -e "${YELLOW}Testing CLI command directly...${NC}"
    cd "$TEST_DIR"

    # Use the CLI to create a work effort
    if python "$PROJECT_ROOT/cli.py" work --title "Test CLI Work Effort" --assignee "CLI Tester" --priority "high" --due-date "+3d"; then
        # Check if the work effort was created in the active directory
        if ls "$TEST_DIR/work_efforts/active/"*"Test CLI Work Effort"* 1> /dev/null 2>&1; then
            echo -e "${GREEN}✓ CLI command successfully created work effort${NC}"
        else
            echo -e "${RED}✗ CLI command did not create work effort file${NC}"
            TEST_STATUS=1
        fi
    else
        echo -e "${RED}✗ CLI command failed${NC}"
        TEST_STATUS=1
    fi
}

# Verify that the config.json is loaded
test_config_loading() {
    echo -e "${YELLOW}Testing config.json loading...${NC}"
    cd "$TEST_DIR"

    # Create a simple test script
    cat > test_config_loading.py << EOF
import os
import sys
import json

# Add the project root to sys.path
sys.path.insert(0, "$PROJECT_ROOT")

# Import the load_config function
from cli import load_config

# Call the function
config = load_config()

# Print the config for verification
print(json.dumps(config, indent=2))

# Check if the config is loaded correctly
if config and config.get('work_efforts', {}).get('use_manager') == True:
    print("Config loaded successfully!")
    exit(0)
else:
    print("Config loading failed!")
    exit(1)
EOF

    # Run the test script
    run_test "python test_config_loading.py" "Loading config.json from CLI module"
}

# Test the run_work_effort_manager.py script
test_run_work_effort_manager() {
    echo -e "${YELLOW}Testing run_work_effort_manager.py script...${NC}"
    cd "$TEST_DIR"

    # Create a simple test script to check if the script loads config correctly
    cat > test_run_work_effort_manager.py << EOF
import os
import sys
import json

# Add the project scripts to sys.path
sys.path.insert(0, "$PROJECT_ROOT/work_efforts/scripts")

# Import the function
from run_work_effort_manager import load_config_from_ai_setup

# Call the function
config = load_config_from_ai_setup()

# Print the config for verification
print(json.dumps(config, indent=2))

# Check if the config is loaded correctly
if config and config.get('work_efforts', {}).get('use_manager') == True:
    print("Config loaded successfully by run_work_effort_manager!")
    exit(0)
else:
    print("Config loading failed in run_work_effort_manager!")
    exit(1)
EOF

    # Run the test script
    run_test "python test_run_work_effort_manager.py" "Loading config.json from run_work_effort_manager module"
}

# Clean up test environment
cleanup() {
    echo -e "${YELLOW}Cleaning up test environment...${NC}"
    rm -rf "$TEST_DIR"
    echo -e "${GREEN}Cleanup complete.${NC}"
}

# Run the tests
setup_test_env
run_python_tests
test_config_loading
test_run_work_effort_manager
test_cli_command
cleanup

# Exit with the test status
if [ $TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
fi

exit $TEST_STATUS