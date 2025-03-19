from typing import Optional
import os
import logging

from .manager import WorkEffortManager
from .manager_registry import WorkEffortManagerRegistry

class WorkEffortManagerLoader:
    """Loader for work effort managers."""

    def __init__(self, project_dir: str):
        """Initialize the loader with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.registry = WorkEffortManagerRegistry(project_dir)

    def load_manager(self, manager_name: Optional[str] = None) -> Optional[WorkEffortManager]:
        """Load a work effort manager by name or get the default manager."""
        try:
            if manager_name:
                return self.registry.get_manager(manager_name)
            return self.registry.get_default_manager()
        except Exception as e:
            self.logger.error(f"Error loading manager: {e}")
            return None

    def load_or_create_manager(self, manager_name: str) -> Optional[WorkEffortManager]:
        """Load a manager by name or create it if it doesn't exist."""
        try:
            manager = self.registry.get_manager(manager_name)
            if not manager:
                self.logger.info(f"Creating new manager: {manager_name}")
                manager = self.registry.get_manager(manager_name)  # This will create the manager
            return manager
        except Exception as e:
            self.logger.error(f"Error loading or creating manager: {e}")
            return None

    def remove_manager(self, manager_name: str) -> bool:
        """Remove a manager from the registry."""
        try:
            return self.registry.remove_manager(manager_name)
        except Exception as e:
            self.logger.error(f"Error removing manager: {e}")
            return False

    def list_managers(self) -> list[str]:
        """List all registered managers."""
        try:
            return self.registry.list_managers()
        except Exception as e:
            self.logger.error(f"Error listing managers: {e}")
            return []

    def set_default_manager(self, manager_name: str) -> bool:
        """Set the default manager."""
        try:
            return self.registry.set_default_manager(manager_name)
        except Exception as e:
            self.logger.error(f"Error setting default manager: {e}")
            return False