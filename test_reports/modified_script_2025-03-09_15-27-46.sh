#!/bin/bash
NONINTERACTIVE=true
export YES_TO_ALL=true

#!/bin/bash
# Simple test for code-conductor version command

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

# Run the version command
print_header "Testing code-conductor version command"
VERSION_OUTPUT=$(code-conductor -v)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Version command executed successfully"
    echo "Output: $VERSION_OUTPUT"
else
    print_error "Version command failed with exit code $EXIT_CODE"
    echo "Output: $VERSION_OUTPUT"
    exit 1
fi

# Try the help command as well
print_header "Testing code-conductor help command"
HELP_OUTPUT=$(code-conductor help | head -n 5)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Help command executed successfully"
    echo "First 5 lines of output: $HELP_OUTPUT"
else
    print_error "Help command failed with exit code $EXIT_CODE"
    echo "Output: $HELP_OUTPUT"
    exit 1
fi

print_header "Test Summary"
print_success "All simple tests passed!"
exit 0
