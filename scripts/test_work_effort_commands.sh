#!/bin/bash

# Comprehensive Test Script for Code Conductor Work Efforts
# This script tests all available features of the code-conductor and cc-work-e commands

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}===============================================${NC}"
    echo -e "${BLUE}=== $1 ${NC}"
    echo -e "${BLUE}===============================================${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Function to check if a directory exists
check_dir_exists() {
    if [ -d "$1" ]; then
        return 0 # Directory exists
    else
        return 1 # Directory doesn't exist
    fi
}

# Create a test directory structure
TEST_DIR="$(pwd)/comprehensive_test"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

print_header "Starting Comprehensive Work Effort Tests"
print_info "Test directory: $TEST_DIR"

# 1. Test setup command - with check for existing folders
print_header "1. Testing 'code-conductor setup' command"

# Check for existing work_efforts and .AI-Setup folders
WORK_EFFORTS_EXISTS=false
AI_SETUP_EXISTS=false

if check_dir_exists "work_efforts"; then
    print_info "work_efforts folder already exists"
    WORK_EFFORTS_EXISTS=true
fi

if check_dir_exists ".AI-Setup"; then
    print_info ".AI-Setup folder already exists"
    AI_SETUP_EXISTS=true
fi

if $WORK_EFFORTS_EXISTS && $AI_SETUP_EXISTS; then
    print_info "Both required folders already exist. Setup may not be needed."
    read -p "Run setup anyway? (y/n): " RUN_SETUP
    if [[ $RUN_SETUP == "y" || $RUN_SETUP == "Y" ]]; then
        print_info "Running setup as requested..."
        code-conductor setup
    else
        print_info "Skipping setup command."
    fi
else
    print_info "At least one required folder does not exist. Running setup..."
    code-conductor setup
fi

# 2. Test cc-work-e with various options
print_header "2. Testing 'cc-work-e' command with various options"

# 2.1 Default work effort (no options)
print_info "2.1 Creating default work effort (no options)"
cc-work-e

# 2.2 Work effort with custom title
print_info "2.2 Creating work effort with custom title"
cc-work-e --title "Custom Title Work Effort"

# 2.3 Work effort with all custom options
print_info "2.3 Creating work effort with all custom options"
cc-work-e --title "Full Options Work Effort" --assignee "TestUser" --priority "high" --due-date "2025-06-30"

# 2.4 Work effort in current directory
print_info "2.4 Creating work effort in current directory"
mkdir -p "current_dir_test"
cd "current_dir_test"
cc-work-e --use-current-dir --title "Current Directory Work Effort"
cd ..

# 2.5 Work effort in package directory explicitly
print_info "2.5 Creating work effort in package directory explicitly"
cc-work-e --package-dir --title "Package Directory Work Effort"

# 3. Test code-conductor work command
print_header "3. Testing 'code-conductor work' command"

# 3.1 Default work effort
print_info "3.1 Creating default work effort with code-conductor work"
code-conductor work

# 3.2 Work effort with custom title
print_info "3.2 Creating work effort with custom title with code-conductor work"
code-conductor work --title "CC Work Command Test"

# 3.3 Work effort with all custom options
print_info "3.3 Creating work effort with all custom options with code-conductor work"
code-conductor work --title "CC Work Full Options" --assignee "CCUser" --priority "critical" --due-date "2025-12-31"

# 4. Test listing commands
print_header "4. Testing listing commands"

# 4.1 List all work efforts
print_info "4.1 Listing all work efforts with code-conductor list"
code-conductor list

# 5. Create work efforts in special locations/directories
print_header "5. Testing work efforts in special locations"

# 5.1 Create nested directory structure
print_info "5.1 Creating work effort in nested directory"
mkdir -p "nested/directory/structure"
cd "nested/directory/structure"
cc-work-e --use-current-dir --title "Nested Directory Work Effort"
cd "$TEST_DIR"

# 6. Create work efforts with special characters
print_header "6. Testing work efforts with special characters"

# 6.1 Work effort with special characters in title
print_info "6.1 Creating work effort with special characters in title"
cc-work-e --title "Special!@#$%^&*() Characters"

# 6.2 Work effort with very long title
print_info "6.2 Creating work effort with very long title"
cc-work-e --title "This is an extremely long title for a work effort that will test how the system handles very long titles which might potentially cause issues with filename length limits or display formatting in various interfaces. It's important to test edge cases like this."

# 7. Run interactive mode (this will require user interaction)
print_header "7. Testing interactive mode"
print_info "7.1 Interactive mode will require user input - we'll skip this in automated testing"
# Uncomment to test interactively:
# cc-work-e -i

# 8. Final summary
print_header "8. Final Summary"

# 8.1 List all work efforts created
print_info "8.1 Listing all work efforts created during testing"
code-conductor list

print_success "All tests completed!"
print_info "Test directory: $TEST_DIR"
print_info "You can review the created work efforts at this location."