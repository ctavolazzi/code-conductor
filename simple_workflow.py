#!/usr/bin/env python3
"""
Simple Workflow Runner

A simplified version of the workflow runner that just creates a script file
with the provided feature name.
"""

import os
import re
import sys
import argparse

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

def main():
    parser = argparse.ArgumentParser(description="Simple workflow runner")
    parser.add_argument("--feature-name", type=str, default="New Feature",
                        help="Name of the feature")
    args = parser.parse_args()

    create_script(args.feature_name, f"Implementation of {args.feature_name}")

    return 0

if __name__ == "__main__":
    sys.exit(main())