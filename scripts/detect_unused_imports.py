#!/usr/bin/env python3
"""
A script to detect unused imports in Python files.

This script uses pyflakes to find unused imports in Python files within a specified directory,
with additional checks for common edge cases like re-exports, type hints, and dynamic usage.
It generates a report that lists all the unused imports found in each file.

Usage:
    python detect_unused_imports.py [options]

Options:
    --directory DIR, -d DIR   Directory to scan for Python files (default: src)
    --recursive, -r           Scan directories recursively (default: True)
    --pattern PATTERN, -p PATTERN
                             Glob pattern for files to scan (default: *.py)
    --output FILE, -o FILE    Output file for the report (default: unused_imports_report.md)
    --verbose, -v            Enable verbose output
    --exclude PATTERN, -e PATTERN
                             Glob pattern for files to exclude
    --config FILE, -c FILE   Configuration file (JSON) for special cases
"""

import os
import sys
import ast
import json
import argparse
import glob
from collections import defaultdict
import pyflakes.api
import pyflakes.reporter
import pyflakes.messages
import io
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

class Config:
    """Configuration for the import analyzer."""
    def __init__(self, config_file: Optional[str] = None):
        self.required_imports: Dict[str, List[str]] = {}  # file pattern -> list of imports
        self.reexport_patterns: List[str] = []  # patterns for re-export files
        self.ignore_files: List[str] = []  # patterns for files to ignore
        self.ignore_imports: List[str] = []  # imports to always ignore

        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.required_imports = config.get('required_imports', {})
                self.reexport_patterns = config.get('reexport_patterns', [])
                self.ignore_files = config.get('ignore_files', [])
                self.ignore_imports = config.get('ignore_imports', [])

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to find import usage in various contexts."""
    def __init__(self):
        self.imports: Set[str] = set()  # All imports
        self.used_names: Set[str] = set()  # Names actually used
        self.reexported_names: Set[str] = set()  # Names in __all__ or re-exported
        self.type_hint_names: Set[str] = set()  # Names used in type hints
        self.string_names: Set[str] = set()  # Names used in strings
        self.dynamic_names: Set[str] = set()  # Names used dynamically (getattr, etc.)

    def visit_Import(self, node: ast.Import) -> None:
        """Record import statements."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Record from ... import statements."""
        module = node.module or ''
        for name in node.names:
            if name.name == '*':
                continue
            full_name = f"{module}.{name.name}" if module else name.name
            self.imports.add(full_name)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Record name usage."""
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Record attribute access."""
        # Build full attribute chain (e.g., foo.bar.baz)
        attrs = []
        current = node
        while isinstance(current, ast.Attribute):
            attrs.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            attrs.append(current.id)
            full_name = '.'.join(reversed(attrs))
            self.used_names.add(full_name)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Record type annotation usage."""
        if isinstance(node.annotation, ast.Name):
            self.type_hint_names.add(node.annotation.id)
        elif isinstance(node.annotation, ast.Attribute):
            # Handle nested type hints (e.g., typing.List)
            attrs = []
            current = node.annotation
            while isinstance(current, ast.Attribute):
                attrs.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                attrs.append(current.id)
                full_name = '.'.join(reversed(attrs))
                self.type_hint_names.add(full_name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Record assignments, checking for __all__ and re-exports."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__all__':
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Str):
                            self.reexported_names.add(elt.s)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Record function calls, checking for dynamic usage."""
        if isinstance(node.func, ast.Name) and node.func.id in {'getattr', 'hasattr', 'isinstance', 'issubclass'}:
            # Check for dynamic attribute access
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Str):
                self.dynamic_names.add(node.args[1].s)
        self.generic_visit(node)

class ImportAnalyzer:
    """Analyzes Python files for unused imports with special case handling."""
    def __init__(self, config: Config):
        self.config = config

    def is_import_used(self, import_name: str, visitor: ImportVisitor, file_path: str) -> bool:
        """
        Check if an import is actually used, considering all usage contexts.

        Args:
            import_name: The name of the import to check
            visitor: The AST visitor that collected usage information
            file_path: Path to the file being checked

        Returns:
            bool: True if the import is used, False otherwise
        """
        # Check if this import should be ignored
        if any(re.match(pattern, import_name) for pattern in self.config.ignore_imports):
            return True

        # Check if this is a required import for this file
        for pattern, imports in self.config.required_imports.items():
            if re.match(pattern, file_path) and import_name in imports:
                return True

        # Check if this is a re-export file
        if any(re.match(pattern, file_path) for pattern in self.config.reexport_patterns):
            return True

        # Check various usage contexts
        base_name = import_name.split('.')[-1]
        if (base_name in visitor.used_names or
            base_name in visitor.reexported_names or
            base_name in visitor.type_hint_names or
            base_name in visitor.string_names or
            base_name in visitor.dynamic_names):
            return True

        # Check if any part of a dotted import is used
        parts = import_name.split('.')
        for i in range(len(parts)):
            partial = '.'.join(parts[:i+1])
            if partial in visitor.used_names:
                return True

        return False

    def analyze_file(self, file_path: str, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze a Python file for unused imports.

        Args:
            file_path: Path to the file to analyze
            verbose: Whether to print verbose output

        Returns:
            List of dictionaries containing information about unused imports
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)
            visitor = ImportVisitor()
            visitor.visit(tree)

            # Also use pyflakes for additional checks
            collector = ImportMessageCollector()
            pyflakes.api.check(content, file_path, reporter=collector)

            # Combine results from AST analysis and pyflakes
            unused_imports = []
            for message in collector.messages:
                import_name = message.message_args[0]
                if not self.is_import_used(import_name, visitor, file_path):
                    unused_imports.append({
                        'name': import_name,
                        'line': message.lineno,
                        'col': message.col
                    })

            if verbose and unused_imports:
                print(f"Found {len(unused_imports)} unused imports in {file_path}")

            return unused_imports
        except Exception as e:
            if verbose:
                print(f"Error analyzing {file_path}: {e}")
            return []

class ImportMessageCollector:
    """Collects unused import messages from pyflakes."""
    def __init__(self):
        self.messages = []

    def flake(self, message):
        """Callback for pyflakes messages."""
        if isinstance(message, pyflakes.messages.UnusedImport):
            self.messages.append(message)

    def unexpectedError(self, filename, msg):
        """Handle unexpected errors."""
        pass

    def syntaxError(self, filename, msg, lineno, offset, text):
        """Handle syntax errors."""
        pass

def find_python_files(directory: str, pattern: str, recursive: bool = True, exclude: Optional[str] = None) -> List[str]:
    """Find Python files matching the pattern in the given directory."""
    if recursive:
        search_pattern = os.path.join(directory, "**", pattern)
        files = glob.glob(search_pattern, recursive=True)
    else:
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)

    # Filter out excluded files
    if exclude:
        exclude_pattern = os.path.join(directory, "**", exclude)
        exclude_files = set(glob.glob(exclude_pattern, recursive=True))
        files = [f for f in files if f not in exclude_files]

    return sorted(files)

def generate_report(results: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
    """Generate a markdown report of unused imports."""
    total_imports = sum(len(imports) for imports in results.values())

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Unused Imports Report\n\n")
        f.write(f"**Total unused imports found: {total_imports}**\n\n")

        # Sort files by number of unused imports (descending)
        sorted_files = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)

        f.write("## Files by Unused Import Count\n\n")
        f.write("| File | Unused Imports |\n")
        f.write("|------|---------------|\n")
        for file_path, imports in sorted_files:
            if imports:
                f.write(f"| {file_path} | {len(imports)} |\n")

        f.write("\n## Detailed Report\n\n")
        for file_path, imports in sorted_files:
            if imports:
                rel_path = os.path.relpath(file_path)
                f.write(f"### {rel_path}\n\n")
                f.write("| Import | Line | Column |\n")
                f.write("|--------|------|--------|\n")
                for imp in imports:
                    f.write(f"| `{imp['name']}` | {imp['line']} | {imp['col']} |\n")
                f.write("\n")

    print(f"Report generated: {output_file}")
    print(f"Total unused imports found: {total_imports}")

def main() -> int:
    """Main function to detect unused imports."""
    parser = argparse.ArgumentParser(description="Detect unused imports in Python files")
    parser.add_argument('--directory', '-d', default='src', help='Directory to scan')
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                        help='Scan directories recursively')
    parser.add_argument('--pattern', '-p', default='*.py', help='File pattern to match')
    parser.add_argument('--output', '-o', default='unused_imports_report.md',
                        help='Output file for the report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--exclude', '-e', help='Pattern for files to exclude')
    parser.add_argument('--config', '-c', help='Configuration file for special cases')

    args = parser.parse_args()

    # Ensure directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        return 1

    print(f"Scanning directory: {args.directory}")
    print(f"Pattern: {args.pattern}")
    if args.exclude:
        print(f"Excluding: {args.exclude}")

    # Load configuration
    config = Config(args.config)

    # Find Python files
    files = find_python_files(args.directory, args.pattern, args.recursive, args.exclude)
    print(f"Found {len(files)} Python files to analyze.")

    # Create analyzer
    analyzer = ImportAnalyzer(config)

    # Analyze files
    results = {}
    for file_path in files:
        # Skip ignored files
        if any(re.match(pattern, file_path) for pattern in config.ignore_files):
            if args.verbose:
                print(f"Skipping ignored file: {file_path}")
            continue

        if args.verbose:
            print(f"Analyzing {file_path}...")
        unused_imports = analyzer.analyze_file(file_path, args.verbose)
        if unused_imports:
            results[file_path] = unused_imports

    # Generate report
    generate_report(results, args.output)

    return 0

if __name__ == "__main__":
    sys.exit(main())