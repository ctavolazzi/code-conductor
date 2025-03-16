#!/bin/bash
# test_types.sh - Functions for running specific test types

# Source common utilities and test runner
source ./test_utils.sh
source ./test_runner.sh

# Function to run the config system unit test
run_config_unit_test() {
    debug_print "Setting up config unit test"
    if [ -n "$PYTHON_CMD" ] && [ -f "tests/test_config_system.py" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "Config System Unit Tests" "$PYTHON_CMD -m unittest tests/test_config_system.py" "Unit Tests" 60; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        if [ -z "$PYTHON_CMD" ]; then
            print_warning "Skipping Config System Unit Tests - Python 3 not available"
            debug_print "Python 3 not available for config unit test"
        else
            print_warning "Skipping Config System Unit Tests - file not found: tests/test_config_system.py"
            debug_print "Test file not found for config unit test"
        fi
        echo "## Config System Unit Tests" >> "$REPORT_FILE"
        echo "**Type:** Unit Tests" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (Python 3 or test file not available)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the config system shell test
run_config_shell_test() {
    debug_print "Setting up config shell test"
    if [ -f "./test_config_system.sh" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "Config System Shell Tests" "./test_config_system.sh" "Integration Tests" $MAX_TEST_TIME; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping Config System Shell Tests - file not found: ./test_config_system.sh"
        debug_print "Test file not found for config shell test"
        echo "## Config System Shell Tests" >> "$REPORT_FILE"
        echo "**Type:** Integration Tests" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (File not found)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the multi-manager shell test
run_multi_manager_test() {
    debug_print "Setting up multi-manager test"
    if [ -f "./test_multi_manager.sh" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "Multi-Manager Shell Tests" "./test_multi_manager.sh" "Integration Tests" $MAX_TEST_TIME; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping Multi-Manager Shell Tests - file not found: ./test_multi_manager.sh"
        debug_print "Test file not found for multi-manager test"
        echo "## Multi-Manager Shell Tests" >> "$REPORT_FILE"
        echo "**Type:** Integration Tests" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (File not found)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the help command test
run_help_command_test() {
    debug_print "Setting up help command test"
    if command_exists code-conductor; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "CLI Help Command" "code-conductor help" "Command Test" 30; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping CLI Help Command - code-conductor not in PATH"
        debug_print "code-conductor not in PATH"
        echo "## CLI Help Command" >> "$REPORT_FILE"
        echo "**Type:** Command Test" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (code-conductor not in PATH)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the version command test
run_version_command_test() {
    debug_print "Setting up version command test"
    if command_exists code-conductor; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "CLI Version Command" "code-conductor -v" "Command Test" 10; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping CLI Version Command - code-conductor not in PATH"
        debug_print "code-conductor not in PATH"
        echo "## CLI Version Command" >> "$REPORT_FILE"
        echo "**Type:** Command Test" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (code-conductor not in PATH)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the simple version test
run_simple_version_test() {
    debug_print "Setting up simple version test"
    if [ -f "./simple_version_test.sh" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "Simple Version Test" "./simple_version_test.sh" "Basic Test" 10; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping Simple Version Test - file not found: ./simple_version_test.sh"
        debug_print "Test file not found for simple version test"
        echo "## Simple Version Test" >> "$REPORT_FILE"
        echo "**Type:** Basic Test" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (File not found)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run the simple help test
run_simple_help_test() {
    debug_print "Setting up simple help test"
    if [ -f "./simple_help_test.sh" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if run_test "Simple Help Test" "./simple_help_test.sh" "Basic Test" 10; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Skipping Simple Help Test - file not found: ./simple_help_test.sh"
        debug_print "Test file not found for simple help test"
        echo "## Simple Help Test" >> "$REPORT_FILE"
        echo "**Type:** Basic Test" >> "$REPORT_FILE"
        echo "**Status:** ⚠️ SKIPPED (File not found)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Function to run a single test by name
run_single_test() {
    local test_name="$1"
    debug_print "Running single test: $test_name"

    case "$test_name" in
        "config-unit")
            run_config_unit_test
            ;;
        "config-shell")
            run_config_shell_test
            ;;
        "multi-manager")
            run_multi_manager_test
            ;;
        "help")
            run_help_command_test
            ;;
        "version")
            run_version_command_test
            ;;
        "simple-version")
            run_simple_version_test
            ;;
        "simple-help")
            run_simple_help_test
            ;;
        "all")
            run_all_tests
            ;;
        "simple-all")
            run_simple_version_test
            run_simple_help_test
            ;;
        *)
            print_error "Unknown test: $test_name"
            echo "Available tests: config-unit, config-shell, multi-manager, help, version, simple-version, simple-help, all, simple-all"
            return 1
            ;;
    esac
}

# Function to run all tests
run_all_tests() {
    debug_print "Running all tests"
    run_config_unit_test
    run_config_shell_test
    run_multi_manager_test
    run_help_command_test
    run_version_command_test
    run_simple_version_test
    run_simple_help_test
}