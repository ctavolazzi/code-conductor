from typing import Dict, Optional
import os
import json
import logging
from datetime import datetime

class WorkEffortManagerConfig:
    """Class to handle work effort manager configuration."""

    def __init__(self, project_dir: str):
        """Initialize the manager config with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.config_file = os.path.join(project_dir, ".code_conductor", "manager_config.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def get_config(self, manager_name: str) -> Optional[Dict]:
        """Get configuration for a specific manager."""
        try:
            config = self._load_config()
            return config.get(manager_name)
        except Exception as e:
            self.logger.error(f"Error getting config for {manager_name}: {str(e)}")
            return None

    def set_config(self, manager_name: str, config: Dict) -> bool:
        """Set configuration for a specific manager."""
        try:
            current_config = self._load_config()
            current_config[manager_name] = {
                **config,
                "updated_at": datetime.now().isoformat()
            }
            self._save_config(current_config)
            return True
        except Exception as e:
            self.logger.error(f"Error setting config for {manager_name}: {str(e)}")
            return False

    def remove_config(self, manager_name: str) -> bool:
        """Remove configuration for a specific manager."""
        try:
            current_config = self._load_config()
            if manager_name in current_config:
                del current_config[manager_name]
                self._save_config(current_config)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing config for {manager_name}: {str(e)}")
            return False

    def get_default_config(self) -> Dict:
        """Get the default configuration."""
        return {
            "work_effort_dir": os.path.join(self.project_dir, "work_efforts"),
            "active_dir": "active",
            "completed_dir": "completed",
            "archived_dir": "archived",
            "template_dir": "templates",
            "history_dir": "history",
            "default_template": "default.json",
            "default_assignee": "self",
            "default_priority": "medium",
            "default_status": "active",
            "auto_index": True,
            "auto_backup": True,
            "backup_interval": 3600,  # 1 hour in seconds
            "max_backups": 10
        }

    def _load_config(self) -> Dict:
        """Load the manager config from disk."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {str(e)}")
                return {}
        return {}

    def _save_config(self, config: Dict):
        """Save the manager config to disk."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")

    def clear_config(self):
        """Clear all manager configuration."""
        try:
            self._save_config({})
        except Exception as e:
            self.logger.error(f"Error clearing config: {str(e)}")

    def ensure_directories(self, manager_name: str) -> bool:
        """Ensure all required directories exist for a manager."""
        try:
            config = self.get_config(manager_name) or self.get_default_config()
            base_dir = config["work_effort_dir"]

            dirs_to_create = [
                base_dir,
                os.path.join(base_dir, config["active_dir"]),
                os.path.join(base_dir, config["completed_dir"]),
                os.path.join(base_dir, config["archived_dir"]),
                os.path.join(base_dir, config["template_dir"]),
                os.path.join(base_dir, config["history_dir"])
            ]

            for directory in dirs_to_create:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            return True
        except Exception as e:
            self.logger.error(f"Error ensuring directories for {manager_name}: {str(e)}")
            return False