#!/usr/bin/env python3
"""
Simple Workflow Runner

A simplified version of the workflow runner that creates a script with the
provided feature name.
"""

import os
import re
import sys
import argparse
from typing import Dict, List
import subprocess

def slugify(text):
    """Convert text to slug format."""
    return re.sub(r'[^a-z0-9_]', '', text.lower().replace(' ', '_'))

def create_script(feature_name, description="A new feature"):
    """Create a script file with the feature name."""
    script_name = slugify(feature_name)
    script_path = f"{script_name}.py"

    content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{feature_name}

{description}

Usage:
    python {script_name}.py [options]
\"\"\"

import sys

def main():
    print("Implementing {feature_name}...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""

    # Fix the feature name interpolation in the content
    content = content.replace("{feature_name}", feature_name)

    with open(script_path, 'w') as f:
        f.write(content)

    os.chmod(script_path, 0o755)
    print(f"✅ Created script: {script_path}")

    return script_path

def create_test(feature_name, script_name):
    """Create a test file for the feature."""
    test_path = f"test_{script_name}.py"
    class_name = ''.join(word.capitalize() for word in script_name.split('_'))

    content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Tests for {script_name}

This script tests the functionality of {script_name}.py

Usage:
    python test_{script_name}.py
\"\"\"

import os
import sys
import unittest

# Import the module to test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import {script_name}

class Test{class_name}(unittest.TestCase):
    \"\"\"Test the {feature_name} functionality.\"\"\"

    def test_basic_functionality(self):
        \"\"\"Test basic functionality.\"\"\"
        self.assertTrue(True)  # Placeholder assertion

if __name__ == "__main__":
    print("Running tests for {feature_name}...")
    unittest.main()
    print("Tests completed successfully!")
"""

    # Fix the feature name interpolation in the content
    content = content.replace("{feature_name}", feature_name)

    with open(test_path, 'w') as f:
        f.write(content)

    os.chmod(test_path, 0o755)
    print(f"✅ Created test script: {test_path}")

    return test_path

def execute_script(script_path):
    """Execute a script and return the results."""
    print(f"Executing {script_path}...")
    try:
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)

        print("\nExecution Results:")
        print("-" * 50)
        print(f"Return code: {result.returncode}")
        print("\nStandard output:")
        print(result.stdout or "(No output)")

        if result.stderr:
            print("\nStandard error:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ Script executed successfully")
        else:
            print("\n⚠️ Script execution failed")

        return result.returncode == 0
    except Exception as e:
        print(f"Error executing script: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a simplified workflow process")
    parser.add_argument("--feature-name", type=str, default="New Feature",
                        help="Name of the feature to develop")
    parser.add_argument("--description", type=str,
                        help="Description of the feature")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run in non-interactive mode with default values")
    args = parser.parse_args()

    feature_name = args.feature_name
    description = args.description or f"Implementation of {feature_name}"

    print(f"\n=== Using Feature: {feature_name} ===\n")

    # 1. Create script
    script_name = slugify(feature_name)
    script_path = create_script(feature_name, description)

    # 2. Execute script
    execute_script(script_path)

    # 3. Create test
    test_path = create_test(feature_name, script_name)

    print("\n=== Workflow completed successfully! ===\n")
    print(f"Created files:")
    print(f"- Script: {script_path}")
    print(f"- Tests: {test_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())