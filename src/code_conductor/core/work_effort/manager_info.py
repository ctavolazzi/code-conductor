from typing import Dict, Optional
import os
import json
import logging
from datetime import datetime

class WorkEffortManagerInfo:
    """Class to handle work effort manager information."""

    def __init__(self, project_dir: str):
        """Initialize the manager info with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.info_file = os.path.join(project_dir, ".code_conductor", "manager_info.json")
        self._ensure_info_dir()

    def _ensure_info_dir(self):
        """Ensure the info directory exists."""
        info_dir = os.path.dirname(self.info_file)
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)

    def get_manager_info(self, manager_name: str) -> Optional[Dict]:
        """Get information for a specific manager."""
        try:
            info = self._load_info()
            return info.get(manager_name)
        except Exception as e:
            self.logger.error(f"Error getting manager info for {manager_name}: {str(e)}")
            return None

    def set_manager_info(self, manager_name: str, info: Dict) -> bool:
        """Set information for a specific manager."""
        try:
            current_info = self._load_info()
            current_info[manager_name] = {
                **info,
                "updated_at": datetime.now().isoformat()
            }
            self._save_info(current_info)
            return True
        except Exception as e:
            self.logger.error(f"Error setting manager info for {manager_name}: {str(e)}")
            return False

    def remove_manager_info(self, manager_name: str) -> bool:
        """Remove information for a specific manager."""
        try:
            current_info = self._load_info()
            if manager_name in current_info:
                del current_info[manager_name]
                self._save_info(current_info)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing manager info for {manager_name}: {str(e)}")
            return False

    def get_default_manager(self) -> Optional[str]:
        """Get the name of the default manager."""
        try:
            info = self._load_info()
            return info.get("default_manager")
        except Exception as e:
            self.logger.error(f"Error getting default manager: {str(e)}")
            return None

    def set_default_manager(self, manager_name: str) -> bool:
        """Set the default manager."""
        try:
            info = self._load_info()
            info["default_manager"] = manager_name
            info["default_manager_updated_at"] = datetime.now().isoformat()
            self._save_info(info)
            return True
        except Exception as e:
            self.logger.error(f"Error setting default manager: {str(e)}")
            return False

    def list_managers(self) -> Dict[str, Dict]:
        """List all managers and their information."""
        try:
            info = self._load_info()
            return {k: v for k, v in info.items() if k not in ["default_manager", "default_manager_updated_at"]}
        except Exception as e:
            self.logger.error(f"Error listing managers: {str(e)}")
            return {}

    def _load_info(self) -> Dict:
        """Load the manager info from disk."""
        if os.path.exists(self.info_file):
            try:
                with open(self.info_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading manager info: {str(e)}")
                return {}
        return {}

    def _save_info(self, info: Dict):
        """Save the manager info to disk."""
        try:
            with open(self.info_file, "w") as f:
                json.dump(info, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving manager info: {str(e)}")

    def clear_info(self):
        """Clear all manager information."""
        try:
            self._save_info({})
        except Exception as e:
            self.logger.error(f"Error clearing manager info: {str(e)}")