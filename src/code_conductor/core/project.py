import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def find_project_root() -> Optional[str]:
    """Find the root directory of the Code Conductor project.

    Returns:
        The project root directory if found, None otherwise.
    """
    try:
        current_dir = os.getcwd()

        # Look for _AI-Setup directory or work_efforts directory
        while current_dir != "/":
            if os.path.exists(os.path.join(current_dir, "_AI-Setup")) or \
               os.path.exists(os.path.join(current_dir, "work_efforts")):
                return current_dir

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                break

            current_dir = parent_dir

        return None

    except Exception as e:
        logger.error(f"Error finding project root: {str(e)}")
        return None