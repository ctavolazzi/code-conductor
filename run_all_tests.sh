#!/bin/bash
# Comprehensive test runner for code-conductor
# Automatically discovers and runs all tests

# Set default values for script options
VERBOSE=false
SINGLE_TEST=""
SKIP_DEPS_CHECK=false
MAX_TEST_TIME=30  # Default max test time in seconds
SIMPLE_TESTS_ONLY=false
AUTO_DISCOVER=true  # Set to true by default to enable auto-discovery
TEST_CATEGORY=""

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      export VERBOSE=true
      shift
      ;;
    -t|--test)
      export SINGLE_TEST="$2"
      shift
      shift
      ;;
    -s|--skip-deps)
      SKIP_DEPS_CHECK=true
      shift
      ;;
    -m|--max-time)
      export MAX_TEST_TIME="$2"
      shift
      shift
      ;;
    --simple)
      export SIMPLE_TESTS_ONLY=true
      shift
      ;;
    -c|--category)
      export TEST_CATEGORY="$2"
      shift
      shift
      ;;
    --no-discover)
      AUTO_DISCOVER=false
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [-v|--verbose] [-t|--test TEST_NAME] [-s|--skip-deps] [-m|--max-time SECONDS] [--simple] [-c|--category CATEGORY] [--no-discover]"
      echo "  -v, --verbose: Enable verbose output"
      echo "  -t, --test TEST_NAME: Run only the specified test"
      echo "      Available tests: config-unit, config-shell, multi-manager, help, version, simple-version, simple-help, all, simple-all"
      echo "  -s, --skip-deps: Skip dependency checking"
      echo "  -m, --max-time: Maximum time to wait for a test in seconds (default: 30)"
      echo "  --simple: Run only simple, quick tests (version, help)"
      echo "  -c, --category: Run tests from a specific category (shell, python, simple, integration, unit, command, performance, cli)"
      echo "  --no-discover: Skip auto-discovery of tests"
      echo "  -h, --help: Show this help message"
      exit 0
      ;;
    *)
      echo -e "Unknown option: $1"
      echo "Usage: $0 [-v|--verbose] [-t|--test TEST_NAME] [-s|--skip-deps] [-m|--max-time SECONDS] [--simple] [-c|--category CATEGORY] [--no-discover]"
      echo "Use --help for more information"
      exit 1
      ;;
  esac
done

# Auto-discover tests if enabled
if [ "$AUTO_DISCOVER" = true ]; then
  echo "Auto-discovering tests..."

  # Check if test_discovery.sh exists and is executable
  if [ -f "./test_discovery.sh" ] && [ -x "./test_discovery.sh" ]; then
    # Run test discovery with appropriate verbosity
    if [ "$VERBOSE" = true ]; then
      ./test_discovery.sh -v -g
    else
      ./test_discovery.sh -g
    fi

    # Check if discovery was successful
    if [ $? -ne 0 ]; then
      echo "Error: Test discovery failed. Falling back to existing test catalog if available."
    fi
  else
    echo "Warning: test_discovery.sh not found or not executable. Skipping auto-discovery."
  fi
fi

# Check if test catalog exists
if [ ! -f "./test_catalog.sh" ]; then
  echo "Error: test_catalog.sh not found. Please run test_discovery.sh first or ensure it's in the current directory."
  exit 1
fi

# Source all required modules and the test catalog
source ./test_utils.sh
source ./test_runner.sh
source ./test_reporting.sh
source ./test_types.sh
source ./test_catalog.sh

# Initialize tracking variables for tests
export TOTAL_TESTS=0
export PASSED_TESTS=0
export FAILED_TESTS=0
export MANUAL_TESTS=0

# Register cleanup function
register_cleanup

# Start time
START_TIME=$SECONDS
debug_print "Script started at: $(date)"

# Initialize report
init_report

# Initialize test environment
init_test_environment "$SKIP_DEPS_CHECK"

# Run tests based on mode
if [ -n "$SINGLE_TEST" ]; then
    debug_print "Running single test: $SINGLE_TEST"
    run_single_test "$SINGLE_TEST"
elif [ "$SIMPLE_TESTS_ONLY" = true ]; then
    debug_print "Running only simple tests"
    run_tests_from_array "Simple Tests" "${SIMPLE_TESTS[@]}"
elif [ -n "$TEST_CATEGORY" ]; then
    debug_print "Running tests from category: $TEST_CATEGORY"
    case "$TEST_CATEGORY" in
        "shell")
            run_tests_from_array "Shell Tests" "${SHELL_TESTS[@]}"
            ;;
        "python")
            run_tests_from_array "Python Tests" "${PYTHON_TESTS[@]}"
            ;;
        "simple")
            run_tests_from_array "Simple Tests" "${SIMPLE_TESTS[@]}"
            ;;
        "integration")
            run_tests_from_array "Integration Tests" "${INTEGRATION_TESTS[@]}"
            ;;
        "unit")
            run_tests_from_array "Unit Tests" "${UNIT_TESTS[@]}"
            ;;
        "command")
            run_tests_from_array "Command Tests" "${COMMAND_TESTS[@]}"
            ;;
        "performance")
            run_tests_from_array "Performance Tests" "${PERFORMANCE_TESTS[@]}"
            ;;
        "cli")
            run_tests_from_array "CLI Tests" "${CLI_TESTS[@]}"
            ;;
        *)
            echo "Unknown category: $TEST_CATEGORY"
            echo "Available categories: shell, python, simple, integration, unit, command, performance, cli"
            exit 1
            ;;
    esac
else
    debug_print "Running all tests"
    run_all_tests
    MANUAL_TESTS=$((MANUAL_TESTS + 1))
    add_manual_tests_to_report
fi

# Calculate total time
TOTAL_DURATION=$((SECONDS - START_TIME))
debug_print "Total duration: ${TOTAL_DURATION}s"

# Generate report summary
generate_report_summary "$TOTAL_TESTS" "$PASSED_TESTS" "$FAILED_TESTS" "$MANUAL_TESTS" "$TOTAL_DURATION"

debug_print "Script completed at: $(date)"
debug_print "Exit code: $FAILED_TESTS"

exit $FAILED_TESTS