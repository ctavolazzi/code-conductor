#!/usr/bin/env python3
"""
Tests for CLI validation functions.

This module tests the validation functions in the CLI module, specifically:
- validate_title
- validate_date
- validate_priority
"""

import sys
import os
import unittest
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import functions to test
from src.code_conductor.cli.cli import validate_title, validate_date, validate_priority

class TestValidateTitle(unittest.TestCase):
    """Tests for validate_title function"""

    def test_validate_title_normal(self):
        """Test validate_title with normal input"""
        title = "Test Work Effort"
        result = validate_title(title)
        self.assertEqual(result, title)

    def test_validate_title_with_special_chars(self):
        """Test validate_title with special characters"""
        title = "Test: Work <Effort> with *special* chars?"
        result = validate_title(title)
        self.assertEqual(result, "Test_ Work _Effort_ with _special_ chars_")

    def test_validate_title_too_long(self):
        """Test validate_title with a title that's too long"""
        title = "x" * 300
        result = validate_title(title)
        self.assertEqual(len(result), 200)

    def test_validate_title_empty(self):
        """Test validate_title with empty input"""
        with self.assertRaises(ValueError):
            validate_title("")

    def test_validate_title_none(self):
        """Test validate_title with None input"""
        with self.assertRaises(ValueError):
            validate_title(None)

    def test_validate_title_whitespace(self):
        """Test validate_title with whitespace input"""
        with self.assertRaises(ValueError):
            validate_title("   ")

class TestValidateDate(unittest.TestCase):
    """Tests for validate_date function"""

    def test_validate_date_normal(self):
        """Test validate_date with normal input"""
        date = "2025-03-16"
        result = validate_date(date)
        self.assertEqual(result, date)

    def test_validate_date_invalid_format(self):
        """Test validate_date with invalid format"""
        with self.assertRaises(ValueError):
            validate_date("03/16/2025")

    def test_validate_date_invalid_date(self):
        """Test validate_date with invalid date"""
        with self.assertRaises(ValueError):
            validate_date("2025-02-30")

    def test_validate_date_empty(self):
        """Test validate_date with empty input"""
        with self.assertRaises(ValueError):
            validate_date("")

    def test_validate_date_none(self):
        """Test validate_date with None input"""
        with self.assertRaises(ValueError):
            validate_date(None)

    def test_validate_date_whitespace(self):
        """Test validate_date with whitespace input"""
        with self.assertRaises(ValueError):
            validate_date("   ")

class TestValidatePriority(unittest.TestCase):
    """Tests for validate_priority function"""

    def test_validate_priority_normal(self):
        """Test validate_priority with normal input"""
        for priority in ["low", "medium", "high", "critical"]:
            result = validate_priority(priority)
            self.assertEqual(result, priority)

    def test_validate_priority_case_insensitive(self):
        """Test validate_priority with case-insensitive input"""
        result = validate_priority("HIGH")
        self.assertEqual(result, "high")

    def test_validate_priority_invalid(self):
        """Test validate_priority with invalid input"""
        result = validate_priority("invalid")
        self.assertEqual(result, "medium")  # Default value

if __name__ == "__main__":
    pytest.main(["-v", __file__])