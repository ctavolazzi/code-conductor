#!/bin/bash
# test_runner.sh - Functions for running tests

# Source common utilities
source ./test_utils.sh

# Global variables for tracking test runs
MODIFIED_SCRIPTS=()  # Track modified scripts for cleanup

# Function to limit log file size (truncate if too large)
limit_log_output() {
    local log_content="$1"
    local max_size_kb=${2:-500}  # Default to 500KB max size

    # Calculate rough size (character count as a rough estimation)
    local log_size_chars=${#log_content}
    local max_size_chars=$((max_size_kb * 1024))

    # Check if log content exceeds max size
    if [ $log_size_chars -gt $max_size_chars ]; then
        # Calculate how much to keep from beginning and end
        local third=$((max_size_chars / 3))
        local beginning=${log_content:0:$third}
        local ending=${log_content: -$third}

        # Truncate the middle
        echo "$beginning"
        echo "..."
        echo "[...LOG TRUNCATED FOR SIZE ($(($log_size_chars / 1024))KB) - SHOWING FIRST AND LAST PARTS ONLY...]"
        echo "..."
        echo "$ending"
    else
        # Return the original content if it's under the limit
        echo "$log_content"
    fi
}

# Function to run a test with timeout and add to report
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_type="$3"
    local timeout_seconds="${4:-$MAX_TEST_TIME}"  # Use default if not specified
    local max_log_size_kb="${5:-500}"  # Maximum log size in KB (default: 500KB)

    print_header "Running $test_name"
    echo "Command: $test_command"
    echo "Timeout: ${timeout_seconds}s"

    debug_print "=== TEST START: $test_name ==="
    debug_print "Command: $test_command"
    debug_print "Type: $test_type"
    debug_print "Timeout: ${timeout_seconds}s"
    debug_print "Max log size: ${max_log_size_kb}KB"

    # Add test to report
    echo "## $test_name" >> "$REPORT_FILE"
    echo "**Type:** $test_type" >> "$REPORT_FILE"
    echo "**Command:** \`$test_command\`" >> "$REPORT_FILE"
    echo "**Timeout:** ${timeout_seconds}s" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # Create temporary file for output
    local temp_output=$(mktemp)
    debug_print "Created temporary output file: $temp_output"

    # Modify the command if it's a shell script to make it non-interactive
    local original_command="$test_command"
    local temp_script=""

    if [[ "$test_command" == *".sh" ]]; then
        debug_print "Shell script detected, preparing non-interactive version"
        # Get the script name
        local script_name=$(echo "$test_command" | awk '{print $1}')
        # Make a non-interactive version
        temp_script=$(prepare_script_for_testing "$script_name")
        MODIFIED_SCRIPTS+=("$temp_script")  # Track for cleanup
        # Change the command to use the temporary script
        test_command="${test_command/$script_name/$temp_script}"
        debug_print "Modified command: $test_command"
    fi

    # Check if test files exist
    if [[ "$test_command" == *"unittest"* ]]; then
        local test_file=$(echo "$test_command" | grep -o "tests/[^ ]*")
        debug_print "Unittest file to check: $test_file"
        if [ ! -f "$test_file" ]; then
            print_error "Test file $test_file does not exist"
            debug_print "Test file does not exist: $test_file"
            echo "**Result:** ❌ FAILED (Test file not found)" >> "$REPORT_FILE"
            echo "**Error:** Test file \`$test_file\` does not exist" >> "$REPORT_FILE"
            return 1
        fi
        debug_print "Test file exists: $test_file"
    elif [[ "$original_command" == *".sh"* ]]; then
        local script_name=$(echo "$original_command" | awk '{print $1}')
        debug_print "Shell script to check: $script_name"
        if [ ! -f "$script_name" ]; then
            print_error "Test script $script_name does not exist"
            debug_print "Test script does not exist: $script_name"
            echo "**Result:** ❌ FAILED (Test script not found)" >> "$REPORT_FILE"
            echo "**Error:** Test script \`$script_name\` does not exist" >> "$REPORT_FILE"
            return 1
        fi
        debug_print "Test script exists: $script_name"
    fi

    # Check if the command is available (first word of the command)
    local cmd_first_word=$(echo "$test_command" | awk '{print $1}')
    debug_print "Checking command: $cmd_first_word"

    if [[ -f "$cmd_first_word" ]]; then
        # If it's a file path, it's ok
        debug_print "Command is a file path: $cmd_first_word"
    elif ! command_exists "$cmd_first_word"; then
        print_error "Command '$cmd_first_word' not found or not executable"
        debug_print "Command not found: $cmd_first_word"
        echo "**Result:** ❌ FAILED (Command '$cmd_first_word' not found)" >> "$REPORT_FILE"
        return 127
    fi
    debug_print "Command is available: $cmd_first_word"

    # Start time
    local start_time=$SECONDS
    debug_print "Test started at: $(date)"

    echo -e "${YELLOW}Test running...${NC}"

    # Create a file that will help us check for timeout
    local done_file=$(mktemp)
    debug_print "Created done file marker: $done_file"

    # Run the test with timeout and capture output
    execute_test_with_timeout "$test_command" "$temp_output" "$done_file" "$timeout_seconds"

    # Get the exit code
    local exit_code=$(cat "$done_file")

    # Get execution time
    local duration=$((SECONDS - start_time))
    debug_print "Test ran for ${duration}s"
    debug_print "Test ended at: $(date)"
    debug_print "Exit code: $exit_code"

    # Handle timeout case
    if [ "$exit_code" = "124" ]; then
        print_error "Test timed out after ${timeout_seconds} seconds"
        debug_print "Test TIMED OUT after ${timeout_seconds}s"
        echo "**Result:** ❌ FAILED (Timed out after ${timeout_seconds}s)" >> "$REPORT_FILE"
    elif [ "$exit_code" = "127" ]; then
        print_error "Command not found (exit code 127)"
        debug_print "Test FAILED - Command not found (exit code 127)"
        echo "**Result:** ❌ FAILED (Command not found)" >> "$REPORT_FILE"
    elif [ "$exit_code" != "0" ]; then
        print_error "Test failed with exit code $exit_code"
        debug_print "Test FAILED with exit code $exit_code"
        echo "**Result:** ❌ FAILED (Exit code: $exit_code)" >> "$REPORT_FILE"
    else
        print_success "Test passed in ${duration}s"
        debug_print "Test PASSED in ${duration}s"
        echo "**Result:** ✅ PASSED" >> "$REPORT_FILE"
    fi

    echo "**Duration:** ${duration}s" >> "$REPORT_FILE"

    # Show first few lines of output immediately for quick feedback
    if [ "$VERBOSE" = true ]; then
        echo "Output preview (first 10 lines):"
        head -n 10 "$temp_output"
        echo "..."
    fi

    # Add output summary to report
    add_output_to_report "$temp_output" "$test_name"

    # Clean up temp files
    debug_print "Removing temporary files: $temp_output $done_file"
    rm -f "$temp_output" "$done_file"

    debug_print "=== TEST END: $test_name ==="
    echo ""

    # Return the exit code
    return $exit_code
}

# Function to execute test with timeout
execute_test_with_timeout() {
    local test_command="$1"
    local temp_output="$2"
    local done_file="$3"
    local timeout_seconds="$4"

    if command_exists timeout; then
        debug_print "Using system timeout command"
        echo "$ $test_command" > "$temp_output"
        echo "----------------------------------------" >> "$temp_output"

        # Run with timeout command
        debug_print "Using timeout command"
        if [ "$VERBOSE" = true ]; then
            (timeout $timeout_seconds bash -c "$test_command" 2>&1 | tee -a "$temp_output"; echo $? > "$done_file") &
        else
            (timeout $timeout_seconds bash -c "$test_command" >> "$temp_output" 2>&1; echo $? > "$done_file") &
        fi

        local test_pid=$!
        debug_print "Test running with PID: $test_pid"

        # Wait for the command to finish or timeout
        local elapsed=0
        while [ ! -s "$done_file" ] && [ $elapsed -lt $timeout_seconds ]; do
            sleep 1
            elapsed=$((elapsed + 1))
            if [ "$VERBOSE" = true ] && [ $((elapsed % 5)) -eq 0 ]; then
                echo -e "${YELLOW}Still running... ${elapsed}s${NC}"
            fi
        done

        # Check if we timed out
        if [ ! -s "$done_file" ]; then
            debug_print "Test timed out after ${elapsed}s, killing PID $test_pid"
            kill -9 $test_pid 2>/dev/null
            echo "TIMEOUT REACHED AFTER ${elapsed}s" >> "$temp_output"
            echo "124" > "$done_file"  # 124 is the timeout exit code
        fi
    else
        debug_print "System timeout command not available, using basic timeout"
        echo "$ $test_command" > "$temp_output"
        echo "----------------------------------------" >> "$temp_output"
        echo "Using basic timeout mechanism (no timeout command available)" >> "$temp_output"

        execute_with_basic_timeout "$test_command" "$temp_output" "$done_file" "$timeout_seconds"
    fi
}

# Function to execute with a basic timeout (no timeout command)
execute_with_basic_timeout() {
    local test_command="$1"
    local temp_output="$2"
    local done_file="$3"
    local timeout_seconds="$4"

    if [ "$VERBOSE" = true ]; then
        # Run the command with a manual timeout mechanism
        (
            bash -c "$test_command" 2>&1 | tee -a "$temp_output" &
            cmd_pid=$!

            # Wait for the command to finish or timeout
            elapsed=0
            while kill -0 $cmd_pid 2>/dev/null && [ $elapsed -lt $timeout_seconds ]; do
                sleep 1
                elapsed=$((elapsed + 1))
                if [ $((elapsed % 5)) -eq 0 ]; then
                    echo -e "${YELLOW}Still running... ${elapsed}s${NC}"
                fi
            done

            # Check if we timed out
            if kill -0 $cmd_pid 2>/dev/null; then
                echo "TIMEOUT REACHED AFTER ${elapsed}s" | tee -a "$temp_output"
                kill -9 $cmd_pid 2>/dev/null
                echo "124" > "$done_file"  # 124 is the timeout exit code
            else
                wait $cmd_pid
                echo $? > "$done_file"
            fi
        )
    else
        # Run the command with a manual timeout mechanism
        (
            bash -c "$test_command" >> "$temp_output" 2>&1 &
            cmd_pid=$!

            # Wait for the command to finish or timeout
            elapsed=0
            while kill -0 $cmd_pid 2>/dev/null && [ $elapsed -lt $timeout_seconds ]; do
                sleep 1
                elapsed=$((elapsed + 1))
            done

            # Check if we timed out
            if kill -0 $cmd_pid 2>/dev/null; then
                echo "TIMEOUT REACHED AFTER ${elapsed}s" >> "$temp_output"
                kill -9 $cmd_pid 2>/dev/null
                echo "124" > "$done_file"  # 124 is the timeout exit code
            else
                wait $cmd_pid
                echo $? > "$done_file"
            fi
        )
    fi
}

# Function to add output to report
add_output_to_report() {
    local temp_output="$1"
    local test_name="$2"

    # Add output summary
    echo "### Output Summary" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"

    # Get the output and limit it for the report
    local output_lines=$(wc -l < "$temp_output")
    debug_print "Output is $output_lines lines long"
    if [ $output_lines -gt 60 ]; then
        head -n 30 "$temp_output" >> "$REPORT_FILE"
        echo -e "\n... [${output_lines} lines total, showing first 30 and last 30] ...\n" >> "$REPORT_FILE"
        tail -n 30 "$temp_output" >> "$REPORT_FILE"
    else
        cat "$temp_output" >> "$REPORT_FILE"
    fi
    echo '```' >> "$REPORT_FILE"

    # Add full log link
    local log_file="$REPORT_DIR/${test_name// /_}_$TIMESTAMP.log"
    debug_print "Copying output to log file: $log_file"
    cp "$temp_output" "$log_file"
    echo "" >> "$REPORT_FILE"
    echo "[Full log file]($log_file)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Function to run manual tests (which require manual verification)
add_manual_test_info() {
    local test_name="$1"
    local test_steps="$2"
    local test_expected="$3"

    print_header "Manual Test: $test_name"
    print_warning "This test requires manual verification"
    debug_print "Adding manual test: $test_name"

    echo "## $test_name (Manual Test)" >> "$REPORT_FILE"
    echo "**Type:** Manual Verification Required" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "### Steps" >> "$REPORT_FILE"
    echo "$test_steps" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "### Expected Result" >> "$REPORT_FILE"
    echo "$test_expected" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    debug_print "Manual test information added to report"
}

# Clean up function for temporary files
cleanup_temp_files() {
    debug_print "Cleaning up temporary files..."
    for script in "${MODIFIED_SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            debug_print "Removing temporary script: $script"
            rm -f "$script"
        fi
    done
}

# Register cleanup function to be called on exit
register_cleanup() {
    trap cleanup_temp_files EXIT
}

# Function to run tests from a specified array
run_tests_from_array() {
    local category_name="$1"
    shift  # Remove the first argument, leaving the array elements

    print_header "Running tests from category: $category_name"

    # Check if any tests are available
    if [ $# -eq 0 ]; then
        print_warning "No tests found in category: $category_name"
        echo "## $category_name Tests" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (No tests found)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        return 0
    fi

    debug_print "Found $(($#)) tests in category: $category_name"

    # Add category header to report
    echo "# $category_name Tests" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    local passed_count=0
    local failed_count=0

    # Run each test in the array
    for test_file in "$@"; do
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        debug_print "Running test file: $test_file"

        # Determine test type based on file extension and location
        local test_type="Standard Test"
        if [[ "$test_file" == *".py" ]]; then
            test_type="Python Test"
        elif [[ "$test_file" == *"simple_"* ]]; then
            test_type="Simple Test"
        fi

        # Process each test file with a descriptive name derived from the filename
        local test_name=$(basename "$test_file" | sed 's/\.sh$//; s/\.py$//; s/_/ /g; s/test/Test/; s/simple/Simple/;')

        # Build the command to run the test
        local test_command=""
        if [[ "$test_file" == *".py" ]]; then
            if [ -n "$PYTHON_CMD" ]; then
                test_command="$PYTHON_CMD $test_file"
            else
                print_warning "Skipping Python test: $test_file - Python not available"
                continue
            fi
        else
            test_command="./$test_file"
        fi

        # Run the test
        if run_test "$test_name" "$test_command" "$test_type" $MAX_TEST_TIME $MAX_LOG_SIZE_KB; then
            passed_count=$((passed_count + 1))
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            failed_count=$((failed_count + 1))
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    done

    # Add summary for this category
    echo "## Category Summary: $category_name" >> "$REPORT_FILE"
    echo "- Total tests: $(($#))" >> "$REPORT_FILE"
    echo "- Passed: $passed_count" >> "$REPORT_FILE"
    echo "- Failed: $failed_count" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    debug_print "Category $category_name complete: $passed_count passed, $failed_count failed"

    # Return non-zero if any tests failed
    return $failed_count
}