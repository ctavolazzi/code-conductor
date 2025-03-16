#!/bin/bash
# Simple test for code-conductor setup command in non-interactive mode

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

# Create a temporary directory for testing
print_header "Creating test environment"
TEST_DIR=$(mktemp -d)
echo "Test directory: $TEST_DIR"

# Make sure the test directory is cleaned up when the script exits
cleanup() {
    echo "Cleaning up test directory: $TEST_DIR"
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Change to the test directory
cd "$TEST_DIR" || { print_error "Failed to change to test directory"; exit 1; }

# Run the setup command in non-interactive mode
print_header "Testing code-conductor setup command (non-interactive)"
yes | code-conductor setup > setup_output.txt 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Setup command executed successfully"
    echo "Exit code: $EXIT_CODE"
else
    print_error "Setup command failed with exit code $EXIT_CODE"
    cat setup_output.txt
    exit 1
fi

# Check if .AI-Setup directory was created
if [ -d ".AI-Setup" ]; then
    print_success ".AI-Setup directory was created"
else
    print_error ".AI-Setup directory was not created"
    exit 1
fi

# Check if work_efforts directory was created
if [ -d ".AI-Setup/work_efforts" ]; then
    print_success "work_efforts directory was created"
else
    print_error "work_efforts directory was not created"
    exit 1
fi

# Check if config.json was created
if [ -f ".AI-Setup/config.json" ]; then
    print_success "config.json was created"
    echo "Config contents:"
    cat ".AI-Setup/config.json"
else
    print_error "config.json was not created"
    exit 1
fi

# Return to the original directory
cd - > /dev/null

print_header "Test Summary"
print_success "All simple setup tests passed!"
exit 0