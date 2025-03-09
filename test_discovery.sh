#!/bin/bash
# test_discovery.sh - Tool to discover and categorize all tests in the project

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

# Parse command line arguments
GENERATE_MODULE=false
UPDATE_TYPES=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -g|--generate)
      GENERATE_MODULE=true
      shift
      ;;
    -u|--update)
      UPDATE_TYPES=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [-g|--generate] [-u|--update] [-v|--verbose]"
      echo "  -g, --generate: Generate test_catalog.sh module with discovered tests"
      echo "  -u, --update: Update test_types.sh with discovered tests"
      echo "  -v, --verbose: Show verbose output"
      echo "  -h, --help: Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for more information"
      exit 1
      ;;
  esac
done

# Function to log verbose messages
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "$1"
    fi
}

print_header "Test Discovery Tool"
echo "Discovering all test files in the project..."

# Arrays to store discovered tests
SHELL_TESTS=()
PYTHON_TESTS=()
SIMPLE_TESTS=()
INTEGRATION_TESTS=()
UNIT_TESTS=()
COMMAND_TESTS=()
PERFORMANCE_TESTS=()
CLI_TESTS=()

# Find all shell test files in root and tests directory
log_verbose "Looking for shell test files..."
while IFS= read -r file; do
    if [[ "$file" == *"test_"* && "$file" == *".sh" ]] || [[ "$file" == *"simple_"* && "$file" == *".sh" ]]; then
        # Skip utility scripts and generated/temp files
        if [[ "$file" == *"test_utils.sh" || "$file" == *"test_runner.sh" || "$file" == *"test_reporting.sh" || "$file" == *"test_types.sh" || "$file" == *"test_catalog.sh" || "$file" == *"test_discovery.sh" || "$file" == *".test_temp" || "$file" == *"modified_script_"* ]]; then
            log_verbose "Skipping utility or temp script: $file"
            continue
        fi

        # Skip files in test_reports directory
        if [[ "$file" == *"test_reports/"* ]]; then
            log_verbose "Skipping file in test_reports directory: $file"
            continue
        fi

        # Check if it's a simple test
        if [[ "$file" == *"simple_"* ]]; then
            log_verbose "Found simple shell test: $file"
            SIMPLE_TESTS+=("$file")
        # Check if it's an integration test
        elif grep -q "integration test" "$file" || grep -q "Integration test" "$file"; then
            log_verbose "Found integration shell test: $file"
            INTEGRATION_TESTS+=("$file")
        elif grep -q "command test" "$file" || grep -q "Command test" "$file"; then
            log_verbose "Found command shell test: $file"
            COMMAND_TESTS+=("$file")
        elif grep -q "CLI test" "$file" || grep -q "cli test" "$file"; then
            log_verbose "Found CLI shell test: $file"
            CLI_TESTS+=("$file")
        else
            log_verbose "Found standard shell test: $file"
        fi
        SHELL_TESTS+=("$file")
    fi
done < <(find . -maxdepth 2 -type f -name "*.sh" -not -path "./.git/*" | grep -v "run_all_tests.sh" | grep -v "build_and_upload.sh")

# Find additional simple tests (including non "test_" prefixed files)
while IFS= read -r file; do
    if [[ "$file" == *"simple_"* && "$file" == *".sh" ]] && [[ ! " ${SHELL_TESTS[@]} " =~ " ${file} " ]]; then
        log_verbose "Found additional simple shell test: $file"
        SIMPLE_TESTS+=("$file")
        SHELL_TESTS+=("$file")
    fi
done < <(find . -maxdepth 2 -type f -name "simple_*.sh" -not -path "./.git/*")

# Find all Python test files only in the tests directory
log_verbose "Looking for Python test files..."
while IFS= read -r file; do
    if [[ "$file" == *"test_"* && "$file" == *".py" ]]; then
        # Check if it's a unit test
        if grep -q "unittest" "$file" && grep -q "TestCase" "$file"; then
            log_verbose "Found Python unit test: $file"
            UNIT_TESTS+=("$file")

            # Further categorize the test
            if grep -q "performance" "$file" || grep -q "Performance" "$file"; then
                log_verbose "Categorized as performance test: $file"
                PERFORMANCE_TESTS+=("$file")
            elif grep -q "integration" "$file" || grep -q "Integration" "$file"; then
                log_verbose "Categorized as integration test: $file"
                INTEGRATION_TESTS+=("$file")
            elif grep -q "cli" "$file" || grep -q "CLI" "$file"; then
                log_verbose "Categorized as CLI test: $file"
                CLI_TESTS+=("$file")
            fi
        else
            log_verbose "Found standard Python test: $file"
        fi
        PYTHON_TESTS+=("$file")
    fi
done < <(find ./tests -type f -name "*.py" -not -path "*/__pycache__/*")

# Print summary
print_header "Discovered Tests"
echo "Shell tests: ${#SHELL_TESTS[@]}"
echo "Python tests: ${#PYTHON_TESTS[@]}"
echo "Simple tests: ${#SIMPLE_TESTS[@]}"
echo "Integration tests: ${#INTEGRATION_TESTS[@]}"
echo "Unit tests: ${#UNIT_TESTS[@]}"
echo "Command tests: ${#COMMAND_TESTS[@]}"
echo "Performance tests: ${#PERFORMANCE_TESTS[@]}"
echo "CLI tests: ${#CLI_TESTS[@]}"

# Print detailed lists if verbose
if [ "$VERBOSE" = true ]; then
    print_header "Shell Tests"
    for test in "${SHELL_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Python Tests"
    for test in "${PYTHON_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Simple Tests"
    for test in "${SIMPLE_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Integration Tests"
    for test in "${INTEGRATION_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Unit Tests"
    for test in "${UNIT_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Command Tests"
    for test in "${COMMAND_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "Performance Tests"
    for test in "${PERFORMANCE_TESTS[@]}"; do
        echo "- $test"
    done

    print_header "CLI Tests"
    for test in "${CLI_TESTS[@]}"; do
        echo "- $test"
    done
fi

# Generate test catalog module if requested
if [ "$GENERATE_MODULE" = true ]; then
    print_header "Generating test_catalog.sh"

    echo "#!/bin/bash" > test_catalog.sh
    echo "# Auto-generated test catalog - $(date)" >> test_catalog.sh
    echo "# This file is generated by test_discovery.sh" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Shell Tests" >> test_catalog.sh
    echo "SHELL_TESTS=(" >> test_catalog.sh
    for test in "${SHELL_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Python Tests" >> test_catalog.sh
    echo "PYTHON_TESTS=(" >> test_catalog.sh
    for test in "${PYTHON_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Simple Tests" >> test_catalog.sh
    echo "SIMPLE_TESTS=(" >> test_catalog.sh
    for test in "${SIMPLE_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Integration Tests" >> test_catalog.sh
    echo "INTEGRATION_TESTS=(" >> test_catalog.sh
    for test in "${INTEGRATION_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Unit Tests" >> test_catalog.sh
    echo "UNIT_TESTS=(" >> test_catalog.sh
    for test in "${UNIT_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Command Tests" >> test_catalog.sh
    echo "COMMAND_TESTS=(" >> test_catalog.sh
    for test in "${COMMAND_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# Performance Tests" >> test_catalog.sh
    echo "PERFORMANCE_TESTS=(" >> test_catalog.sh
    for test in "${PERFORMANCE_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh
    echo "" >> test_catalog.sh

    echo "# CLI Tests" >> test_catalog.sh
    echo "CLI_TESTS=(" >> test_catalog.sh
    for test in "${CLI_TESTS[@]}"; do
        echo "    \"$test\"" >> test_catalog.sh
    done
    echo ")" >> test_catalog.sh

    # Make the catalog executable
    chmod +x test_catalog.sh
    print_success "Generated test_catalog.sh"
fi

# Update test_types.sh if requested
if [ "$UPDATE_TYPES" = true ]; then
    print_header "Updating test_types.sh"

    # TODO: Add implementation for updating test_types.sh
    print_warning "This feature is not yet implemented"
fi

print_success "Test discovery completed!"
exit 0