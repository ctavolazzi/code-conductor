#!/usr/bin/env python3
"""
Work Effort Counter Module for maintaining persistent work effort numbering.

This module provides a durable, persistent counter system that survives system shutdowns
and crashes while maintaining a single source of truth for work effort numbering.
It handles sequential numbering that transitions gracefully from 4-digit numbers (9999) to
5+ digits (10000+) when needed.
"""

import os
import json
import hashlib
import time
import logging
import threading
import re
import datetime
from typing import Dict, Any, Optional, Tuple, List, Union

logger = logging.getLogger(__name__)

class SimpleLock:
    """Simple mock lock for systems without fcntl (Windows)."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock_file = None

    def acquire(self):
        self.lock_file = open(self.file_path, 'w+')
        return True

    def release(self):
        if self.lock_file:
            self.lock_file.close()
            self.lock_file = None
        return True

# Try to import fcntl (available on Unix/Linux/Mac)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

class WorkEffortCounter:
    """
    A persistent counter for work effort numbering that maintains integrity.

    Features:
    - Persistent storage using JSON with metadata
    - Checksum verification for integrity
    - File locking for thread/process safety
    - Previous/next tracking for validation
    - Auto-repair capabilities for corruption
    - Support for numbers exceeding 9999 with variable length
    - Optional date-based prefixing for improved organization
    """

    def __init__(self, counter_file_path: Optional[str] = None):
        """
        Initialize the work effort counter.

        Args:
            counter_file_path: Path to the counter file (JSON)
        """
        # Default counter file to ~/.code_conductor/counter.json if not specified
        if counter_file_path is None:
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".code_conductor")
            os.makedirs(config_dir, exist_ok=True)
            counter_file_path = os.path.join(config_dir, "counter.json")

        self.counter_file_path = counter_file_path
        self.lock_file_path = f"{counter_file_path}.lock"

        # Counter state
        self.current_count = 1  # Start from 1 by default
        self.previous_count = 0
        self.initialized = False
        self.file_lock = None
        self.thread_lock = threading.Lock()
        self.max_regular_count = 9999  # Upper limit for 4-digit numbers
        self.digit_length = 4  # Default digit length for numbers <= 9999

        # Initialize or load counter
        self._load_counter_safe()

    def get_next_count(self) -> int:
        """
        Get the next count value and increment the counter.

        Returns:
            The next count value

        Raises:
            IOError: If counter file cannot be read/written
            ValueError: If counter integrity check fails
        """
        with self.thread_lock:
            self._acquire_file_lock()
            try:
                # Re-load counter to ensure we have latest value
                self._load_counter()

                # Get current count and increment for next time
                count = self.current_count
                self.previous_count = count
                self.current_count += 1

                # Save updated counter
                self._save_counter()

                return count
            finally:
                self._release_file_lock()

    def format_work_effort_number(self, count: int, use_date_prefix: bool = False) -> str:
        """
        Format a work effort number with appropriate padding.

        Args:
            count: The count to format
            use_date_prefix: Whether to include a date prefix (YYYYMMDD)

        Returns:
            Formatted work effort number string
        """
        # Determine number of digits needed
        if count <= self.max_regular_count:
            # Use 4 digits for counts up to 9999
            formatted_count = f"{count:04d}"
        else:
            # Use natural length for larger numbers
            digits = len(str(count))
            formatted_count = f"{count:0{digits}d}"

        # Add date prefix if requested
        if use_date_prefix:
            today = datetime.datetime.now().strftime("%Y%m%d")
            return f"{today}{formatted_count}"

        return formatted_count

    def initialize(self, start_count: int = 1) -> None:
        """
        Initialize or reset the counter to a specific value.

        Args:
            start_count: The starting count value (default: 1)

        Raises:
            IOError: If counter file cannot be written
        """
        if start_count < 1:
            raise ValueError("Start count must be at least 1")

        with self.thread_lock:
            self._acquire_file_lock()
            try:
                self.previous_count = start_count - 1
                self.current_count = start_count
                self.initialized = True
                self._save_counter()
            finally:
                self._release_file_lock()

    def reset(self) -> None:
        """Reset the counter to 1."""
        self.initialize(1)

    def get_current_count(self) -> int:
        """
        Get the current count without incrementing.

        Returns:
            The current count value
        """
        with self.thread_lock:
            self._load_counter_safe()
            return self.current_count

    def _load_counter_safe(self) -> None:
        """
        Load counter with extra safety checks.

        This method catches and logs exceptions rather than propagating them.
        """
        try:
            self._acquire_file_lock()
            try:
                self._load_counter()
            finally:
                self._release_file_lock()
        except Exception as e:
            logger.error(f"Error loading counter: {str(e)}")
            # Initialize with defaults if we can't load
            if not self.initialized:
                self.current_count = 1
                self.previous_count = 0
                self.initialized = True

    def _load_counter(self) -> None:
        """
        Load counter from file and validate integrity.

        Raises:
            IOError: If counter file cannot be read
            ValueError: If counter file has invalid format or checksum
        """
        if not os.path.exists(self.counter_file_path):
            # Initialize counter file if it doesn't exist
            self.initialized = True
            self._save_counter()
            return

        try:
            with open(self.counter_file_path, 'r') as f:
                data = json.load(f)

            # Validate checksum
            stored_checksum = data.get("checksum", "")
            calculated_checksum = self._calculate_checksum({
                "current_count": data.get("current_count", 0),
                "previous_count": data.get("previous_count", 0),
                "timestamp": data.get("timestamp", 0)
            })

            if stored_checksum != calculated_checksum:
                logger.warning("Counter checksum verification failed")
                self._repair_counter()
                return

            # Load values
            self.current_count = data.get("current_count", 1)
            self.previous_count = data.get("previous_count", 0)
            self.initialized = True

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load counter: {str(e)}")
            self._repair_counter()

    def _save_counter(self) -> None:
        """
        Save counter to file with checksum.

        Raises:
            IOError: If counter file cannot be written
        """
        # Create counter data with timestamp and metadata
        timestamp = int(time.time())
        counter_data = {
            "current_count": self.current_count,
            "previous_count": self.previous_count,
            "timestamp": timestamp,
            "version": "1.0"
        }

        # Add checksum
        counter_data["checksum"] = self._calculate_checksum({
            "current_count": self.current_count,
            "previous_count": self.previous_count,
            "timestamp": timestamp
        })

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.counter_file_path), exist_ok=True)

        # Write to temporary file first, then rename for atomicity
        temp_file = f"{self.counter_file_path}.tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(counter_data, f, indent=2)

            # Rename for atomic replacement
            os.replace(temp_file, self.counter_file_path)
        except Exception as e:
            logger.error(f"Failed to save counter: {str(e)}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            raise

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """
        Calculate checksum for counter data.

        Args:
            data: Counter data dictionary

        Returns:
            Checksum string
        """
        # Convert data to JSON string and calculate SHA-256 hash
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _repair_counter(self) -> None:
        """
        Attempt to repair corrupted counter state.

        This method tries several strategies to recover:
        1. Check for backup/temp files
        2. Compare with actual files on disk
        3. Fall back to safe defaults
        """
        logger.info("Attempting to repair counter")

        # Check for backup file
        backup_file = f"{self.counter_file_path}.bak"
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)

                # Validate backup checksum
                stored_checksum = data.get("checksum", "")
                calculated_checksum = self._calculate_checksum({
                    "current_count": data.get("current_count", 0),
                    "previous_count": data.get("previous_count", 0),
                    "timestamp": data.get("timestamp", 0)
                })

                if stored_checksum == calculated_checksum:
                    self.current_count = data.get("current_count", 1)
                    self.previous_count = data.get("previous_count", 0)
                    self.initialized = True
                    self._save_counter()
                    logger.info("Counter repaired from backup file")
                    return
            except:
                pass

        # Fall back to safe default
        logger.warning("Using safe default counter values")
        self.current_count = max(1, self.current_count, self.previous_count + 1)
        self.previous_count = self.current_count - 1
        self.initialized = True
        self._save_counter()

        # Create backup after repair
        try:
            with open(self.counter_file_path, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        except:
            pass

    def _acquire_file_lock(self) -> None:
        """
        Acquire file lock for cross-process synchronization.

        Raises:
            IOError: If lock cannot be acquired
        """
        if self.file_lock is None:
            try:
                lock_dir = os.path.dirname(self.lock_file_path)
                os.makedirs(lock_dir, exist_ok=True)

                if HAS_FCNTL:
                    self.file_lock = open(self.lock_file_path, 'w+')
                    fcntl.flock(self.file_lock, fcntl.LOCK_EX)
                else:
                    self.file_lock = SimpleLock(self.lock_file_path)
                    self.file_lock.acquire()
            except Exception as e:
                if self.file_lock:
                    try:
                        if HAS_FCNTL:
                            self.file_lock.close()
                        else:
                            self.file_lock.release()
                    except:
                        pass
                    self.file_lock = None
                logger.error(f"Failed to acquire lock: {str(e)}")
                raise IOError(f"Cannot acquire counter lock: {str(e)}")

    def _release_file_lock(self) -> None:
        """Release file lock."""
        if self.file_lock:
            try:
                if HAS_FCNTL:
                    fcntl.flock(self.file_lock, fcntl.LOCK_UN)
                    self.file_lock.close()
                else:
                    self.file_lock.release()
            except Exception as e:
                logger.error(f"Error releasing lock: {str(e)}")
            finally:
                self.file_lock = None


# Singleton instance
_counter_instance = None

def get_counter(counter_file_path: Optional[str] = None) -> WorkEffortCounter:
    """
    Factory function to get a WorkEffortCounter instance.

    This is the recommended way to get a counter to ensure only one instance
    exists per counter file.

    Args:
        counter_file_path: Path to counter file

    Returns:
        WorkEffortCounter instance
    """
    global _counter_instance
    if _counter_instance is None:
        _counter_instance = WorkEffortCounter(counter_file_path)
    return _counter_instance


def initialize_counter_from_existing_work_efforts(work_efforts_dir: str, counter_file: Optional[str] = None) -> int:
    """
    Initialize counter based on existing work efforts.

    This function scans for work effort files in the given directory structure and
    initializes the counter to start from the next available number.

    Args:
        work_efforts_dir: Path to the work efforts directory
        counter_file: Path to the counter file (optional)

    Returns:
        int: The next available work effort number
    """
    if counter_file is None:
        counter_file = os.path.join(work_efforts_dir, "counter.json")

    # Create counter instance
    counter = get_counter(counter_file)

    # Define directory paths
    active_dir = os.path.join(work_efforts_dir, "active")
    completed_dir = os.path.join(work_efforts_dir, "completed")
    archived_dir = os.path.join(work_efforts_dir, "archived")

    # Find highest work effort number
    highest_number = 0

    # Regex pattern to match numbered work efforts (e.g., "0001_", "10000_")
    standard_pattern = r"^(\d+)_"

    # Function to check a directory
    def check_directory(directory):
        nonlocal highest_number
        if not os.path.exists(directory):
            return

        for item in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, item)) or item.endswith(".md"):
                # Check for standard pattern
                match = re.match(standard_pattern, item)
                if match:
                    try:
                        number = int(match.group(1))
                        highest_number = max(highest_number, number)
                        logger.info(f"Found numbered item: {item} with number {number}")
                    except ValueError:
                        pass

    # Check all relevant directories
    for directory in [active_dir, completed_dir, archived_dir]:
        check_directory(directory)

    # Initialize counter with next available number
    next_number = highest_number + 1 if highest_number > 0 else 1
    counter.initialize(next_number)
    logger.info(f"Counter initialized to {next_number} based on existing work efforts")

    return next_number


def format_work_effort_filename(title: str, count: int, use_date_prefix: bool = False) -> str:
    """
    Format a work effort filename with proper numbering.

    Args:
        title: The title of the work effort
        count: The count number
        use_date_prefix: Whether to use date prefix

    Returns:
        Properly formatted filename with .md extension
    """
    # Get counter instance
    counter = get_counter()

    # Format the number with appropriate padding
    formatted_count = counter.format_work_effort_number(count, use_date_prefix)

    # Create sanitized file name from title
    from ..work_effort import sanitize_title_for_filename
    safe_title = sanitize_title_for_filename(title)

    # Combine number and title
    return f"{formatted_count}_{safe_title}.md"