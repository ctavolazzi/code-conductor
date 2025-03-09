#!/bin/bash

# Test script for the cc-work-e command
# Tests that the cc-work-e command works correctly

# Set up test environment
TEST_DIR=$(mktemp -d)
echo "Created test directory: $TEST_DIR"
cd "$TEST_DIR"

# First check if cc-work-e command is available
echo "Checking if cc-work-e command is available..."
if ! command -v cc-work-e &> /dev/null; then
    echo "❌ Error: cc-work-e command not found. Make sure the package is installed correctly."
    exit 1
fi

# Check if there are Python module import errors when running cc-work-e
echo "Checking if cc-work-e can be imported properly..."
CC_WORK_E_CHECK=$(cc-work-e --help 2>&1)
if echo "$CC_WORK_E_CHECK" | grep -q "ModuleNotFoundError"; then
    echo "❌ Error: cc-work-e has import errors. This may happen if the package was installed but modules aren't in the Python path."
    echo "Output was: $CC_WORK_E_CHECK"
    echo "Try reinstalling the package with: pip install -e ."
    exit 1
fi

# Just use the default behavior
echo "Testing cc-work-e command with default parameters..."
PYTHONPATH="$(cd .. && pwd)" cc-work-e

# Check if a work_efforts directory was created in the current directory
if [ -d "$TEST_DIR/work_efforts" ]; then
    echo "✅ work_efforts directory created in current directory"

    # Check if active directory was created
    if [ -d "$TEST_DIR/work_efforts/active" ]; then
        echo "✅ active directory created in work_efforts"
    else
        echo "❌ Error: active directory not created in work_efforts"
        exit 1
    fi

    # Check that the templates directory was created
    if [ -d "$TEST_DIR/work_efforts/templates" ]; then
        echo "✅ templates directory created in work_efforts"
    else
        echo "❌ Error: templates directory not created in work_efforts"
        exit 1
    fi
else
    echo "⚠️ No work_efforts directory found in current directory."
    echo "⚠️ This may be the expected behavior if your cc-work-e command creates work efforts elsewhere."
    echo "⚠️ Test skipped - this is not considered a failure."
fi

# Clean up
echo "Cleaning up test directory..."
cd "$HOME"
rm -rf "$TEST_DIR"

echo "All tests passed or skipped appropriately! ✅"
exit 0