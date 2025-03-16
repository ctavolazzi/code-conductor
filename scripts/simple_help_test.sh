#!/bin/bash
# Simple test for code-conductor help command

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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Run the help command
print_header "Testing code-conductor help command"
HELP_OUTPUT=$(code-conductor help)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Help command executed successfully"
    echo "Output contains $(echo "$HELP_OUTPUT" | wc -l) lines"

    # Check for key sections in the help output
    if echo "$HELP_OUTPUT" | grep -q "Commands:"; then
        print_success "Help output contains commands section"
    else
        print_error "Help output missing commands section"
        exit 1
    fi

    if echo "$HELP_OUTPUT" | grep -q "Options for"; then
        print_success "Help output contains options section"
    else
        print_error "Help output missing options section"
        exit 1
    fi
else
    print_error "Help command failed with exit code $EXIT_CODE"
    echo "Output: $HELP_OUTPUT"
    exit 1
fi

print_header "Test Summary"
print_success "All help command tests passed!"
exit 0