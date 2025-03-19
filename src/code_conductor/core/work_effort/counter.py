import os
import json
from pathlib import Path
from typing import Optional

class WorkEffortCounter:
    """Handles work effort numbering."""

    def __init__(self, project_dir: str):
        """Initialize the counter.

        Args:
            project_dir: The project directory path.
        """
        self.project_dir = project_dir
        self.counter_file = os.path.join(project_dir, ".code-conductor", "counter.json")
        self._ensure_counter_file()

    def _ensure_counter_file(self) -> None:
        """Ensure the counter file exists."""
        counter_dir = os.path.dirname(self.counter_file)
        if not os.path.exists(counter_dir):
            os.makedirs(counter_dir, exist_ok=True)

        if not os.path.exists(self.counter_file):
            with open(self.counter_file, "w") as f:
                json.dump({"count": 1}, f)

    def get_next(self) -> int:
        """Get the next work effort number.

        Returns:
            The next work effort number.
        """
        self._ensure_counter_file()

        with open(self.counter_file, "r") as f:
            data = json.load(f)

        count = data["count"]
        data["count"] += 1

        with open(self.counter_file, "w") as f:
            json.dump(data, f)

        return count

    def get_current(self) -> int:
        """Get the current work effort number.

        Returns:
            The current work effort number.
        """
        self._ensure_counter_file()

        with open(self.counter_file, "r") as f:
            data = json.load(f)

        return data["count"]

    def reset(self) -> None:
        """Reset the counter to 1."""
        self._ensure_counter_file()

        with open(self.counter_file, "w") as f:
            json.dump({"count": 1}, f)