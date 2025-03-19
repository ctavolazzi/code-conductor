#!/usr/bin/env python3
"""
AI Work Effort Creator module for code_conductor package.

This module provides compatibility for tests by re-exporting classes and functions
from the work_efforts package.
"""

# NOTE: These imports might appear unused to static analyzers, but they are
# actually re-exported for backward compatibility. They should NOT be removed
# without ensuring no other code depends on these imports.
#
# The 'create_content' function doesn't exist in the underlying module.
# For now, we'll import only what's available.
from src.code_conductor.work_efforts.scripts.ai_work_effort_creator import (
    setup_work_efforts_structure,
    create_work_effort,
    main,
    main_async,
    parse_arguments,
    # Import any generation function that can provide similar functionality
    generate_content_with_ollama as create_content
)
