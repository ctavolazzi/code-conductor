from typing import Dict, Optional
import os
import json
import logging
from datetime import datetime

from .manager import WorkEffortManager
from .manager_factory import WorkEffortManagerFactory

class WorkEffortManagerRegistry:
    """Registry for managing work effort managers."""

    def __init__(self, project_dir: str):
        """Initialize the registry with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.managers: Dict[str, WorkEffortManager] = {}
        self.factory = WorkEffortManagerFactory(project_dir)
        self.registry_file = os.path.join(project_dir, '.code_conductor', 'manager_registry.json')
        self._ensure_registry_dir()
        self._load_registry()

    def _ensure_registry_dir(self) -> None:
        """Ensure the registry directory exists."""
        registry_dir = os.path.dirname(self.registry_file)
        if not os.path.exists(registry_dir):
            os.makedirs(registry_dir)

    def _load_registry(self) -> None:
        """Load the registry from disk."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for manager_name in data.get('managers', []):
                        self.get_manager(manager_name)
            except Exception as e:
                self.logger.error(f"Error loading registry: {e}")

    def _save_registry(self) -> None:
        """Save the registry to disk."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump({
                    'managers': list(self.managers.keys()),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving registry: {e}")

    def get_manager(self, manager_name: str) -> Optional[WorkEffortManager]:
        """Get a manager by name, creating it if it doesn't exist."""
        if manager_name not in self.managers:
            try:
                manager = self.factory.create_manager(manager_name)
                self.managers[manager_name] = manager
                self._save_registry()
            except Exception as e:
                self.logger.error(f"Error creating manager {manager_name}: {e}")
                return None
        return self.managers.get(manager_name)

    def remove_manager(self, manager_name: str) -> bool:
        """Remove a manager from the registry."""
        if manager_name in self.managers:
            try:
                self.factory.remove_manager(manager_name)
                del self.managers[manager_name]
                self._save_registry()
                return True
            except Exception as e:
                self.logger.error(f"Error removing manager {manager_name}: {e}")
        return False
    def list_managers(self) -> list[str]:
        """List all registered managers."""
        return list(self.managers.keys())

    def get_default_manager(self) -> Optional[WorkEffortManager]:
        """Get the default manager."""
        return self.factory.get_default_manager()

    def set_default_manager(self, manager_name: str) -> bool:
        """Set the default manager."""
        if manager_name not in self.managers:
            self.logger.error(f"Manager {manager_name} not found")
            return False
        try:
            # Assuming the factory has a method to set the default manager
            self.factory.set_default_manager(manager_name)
            return True
        except Exception as e:
            self.logger.error(f"Error setting default manager: {e}")
            return False
