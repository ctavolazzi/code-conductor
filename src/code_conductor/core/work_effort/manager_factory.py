from typing import Dict, Optional
import os
import logging
from datetime import datetime

from .manager import WorkEffortManager
from .manager_info import WorkEffortManagerInfo
from .manager_config import WorkEffortManagerConfig
from .indexer import WorkEffortIndexer
from .validator import WorkEffortValidator
from .tracer import WorkEffortTracer
from .counter import WorkEffortCounter
from .template import WorkEffortTemplate
from .event_emitter import EventEmitter

class WorkEffortManagerFactory:
    """Factory class for creating work effort managers."""

    def __init__(self, project_dir: str):
        """Initialize the factory with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)

    def create_manager(self, manager_name: str, config: Optional[Dict] = None) -> Optional[WorkEffortManager]:
        """Create a new work effort manager instance."""
        try:
            # Initialize all required components
            manager_info = WorkEffortManagerInfo(self.project_dir)
            manager_config = WorkEffortManagerConfig(self.project_dir)
            indexer = WorkEffortIndexer(self.project_dir)
            validator = WorkEffortValidator()
            tracer = WorkEffortTracer(self.project_dir)
            counter = WorkEffortCounter(self.project_dir)
            template = WorkEffortTemplate(self.project_dir)
            event_emitter = EventEmitter()

            # Set up configuration
            if config:
                manager_config.set_config(manager_name, config)
            elif not manager_config.get_config(manager_name):
                manager_config.set_config(manager_name, manager_config.get_default_config())

            # Ensure required directories exist
            manager_config.ensure_directories(manager_name)

            # Create and return the manager instance
            manager = WorkEffortManager(
                name=manager_name,
                project_dir=self.project_dir,
                info=manager_info,
                config=manager_config,
                indexer=indexer,
                validator=validator,
                tracer=tracer,
                counter=counter,
                template=template,
                event_emitter=event_emitter
            )

            # Set manager info
            manager_info.set_manager_info(manager_name, {
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })

            return manager
        except Exception as e:
            self.logger.error(f"Error creating manager {manager_name}: {str(e)}")
            return None

    def get_manager(self, manager_name: str) -> Optional[WorkEffortManager]:
        """Get an existing work effort manager instance."""
        try:
            manager_info = WorkEffortManagerInfo(self.project_dir)
            if not manager_info.get_manager_info(manager_name):
                return None

            return self.create_manager(manager_name)
        except Exception as e:
            self.logger.error(f"Error getting manager {manager_name}: {str(e)}")
            return None

    def get_default_manager(self) -> Optional[WorkEffortManager]:
        """Get the default work effort manager instance."""
        try:
            manager_info = WorkEffortManagerInfo(self.project_dir)
            default_manager = manager_info.get_default_manager()
            if not default_manager:
                return None

            return self.get_manager(default_manager)
        except Exception as e:
            self.logger.error(f"Error getting default manager: {str(e)}")
            return None

    def remove_manager(self, manager_name: str) -> bool:
        """Remove a work effort manager."""
        try:
            manager_info = WorkEffortManagerInfo(self.project_dir)
            manager_config = WorkEffortManagerConfig(self.project_dir)

            # Remove manager info and config
            manager_info.remove_manager_info(manager_name)
            manager_config.remove_config(manager_name)

            return True
        except Exception as e:
            self.logger.error(f"Error removing manager {manager_name}: {str(e)}")
            return False

    def set_default_manager(self, manager_name: str) -> bool:
        """Set the default work effort manager.

        Args:
            manager_name: Name of the manager to set as default.

        Returns:
            True if successful, False otherwise.
        """
        try:
            manager_info = WorkEffortManagerInfo(self.project_dir)
            if not manager_info.get_manager_info(manager_name):
                self.logger.error(f"Manager {manager_name} not found")
                return False

            manager_info.set_default_manager(manager_name)
            return True
        except Exception as e:
            self.logger.error(f"Error setting default manager: {str(e)}")
            return False