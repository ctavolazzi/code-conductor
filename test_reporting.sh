#!/bin/bash
# test_reporting.sh - Functions for generating test reports

# Source common utilities
source ./test_utils.sh

# Initialize report file
init_report() {
    # Set timestamp for report
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    REPORT_DIR="test_reports"
    REPORT_FILE="$REPORT_DIR/test_report_$TIMESTAMP.md"

    # Create report directory if it doesn't exist
    mkdir -p "$REPORT_DIR"
    debug_print "Created report directory: $REPORT_DIR"

    # Start the report
    echo "# Code Conductor Test Report" > "$REPORT_FILE"
    echo "Generated on: $(date)" >> "$REPORT_FILE"
    echo "Version: $(code-conductor -v 2>/dev/null || echo 'unknown')" >> "$REPORT_FILE"
    echo "Verbose mode: $([ "$VERBOSE" = true ] && echo 'enabled' || echo 'disabled')" >> "$REPORT_FILE"
    if [ -n "$SINGLE_TEST" ]; then
        echo "Test mode: single test ($SINGLE_TEST)" >> "$REPORT_FILE"
    else
        echo "Test mode: all tests" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"

    # Export variables
    export TIMESTAMP
    export REPORT_DIR
    export REPORT_FILE

    debug_print "Report file initialized: $REPORT_FILE"
}

# Generate report summary
generate_report_summary() {
    local total_tests="$1"
    local passed_tests="$2"
    local failed_tests="$3"
    local manual_tests="$4"
    local total_duration="$5"

    debug_print "Generating report summary"

    # Add summary to report
    echo "## Test Summary" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| Tests | Passed | Failed | Manual Tests | Duration |" >> "$REPORT_FILE"
    echo "|-------|--------|--------|-------------|----------|" >> "$REPORT_FILE"
    echo "| $total_tests | $passed_tests | $failed_tests | $manual_tests | ${total_duration}s |" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # Add detailed results
    echo "## Detailed Results" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    if [ $total_tests -eq 0 ]; then
        echo "⚠️ **No automated tests were run**" >> "$REPORT_FILE"
    elif [ $failed_tests -eq 0 ]; then
        echo "🎉 **All automated tests passed!** 🎉" >> "$REPORT_FILE"
    else
        echo "⚠️ **${failed_tests}/${total_tests} tests failed. Check the logs for details.** ⚠️" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"

    if [ $manual_tests -gt 0 ]; then
        echo "### Manual Tests" >> "$REPORT_FILE"
        echo "**$manual_tests** manual tests require verification" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    # Add cleanup information
    echo "## Test Cleanup" >> "$REPORT_FILE"
    echo "The following test directories can be safely removed:" >> "$REPORT_FILE"
    echo "- \`config_system_test\`" >> "$REPORT_FILE"
    echo "- \`multi_manager_test\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Run \`rm -rf config_system_test multi_manager_test\` to clean up." >> "$REPORT_FILE"

    # Print summary to console
    print_header "Test Summary"
    echo -e "Total Tests: ${CYAN}$total_tests${NC}"
    echo -e "Passed: ${GREEN}$passed_tests${NC}"
    echo -e "Failed: ${RED}$failed_tests${NC}"
    if [ $manual_tests -gt 0 ]; then
        echo -e "Manual Tests: ${YELLOW}$manual_tests${NC}"
    fi
    echo -e "Total Duration: ${CYAN}${total_duration}s${NC}"

    if [ $total_tests -eq 0 ]; then
        print_warning "No automated tests were run"
    elif [ $failed_tests -eq 0 ]; then
        print_success "All automated tests passed!"
    else
        print_error "$failed_tests test(s) failed!"
    fi

    # Print report location
    print_header "Test Report"
    echo -e "Report generated at: ${CYAN}$REPORT_FILE${NC}"
    echo "You can view the report with: less $REPORT_FILE"

    echo -e "\nTest directories can be cleaned up with:"
    echo "rm -rf config_system_test multi_manager_test"
}

# Add manual test information to report
add_manual_tests_to_report() {
    debug_print "Adding manual test information to report"
    # Add manual test instructions for setting up multiple work managers
    add_manual_test_info "Multi-Work-Manager Setup" "
1. Create a new test directory: \`mkdir -p multi_manager_test && cd multi_manager_test\`
2. Initialize a project: \`code-conductor setup\`
3. Create subdirectories: \`mkdir -p frontend backend docs\`
4. Add work managers to each subdirectory:
   - \`code-conductor new-work-manager --target-dir frontend --manager-name Frontend\`
   - \`code-conductor new-work-manager --target-dir backend --manager-name Backend\`
   - \`code-conductor new-work-manager --target-dir docs --manager-name Docs\`
5. List all work managers: \`code-conductor list-managers\`
6. Create work efforts in different managers:
   - \`code-conductor work --title \"Frontend Task\" --manager Frontend\`
   - \`code-conductor work --title \"Backend Task\" --manager Backend\`
7. Change default manager: \`code-conductor set-default --manager-name Backend\`
8. Create work effort without specifying manager (should use default): \`code-conductor work --title \"Default Manager Test\"\`
" "
- The setup process should complete without errors
- Each \`new-work-manager\` command should succeed
- The \`list-managers\` command should show all three managers plus the default one
- Work efforts should be created in the correct directories based on manager
- After changing the default manager, new work efforts should be created in that manager's directory
"
}