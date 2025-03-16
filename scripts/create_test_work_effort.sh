#!/bin/bash
# Script to create a work effort for testing framework in non-interactive mode

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

print_header "Creating Work Effort for Testing Framework"

# Check if python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found in PATH"
    exit 1
fi

# Get current date for title
DATE=$(date +%Y-%m-%d)

# Define the title and description
TITLE="Testing Framework Updates - $DATE"
DESCRIPTION="Added automated test discovery, modular test categories, and enhanced reporting to the testing framework. This work includes test categorization by type (simple, integration, unit, etc.), flexible test selection options, and detailed reporting in markdown format."

# Create the work effort in non-interactive mode
print_header "Running command to create work effort"
echo "Title: $TITLE"
echo "Description: $DESCRIPTION"

python3 cli.py work --title "$TITLE" \
    --description "$DESCRIPTION" \
    --priority "medium" \
    --assignee "dev" \
    -y

if [ $? -eq 0 ]; then
    print_success "Work effort created successfully!"
else
    print_error "Failed to create work effort."
    exit 1
fi

# Print instructions
print_header "Next Steps"
echo "-----------------------------------------"
echo "Work Effort Creation Results:"
echo "-----------------------------------------"
echo "1. The work effort has been created in the _AI-Setup/work_efforts/active directory"
echo "2. You can find it here: $(find . -name "*_${TITLE_SLUG}.md" | head -1)"
echo "-----------------------------------------"

print_success "Process completed!"
exit 0