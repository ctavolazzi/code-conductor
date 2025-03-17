#!/usr/bin/env python3
"""
AI Work Effort Creator module for code_conductor package.

This module provides compatibility for tests by re-exporting classes and functions
from the work_efforts package.
"""

# Re-export for backward compatibility
from src.code_conductor.work_efforts.scripts.ai_work_effort_creator import (
    setup_work_efforts_structure,
    create_work_effort,
    create_content,
    main,
    main_async
)
