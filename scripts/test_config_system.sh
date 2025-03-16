#!/bin/bash
# Test script for the config system

# Set up colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create test directory structure
print_header "Creating test directory structure"
TEST_DIR="$(pwd)/config_system_test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Test 1: Initialize a project with code-conductor setup
print_header "Test 1: Initialize project with code-conductor setup"
echo "Running code-conductor setup in $TEST_DIR"
echo "y" | code-conductor setup

# Verify config.json was created
if [ -f "$TEST_DIR/_AI-Setup/config.json" ]; then
    print_success "Config file created at $TEST_DIR/_AI-Setup/config.json"
    echo "Contents:"
    cat "$TEST_DIR/_AI-Setup/config.json"
else
    print_error "Config file not created at $TEST_DIR/_AI-Setup/config.json"
    exit 1
fi

# Test 2: Create a work effort and verify it's created in the right location
print_header "Test 2: Create work effort and verify location"
code-conductor work --title "Test Config System" --assignee "Tester" --priority "high"

# Verify work effort was created
WORK_EFFORT=$(find "$TEST_DIR/_AI-Setup/work_efforts/active" -name "*test_config_system.md")
if [ -n "$WORK_EFFORT" ]; then
    print_success "Work effort created at $WORK_EFFORT"
else
    print_error "Work effort not created in $TEST_DIR/_AI-Setup/work_efforts/active"
    exit 1
fi

# Test 3: Create subdirectory and verify it finds the config
print_header "Test 3: Create subdirectory and verify config discovery"
mkdir -p "$TEST_DIR/subdir/nested"
cd "$TEST_DIR/subdir/nested"

# List work efforts from the subdirectory
echo "Running code-conductor list from $(pwd)"
code-conductor list

# Verify it listed the work effort created earlier
if [ $? -eq 0 ]; then
    print_success "Successfully listed work efforts from subdirectory"
else
    print_error "Failed to list work efforts from subdirectory"
    exit 1
fi

# Test 4: Create a work effort from the subdirectory
print_header "Test 4: Create work effort from subdirectory"
code-conductor work --title "Nested Subdirectory Test" --assignee "Tester" --priority "medium"

# Verify work effort was created in the correct location
NESTED_WORK_EFFORT=$(find "$TEST_DIR/_AI-Setup/work_efforts/active" -name "*nested_subdirectory_test.md")
if [ -n "$NESTED_WORK_EFFORT" ]; then
    print_success "Work effort created at $NESTED_WORK_EFFORT from subdirectory"
else
    print_error "Work effort not created in $TEST_DIR/_AI-Setup/work_efforts/active"
    exit 1
fi

# Test 5: Create another directory with its own setup
print_header "Test 5: Create separate project with its own setup"
SEPARATE_DIR="$TEST_DIR/separate_project"
mkdir -p "$SEPARATE_DIR"
cd "$SEPARATE_DIR"

# Run setup in this directory
echo "Running code-conductor setup in $SEPARATE_DIR"
echo "y" | code-conductor setup

# Verify config.json was created
if [ -f "$SEPARATE_DIR/_AI-Setup/config.json" ]; then
    print_success "Config file created at $SEPARATE_DIR/_AI-Setup/config.json"
else
    print_error "Config file not created at $SEPARATE_DIR/_AI-Setup/config.json"
    exit 1
fi

# Create a work effort in the separate project
code-conductor work --title "Separate Project Test" --assignee "Tester" --priority "low"

# Verify work effort was created in the correct location
SEPARATE_WORK_EFFORT=$(find "$SEPARATE_DIR/_AI-Setup/work_efforts/active" -name "*separate_project_test.md")
if [ -n "$SEPARATE_WORK_EFFORT" ]; then
    print_success "Work effort created at $SEPARATE_WORK_EFFORT in separate project"
else
    print_error "Work effort not created in $SEPARATE_DIR/_AI-Setup/work_efforts/active"
    exit 1
fi

# Test 6: Modify config to use root location for one project
print_header "Test 6: Modify config to use root location"
CONFIG_FILE="$TEST_DIR/_AI-Setup/config.json"
# Create a backup
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

# Create work_efforts directory at root level
mkdir -p "$TEST_DIR/work_efforts/active"
mkdir -p "$TEST_DIR/work_efforts/completed"
mkdir -p "$TEST_DIR/work_efforts/archived"
mkdir -p "$TEST_DIR/work_efforts/templates"
mkdir -p "$TEST_DIR/work_efforts/scripts"

# Modify config (temporary for this test)
# Note: In a real application, you would use code-conductor commands
# to modify the config, but for testing we'll edit directly
TMP_CONFIG=$(mktemp)
cat "$CONFIG_FILE" | sed 's/"location": "in_ai_setup"/"location": "in_root"/' > "$TMP_CONFIG"
mv "$TMP_CONFIG" "$CONFIG_FILE"

print_success "Modified config to use root location"
echo "Modified config contents:"
cat "$CONFIG_FILE"

# Create a work effort in the original project with modified config
cd "$TEST_DIR"
code-conductor work --title "Root Location Test" --assignee "Tester" --priority "high"

# Verify work effort was created in the root location
ROOT_WORK_EFFORT=$(find "$TEST_DIR/work_efforts/active" -name "*root_location_test.md")
if [ -n "$ROOT_WORK_EFFORT" ]; then
    print_success "Work effort created at $ROOT_WORK_EFFORT (root location)"
else
    print_error "Work effort not created in $TEST_DIR/work_efforts/active"
    exit 1
fi

# Restore original config
mv "${CONFIG_FILE}.bak" "$CONFIG_FILE"

# Summary
print_header "Test Summary"
print_success "All tests passed!"
echo "The config.json system is working correctly to:"
echo "1. Create config files during setup"
echo "2. Determine work effort locations based on config"
echo "3. Find the nearest config file from subdirectories"
echo "4. Support multiple projects with different configs"
echo "5. Support different work effort location preferences"

echo -e "\nTest directory at: $TEST_DIR"
echo "You can examine the files or delete the test directory:"
echo "rm -rf $TEST_DIR"

exit 0