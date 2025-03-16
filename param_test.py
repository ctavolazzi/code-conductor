#!/usr/bin/env python3
"""
Parameter Testing Script

This script tests handling of command-line parameters, particularly for feature names.
"""

import argparse
import re
import sys

def slugify(text):
    """Convert text to slug format."""
    return re.sub(r'[^a-z0-9_]', '', text.lower().replace(' ', '_'))

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test parameter handling")
    parser.add_argument("--feature-name", type=str, default="Default Feature",
                        help="Name of the feature")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run in non-interactive mode")
    args = parser.parse_args()

    # Display the received parameters
    print("\n=== Parameter Test Results ===\n")
    print(f"Feature Name: '{args.feature_name}'")
    print(f"Slugified Name: '{slugify(args.feature_name)}'")
    print(f"Non-interactive Mode: {args.non_interactive}")

    return 0

if __name__ == "__main__":
    sys.exit(main())