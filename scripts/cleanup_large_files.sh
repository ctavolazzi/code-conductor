#!/bin/bash
# Cleanup script for large files in the repository

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

print_header "Removing Large Files from Git Index"
echo "This script will remove large files from Git while preserving them locally."

# First, check if we have any large files in the test_reports directory
print_header "Checking for large test report files"
find test_reports -type f -size +50M | while read file; do
    size=$(du -h "$file" | cut -f1)
    echo "Found large file: $file (${size})"

    # Remove the file from Git tracking
    git rm --cached "$file" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Removed $file from Git tracking"
    else
        print_warning "$file was not tracked in Git or another issue occurred"
    fi
done

# Check if .gitignore has the test_reports entry
if grep -q "test_reports/" .gitignore; then
    print_success "test_reports/ is already in .gitignore"
else
    print_warning "test_reports/ was not found in .gitignore. Adding it now."
    echo "test_reports/" >> .gitignore
    print_success "Added test_reports/ to .gitignore"
fi

# Check if log files are ignored
if grep -q "*.log" .gitignore; then
    print_success "*.log is already in .gitignore"
else
    print_warning "*.log was not found in .gitignore. Adding it now."
    echo "*.log" >> .gitignore
    print_success "Added *.log to .gitignore"
fi

# Check for any other large files
print_header "Checking for other large files"
find . -type f -not -path "*/\.*" -not -path "*/test_reports/*" -size +50M | while read file; do
    size=$(du -h "$file" | cut -f1)
    echo "Found large file: $file (${size})"
    print_warning "Consider removing or excluding this file from Git"
done

print_header "Next steps"
echo "1. Commit the .gitignore changes:"
echo "   git add .gitignore"
echo "   git commit -m \"Add test_reports/ to .gitignore to exclude large log files\""
echo "2. Push your changes again:"
echo "   git push"
echo ""
echo "If you still have issues, you may need to use Git LFS for large files:"
echo "   https://git-lfs.github.com"

print_success "Script completed."
exit 0