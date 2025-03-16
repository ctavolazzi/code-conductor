#!/usr/bin/env python3
"""
Comprehensive test script to identify all files with version references
and suggest which ones need to be updated.
"""

import sys
import os
import re
import glob

# Add parent directory to path to allow direct imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the version from __init__.py
from __init__ import __version__

# Directories to exclude from scanning
EXCLUDE_DIRS = [
    '.git',
    '__pycache__',
    'dist',
    'build',
    '.pytest_cache',
    'test_*',        # Test directories can have test version references
    'tests',         # Skip test files
    'work_efforts/active',  # Historical work efforts can have old versions
]

# Files to exclude from scanning
EXCLUDE_FILES = [
    '.gitignore',
    'LICENSE',
    'README.md',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'requirements.txt',
    'pyproject.toml',
    'setup.cfg',
    'test_*.py',  # Skip test files
    '*.pyc',
    '*.log',
    'test_version*.py',  # Skip version test files
]

def is_excluded(path):
    """Check if a path should be excluded from scanning."""
    base_name = os.path.basename(path)
    for pattern in EXCLUDE_FILES:
        if re.match(pattern.replace('*', '.*'), base_name):
            return True

    for exclude_dir in EXCLUDE_DIRS:
        exclude_pattern = exclude_dir.replace('*', '.*')
        if re.search(f'/{exclude_pattern}/', path):
            return True

    return False

def is_example_version(file_path, version):
    """Check if a version is an example in documentation."""
    if 'docs/' in file_path and version != __version__:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for indications that this is an example
            if 'Example' in content or 'example' in content:
                if version in content and '# Example' in content:
                    return True
    return False

def find_version_references(root_dir):
    """Find all files with version references."""
    version_references = []
    version_pattern = re.compile(r'(?:version|__version__|Version).*?["\']([0-9]+\.[0-9]+\.[0-9]+)["\']', re.IGNORECASE)

    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(re.match(pattern.replace('*', '.*'), d) for pattern in EXCLUDE_DIRS)]

        for file in files:
            if file.endswith(('.py', '.sh', '.md')) and not is_excluded(os.path.join(root, file)):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = version_pattern.findall(content)
                        if matches:
                            for match in matches:
                                # Skip if it's an example in documentation
                                if is_example_version(file_path, match):
                                    continue

                                version_references.append({
                                    'file': file_path,
                                    'version': match,
                                    'updated': match == __version__
                                })
                except (UnicodeDecodeError, IsADirectoryError, PermissionError):
                    continue

    return version_references

def suggest_updates(version_references):
    """Suggest files that need to be updated."""
    needs_update = [ref for ref in version_references if not ref['updated']]
    updated = [ref for ref in version_references if ref['updated']]

    return needs_update, updated

def main():
    """Main function to run the version consistency test."""
    print(f"\n=== Comprehensive Version Consistency Test ===")
    print(f"Current version in __init__.py: {__version__}")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    version_references = find_version_references(root_dir)

    needs_update, updated = suggest_updates(version_references)

    print(f"\n✅ Files with correct version ({__version__}): {len(updated)}")
    for ref in updated:
        print(f"  - {os.path.relpath(ref['file'], root_dir)}")

    print(f"\n❌ Files with outdated versions: {len(needs_update)}")
    for ref in needs_update:
        print(f"  - {os.path.relpath(ref['file'], root_dir)} (found: {ref['version']})")

    if needs_update:
        print("\nRecommended fixes:")
        print("1. Update files with a direct version reference to import from __init__.py")
        print("2. For non-Python files, update the hardcoded version number")
        print("3. For script files (work_effort_manager.py, etc.), consider getting version from __init__.py")
        sys.exit(1)
    else:
        print("\n✅ All version references are consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()