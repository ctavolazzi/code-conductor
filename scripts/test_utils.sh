#!/bin/bash
# test_utils.sh - Common utility functions for test scripts

# Set up colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Global variables for verbose mode
VERBOSE=false

# Function to print debug info if verbose mode is enabled
debug_print() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${PURPLE}[DEBUG] $1${NC}"
    fi
}

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "==================================="
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

print_subheader() {
    echo -e "${CYAN}$1${NC}"
    echo "---------------------------------"
}

# Function to check if file exists
check_file_exists() {
    local file_path="$1"
    debug_print "Checking if file exists: $file_path"
    if [ ! -f "$file_path" ]; then
        print_error "Test file $file_path does not exist"
        debug_print "File does not exist: $file_path"
        return 1
    fi
    debug_print "File exists: $file_path"
    return 0
}

# Function to check if command exists
command_exists() {
    debug_print "Checking if command exists: $1"
    if command -v "$1" >/dev/null 2>&1; then
        debug_print "Command exists: $1"
        return 0
    else
        debug_print "Command does not exist: $1"
        return 1
    fi
}

# Check for Python 3 and set PYTHON_CMD
setup_python() {
    debug_print "Checking for Python 3"
    if command_exists python3; then
        python3_version=$(python3 --version 2>&1)
        print_success "Python 3 detected: $python3_version"
        debug_print "Python 3 found: $python3_version"
        echo "## Environment Check" >> "$REPORT_FILE"
        echo "✅ Python 3: $python3_version" >> "$REPORT_FILE"
        PYTHON_CMD="python3"
    elif command_exists python; then
        python_version=$(python --version 2>&1)
        debug_print "Python found: $python_version"
        if [[ $python_version == *"Python 3"* ]]; then
            print_success "Python 3 detected: $python_version"
            debug_print "Python command is Python 3"
            echo "## Environment Check" >> "$REPORT_FILE"
            echo "✅ Python 3: $python_version" >> "$REPORT_FILE"
            PYTHON_CMD="python"
        else
            print_warning "Python is installed but it's not Python 3: $python_version"
            debug_print "Python command is not Python 3"
            echo "## Environment Check" >> "$REPORT_FILE"
            echo "⚠️ Python is not version 3: $python_version" >> "$REPORT_FILE"
            PYTHON_CMD=""
        fi
    else
        print_warning "Python 3 is not installed or not available in PATH"
        debug_print "Python 3 not found"
        echo "## Environment Check" >> "$REPORT_FILE"
        echo "⚠️ Python 3 is not installed or not available in PATH" >> "$REPORT_FILE"
        PYTHON_CMD=""
    fi
    echo "" >> "$REPORT_FILE"
    export PYTHON_CMD
}

# Function to prepare scripts for non-interactive execution
prepare_script_for_testing() {
    local script_path="$1"
    local output_path="${script_path}.test_temp"

    debug_print "Preparing script for testing: $script_path -> $output_path"

    # Create a temp copy with non-interactive modifications
    cp "$script_path" "$output_path"
    chmod +x "$output_path"

    # Add NONINTERACTIVE flag at the top of the script
    # Use different approach to insert at beginning
    cat > "${output_path}.tmp" <<EOF
#!/bin/bash
NONINTERACTIVE=true
export YES_TO_ALL=true

$(cat "$output_path")
EOF
    mv "${output_path}.tmp" "$output_path"
    chmod +x "$output_path"

    # First, remove any existing --no-input flags which aren't supported
    sed -i '' 's/--no-input//g' "$output_path"

    # Replace any interactive code-conductor commands with non-interactive versions
    # We'll use "yes | " to pipe "y" to any prompts instead of using unsupported flags
    sed -i '' 's/code-conductor work /yes | code-conductor work /g' "$output_path"
    sed -i '' 's/code-conductor work_effort /yes | code-conductor work_effort /g' "$output_path"
    sed -i '' 's/code-conductor setup/yes | code-conductor setup/g' "$output_path"

    # Remove any existing interactive input (echo "y" |) to avoid doubling up
    sed -i '' 's/echo "y" | //g' "$output_path"

    debug_print "Script prepared for testing"
    cat "$output_path" > "$REPORT_DIR/modified_script_${TIMESTAMP}.sh"
    debug_print "Copy of modified script saved to $REPORT_DIR/modified_script_${TIMESTAMP}.sh"

    # Return the path to the modified script
    echo "$output_path"
}

# Initialize test environment by checking dependencies
init_test_environment() {
    local skip_deps=$1

    print_header "Initializing Test Environment"
    echo "Checking for required dependencies..."

    if [ "$skip_deps" = false ]; then
        # Check for Python 3
        setup_python

        # Check for bash
        debug_print "Checking for Bash"
        bash_version=$(bash --version | head -n 1)
        print_success "Bash: $bash_version"
        debug_print "Bash found: $bash_version"
        echo "✅ Bash: $bash_version" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"

        # Check for code-conductor
        debug_print "Checking for code-conductor"
        if command_exists code-conductor; then
            cc_version=$(code-conductor -v 2>&1)
            print_success "code-conductor detected: $cc_version"
            debug_print "code-conductor found: $cc_version"
            echo "✅ code-conductor: $cc_version" >> "$REPORT_FILE"
        else
            print_warning "code-conductor is not installed or not available in PATH"
            debug_print "code-conductor not found in PATH"
            echo "⚠️ code-conductor is not installed or not available in PATH" >> "$REPORT_FILE"
        fi

        echo "" >> "$REPORT_FILE"

        # Check if test files exist
        debug_print "Checking for tests directory"
        if [ ! -d "tests" ]; then
            print_warning "Tests directory not found"
            debug_print "Tests directory not found"
            echo "⚠️ Tests directory not found" >> "$REPORT_FILE"
        else
            print_success "Tests directory exists"
            debug_print "Tests directory found"
            echo "✅ Tests directory exists" >> "$REPORT_FILE"
        fi

        echo "" >> "$REPORT_FILE"
    else
        debug_print "Skipping dependency checks as requested"
        echo "## Environment Check" >> "$REPORT_FILE"
        echo "⚠️ Dependency checking skipped" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"

        # Set PYTHON_CMD based on what's available
        if command_exists python3; then
            PYTHON_CMD="python3"
        elif command_exists python; then
            PYTHON_CMD="python"
        else
            PYTHON_CMD=""
        fi
        debug_print "Python command set to: $PYTHON_CMD"
        export PYTHON_CMD
    fi
}