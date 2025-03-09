#!/bin/bash
NONINTERACTIVE=true
# Test script for multiple work effort managers

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
TEST_DIR="$(pwd)/multi_manager_test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Test 1: Initialize a project with code-conductor setup --no-input
print_header "Test 1: Initialize project with code-conductor setup --no-input"
echo "Running code-conductor setup --no-input in $TEST_DIR"
 code-conductor setup --no-input

# Verify config.json was created with initial work manager
if [ -f "$TEST_DIR/.AI-Setup/config.json" ]; then
    print_success "Config file created at $TEST_DIR/.AI-Setup/config.json"
    echo "Contents:"
    cat "$TEST_DIR/.AI-Setup/config.json"
else
    print_error "Config file not created at $TEST_DIR/.AI-Setup/config.json"
    exit 1
fi

# Test 2: Create a work effort in the initial manager
print_header "Test 2: Create work effort in initial manager"
code-conductor work --no-input --title "Test Work Effort" --title "Main Manager Test" --assignee "Tester" --priority "high"

# Verify work effort was created
MAIN_WORK_EFFORT=$(find "$TEST_DIR/.AI-Setup/work_efforts/active" -name "*main_manager_test.md")
if [ -n "$MAIN_WORK_EFFORT" ]; then
    print_success "Work effort created at $MAIN_WORK_EFFORT"
else
    print_error "Work effort not created in $TEST_DIR/.AI-Setup/work_efforts/active"
    exit 1
fi

# Test 3: Create subdirectories for additional managers
print_header "Test 3: Create subdirectories for additional managers"
mkdir -p "$TEST_DIR/frontend"
mkdir -p "$TEST_DIR/backend"
mkdir -p "$TEST_DIR/docs"

# Test 4: Create new work managers in subdirectories
print_header "Test 4: Create new work managers in subdirectories"

echo "Creating frontend work manager..."
code-conductor new-work-manager --target-dir "$TEST_DIR/frontend" --manager-name "Frontend"
if [ $? -eq 0 ]; then
    print_success "Frontend work manager created"
else
    print_error "Failed to create Frontend work manager"
    exit 1
fi

echo "Creating backend work manager..."
code-conductor new-work-manager --target-dir "$TEST_DIR/backend" --manager-name "Backend"
if [ $? -eq 0 ]; then
    print_success "Backend work manager created"
else
    print_error "Failed to create Backend work manager"
    exit 1
fi

echo "Creating docs work manager..."
code-conductor new-work-manager --target-dir "$TEST_DIR/docs" --manager-name "Documentation"
if [ $? -eq 0 ]; then
    print_success "Documentation work manager created"
else
    print_error "Failed to create Documentation work manager"
    exit 1
fi

# Test 5: Verify work managers were added to config.json
print_header "Test 5: Verify managers in config.json"
if grep -q "Frontend" "$TEST_DIR/.AI-Setup/config.json" &&
   grep -q "Backend" "$TEST_DIR/.AI-Setup/config.json" &&
   grep -q "Documentation" "$TEST_DIR/.AI-Setup/config.json"; then
    print_success "All work managers found in config.json"
else
    print_error "Not all work managers were added to config.json"
    exit 1
fi

# Test 6: List all work managers
print_header "Test 6: List all work managers"
cd "$TEST_DIR"
code-conductor list-managers
if [ $? -eq 0 ]; then
    print_success "Successfully listed all work managers"
else
    print_error "Failed to list work managers"
    exit 1
fi

# Test 7: Create work efforts in different managers
print_header "Test 7: Create work efforts in different managers"

echo "Creating work effort in Frontend manager..."
code-conductor work --no-input --title "Test Work Effort" --title "Frontend Task" --manager "Frontend" --priority "medium"
FRONTEND_WORK=$(find "$TEST_DIR/frontend/work_efforts/active" -name "*frontend_task.md")
if [ -n "$FRONTEND_WORK" ]; then
    print_success "Frontend work effort created at $FRONTEND_WORK"
else
    print_error "Frontend work effort not created"
    exit 1
fi

echo "Creating work effort in Backend manager..."
code-conductor work --no-input --title "Test Work Effort" --title "Backend Task" --manager "Backend" --priority "high"
BACKEND_WORK=$(find "$TEST_DIR/backend/work_efforts/active" -name "*backend_task.md")
if [ -n "$BACKEND_WORK" ]; then
    print_success "Backend work effort created at $BACKEND_WORK"
else
    print_error "Backend work effort not created"
    exit 1
fi

echo "Creating work effort in Documentation manager..."
code-conductor work --no-input --title "Test Work Effort" --title "Documentation Task" --manager "Documentation" --priority "low"
DOCS_WORK=$(find "$TEST_DIR/docs/work_efforts/active" -name "*documentation_task.md")
if [ -n "$DOCS_WORK" ]; then
    print_success "Documentation work effort created at $DOCS_WORK"
else
    print_error "Documentation work effort not created"
    exit 1
fi

# Test 8: List work efforts in different managers
print_header "Test 8: List work efforts in different managers"

echo "Listing work efforts in Frontend manager..."
code-conductor list --manager "Frontend"
if [ $? -eq 0 ]; then
    print_success "Listed Frontend work efforts"
else
    print_error "Failed to list Frontend work efforts"
    exit 1
fi

echo "Listing work efforts in Backend manager..."
code-conductor list --manager "Backend"
if [ $? -eq 0 ]; then
    print_success "Listed Backend work efforts"
else
    print_error "Failed to list Backend work efforts"
    exit 1
fi

# Test 9: Change default manager
print_header "Test 9: Change default manager"
code-conductor set-default --manager-name "Backend"
if [ $? -eq 0 ]; then
    print_success "Set default manager to Backend"
else
    print_error "Failed to set default manager"
    exit 1
fi

# Verify default manager was changed in config.json
if grep -q "\"default_work_manager\": \"backend\"" "$TEST_DIR/.AI-Setup/config.json"; then
    print_success "Default manager updated in config.json"
else
    print_error "Default manager not updated in config.json"
    exit 1
fi

# Test 10: Create work effort using default manager
print_header "Test 10: Create work effort using default manager"
cd "$TEST_DIR"  # Go back to main directory
code-conductor work --no-input --title "Test Work Effort" --title "Default Manager Test" --priority "medium"

# Verify work effort was created in the backend folder (default)
DEFAULT_WORK=$(find "$TEST_DIR/backend/work_efforts/active" -name "*default_manager_test.md")
if [ -n "$DEFAULT_WORK" ]; then
    print_success "Work effort created in default manager (Backend) at $DEFAULT_WORK"
else
    print_error "Work effort not created in default manager"
    exit 1
fi

# Summary
print_header "Test Summary"
print_success "All tests passed!"
echo "The multi-work-manager system is working correctly:"
echo "1. Created main project with setup"
echo "2. Added multiple work effort managers in subdirectories"
echo "3. Created work efforts in different managers"
echo "4. Listed work efforts from specific managers"
echo "5. Changed the default manager"
echo "6. Created work efforts using the default manager"

echo -e "\nTest directory at: $TEST_DIR"
echo "You can examine the files or delete the test directory:"
echo "rm -rf $TEST_DIR"

exit 0