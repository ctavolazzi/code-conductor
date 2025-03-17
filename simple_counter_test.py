#!/usr/bin/env python3
"""
Simple test script for demonstrating the persistent work effort counter functionality.

This script contains both the counter implementation and test code in one file
for easy execution.
"""

import os
import json
import hashlib
import time
import logging
import threading
import tempfile
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CounterTest")

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
    logger.info("Using fcntl for file locking")
except ImportError:
    HAS_FCNTL = False
    logger.info("fcntl not available, using simple lock")

class WorkEffortCounter:
    """
    A persistent counter for work effort numbering that maintains integrity.
    """

    def __init__(self, counter_file_path=None, logger=None):
        """Initialize the work effort counter."""
        self.logger = logger or logging.getLogger("WorkEffortCounter")

        if counter_file_path is None:
            temp_dir = tempfile.mkdtemp(prefix="counter_test_")
            counter_file_path = os.path.join(temp_dir, "counter.json")

        self.counter_file_path = counter_file_path
        self.lock_file_path = f"{counter_file_path}.lock"

        # Counter state
        self.current_count = 1  # Start from 1 by default
        self.previous_count = 0
        self.initialized = False
        self.file_lock = None
        self.thread_lock = threading.Lock()

        # Initialize or load counter
        self._load_counter_safe()

    def get_next_count(self):
        """Get the next count value and increment the counter."""
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

    def initialize(self, start_count=1):
        """Initialize or reset the counter to a specific value."""
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

    def reset(self):
        """Reset the counter to 1."""
        self.initialize(1)

    def get_current_count(self):
        """Get the current count without incrementing."""
        with self.thread_lock:
            self._load_counter_safe()
            return self.current_count

    def _load_counter_safe(self):
        """Load counter with extra safety checks."""
        try:
            self._acquire_file_lock()
            try:
                self._load_counter()
            finally:
                self._release_file_lock()
        except Exception as e:
            self.logger.error(f"Error loading counter: {str(e)}")
            # Initialize with defaults if we can't load
            if not self.initialized:
                self.current_count = 1
                self.previous_count = 0
                self.initialized = True

    def _load_counter(self):
        """Load counter from file and validate integrity."""
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
                self.logger.warning("Counter checksum verification failed")
                self._repair_counter()
                return

            # Load values
            self.current_count = data.get("current_count", 1)
            self.previous_count = data.get("previous_count", 0)
            self.initialized = True

        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Failed to load counter: {str(e)}")
            self._repair_counter()

    def _save_counter(self):
        """Save counter to file with checksum."""
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
            self.logger.error(f"Failed to save counter: {str(e)}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            raise

    def _calculate_checksum(self, data):
        """Calculate checksum for counter data."""
        # Convert data to JSON string and calculate SHA-256 hash
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _repair_counter(self):
        """Attempt to repair corrupted counter state."""
        self.logger.info("Attempting to repair counter")

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
                    self.logger.info("Counter repaired from backup file")
                    return
            except:
                pass

        # Fall back to safe default
        self.logger.warning("Using safe default counter values")
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

    def _acquire_file_lock(self):
        """Acquire file lock for cross-process synchronization."""
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
                self.logger.error(f"Failed to acquire lock: {str(e)}")
                raise IOError(f"Cannot acquire counter lock: {str(e)}")

    def _release_file_lock(self):
        """Release file lock."""
        if self.file_lock:
            try:
                if HAS_FCNTL:
                    fcntl.flock(self.file_lock, fcntl.LOCK_UN)
                    self.file_lock.close()
                else:
                    self.file_lock.release()
            except Exception as e:
                self.logger.error(f"Error releasing lock: {str(e)}")
            finally:
                self.file_lock = None


def get_counter(counter_file_path=None):
    """Factory function to get a WorkEffortCounter instance."""
    return WorkEffortCounter(counter_file_path)


# ===== TEST CODE =====

def simulate_work_effort_creation(counter, title, active_dir):
    """Simulate creating a work effort with the counter."""
    count = counter.get_next_count()
    count_prefix = f"{count:04d}_"

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M")

    # Create filename with sequential prefix
    safe_title = title.lower().replace(' ', '_')
    filename = f"{count_prefix}{timestamp}_{safe_title}.md"
    file_path = os.path.join(active_dir, filename)

    # Create a simple file as a placeholder
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(f"# {title}\n\nWork effort number: {count}")

    return filename, count


def run_basic_tests():
    """Run basic tests to demonstrate the counter functionality."""
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="counter_test_")
    try:
        # Set up test paths
        counter_file = os.path.join(temp_dir, "counter.json")
        active_dir = os.path.join(temp_dir, "active")
        completed_dir = os.path.join(temp_dir, "completed")
        archived_dir = os.path.join(temp_dir, "archived")

        # Create directories
        for directory in [active_dir, completed_dir, archived_dir]:
            os.makedirs(directory, exist_ok=True)

        # ===== TEST 1: Basic Counter Functionality =====
        logger.info("\n===== TEST 1: Basic Counter Functionality =====")

        # Create a new counter
        counter = WorkEffortCounter(counter_file)
        logger.info(f"Created counter at {counter_file}")

        # Check initial value
        init_value = counter.get_current_count()
        logger.info(f"Initial counter value: {init_value}")

        # Create first work effort
        filename1, count1 = simulate_work_effort_creation(counter, "First Task", active_dir)
        logger.info(f"Created work effort: {filename1} with count {count1}")

        # Create second work effort
        filename2, count2 = simulate_work_effort_creation(counter, "Second Task", active_dir)
        logger.info(f"Created work effort: {filename2} with count {count2}")

        # Verify counter incremented
        if count2 == count1 + 1:
            logger.info(f"✓ Counter incremented correctly: {count1} -> {count2}")
        else:
            logger.error(f"❌ Counter did not increment correctly: {count1} -> {count2}")

        # Check counter file contents
        with open(counter_file, 'r') as f:
            data = json.load(f)
            logger.info(f"Counter file contents: {json.dumps(data, indent=2)}")

        # ===== TEST 2: Counter Persistence =====
        logger.info("\n===== TEST 2: Counter Persistence =====")

        # Create a new instance (simulating a new process or application restart)
        counter2 = WorkEffortCounter(counter_file)

        # Check if the value persisted
        persisted_value = counter2.get_current_count()
        if persisted_value == data["current_count"]:
            logger.info(f"✓ Counter value persisted correctly: {persisted_value}")
        else:
            logger.error(f"❌ Counter value did not persist correctly. Expected {data['current_count']}, got {persisted_value}")

        # Create another work effort with the new instance
        filename3, count3 = simulate_work_effort_creation(counter2, "Persistence Test", active_dir)
        logger.info(f"Created work effort after 'restart': {filename3} with count {count3}")

        # ===== TEST 3: Error Recovery =====
        logger.info("\n===== TEST 3: Error Recovery =====")

        # Create a backup of the current counter
        backup_file = f"{counter_file}.bak"
        shutil.copy(counter_file, backup_file)
        logger.info(f"Created backup file: {backup_file}")

        # Corrupt the counter file
        with open(counter_file, 'r') as f:
            data = json.load(f)

        # Modify the data to invalidate the checksum
        previous_value = data["current_count"]
        data["current_count"] = 999
        data["checksum"] = "invalid_checksum"

        with open(counter_file, 'w') as f:
            json.dump(data, f)
        logger.info(f"Corrupted counter file with invalid data: {json.dumps(data, indent=2)}")

        # Create a new counter instance that should detect and recover
        counter3 = WorkEffortCounter(counter_file)
        recovered_value = counter3.get_current_count()

        # Verify recovery succeeded
        if recovered_value >= previous_value:
            logger.info(f"✓ Counter recovered successfully. Value after recovery: {recovered_value}")
        else:
            logger.error(f"❌ Counter did not recover correctly. Expected at least {previous_value}, got {recovered_value}")

        # ===== TEST 4: Migration from Existing Work Efforts =====
        logger.info("\n===== TEST 4: Migration from Existing Work Efforts =====")

        # Remove existing counter file
        if os.path.exists(counter_file):
            os.remove(counter_file)
            logger.info("Removed existing counter file to simulate first-time initialization")

        # Create sample work efforts with different numbering patterns
        sample_filenames = [
            "0001_202503160637_first_work_effort.md",
            "0005_202503160638_second_work_effort.md",
            "0010_202503160639_third_work_effort.md",
            "202503160640_unnumbered_work_effort.md",  # No number
        ]

        # Create the sample files
        for filename in sample_filenames:
            file_path = os.path.join(active_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"# Sample work effort\n\nFilename: {filename}")
            logger.info(f"Created sample file: {filename}")

        # Create a directory-based work effort with a high number
        dir_path = os.path.join(active_dir, "0042_202503160641_directory_work_effort")
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created sample directory: 0042_202503160641_directory_work_effort")

        # Initialize a new counter
        counter4 = WorkEffortCounter(counter_file)

        # Find the highest number in existing files to simulate migration
        highest_number = 0
        import re

        for item in os.listdir(active_dir):
            match = re.match(r"^(\d+)_", item)
            if match:
                try:
                    number = int(match.group(1))
                    highest_number = max(highest_number, number)
                    logger.info(f"Found numbered item: {item} with number {number}")
                except ValueError:
                    pass

        # Initialize counter based on existing work efforts
        next_number = highest_number + 1
        counter4.initialize(next_number)
        logger.info(f"Initialized counter to {next_number} based on existing work efforts")

        # Create a new work effort
        filename5, count5 = simulate_work_effort_creation(counter4, "Post-Migration Task", active_dir)
        logger.info(f"Created work effort after migration: {filename5} with count {count5}")

        if count5 == next_number:
            logger.info(f"✓ Migration successful. New work effort number is {count5}")
        else:
            logger.error(f"❌ Migration failed. Expected {next_number}, got {count5}")

        # Show all created work efforts
        logger.info("\n===== Created Work Efforts =====")
        for item in sorted(os.listdir(active_dir)):
            if os.path.isfile(os.path.join(active_dir, item)) and item.endswith(".md"):
                logger.info(f"- {item}")

        logger.info("\n===== All Tests Completed =====")

    except Exception as e:
        logger.error(f"Error during tests: {str(e)}", exc_info=True)
    finally:
        # Clean up
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting Work Effort Counter Tests")
    run_basic_tests()