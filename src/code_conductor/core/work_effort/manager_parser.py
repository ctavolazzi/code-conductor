from typing import Dict, Optional, Any, List
import os
import logging
import json
import yaml
import re
from datetime import datetime

class WorkEffortManagerParser:
    """Parser for work effort manager data."""

    def __init__(self, project_dir: str):
        """Initialize the parser with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)

    def parse_work_effort_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a work effort file and return its data."""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Work effort file not found: {file_path}")
                return None

            with open(file_path, 'r') as f:
                content = f.read()

            # Extract metadata from frontmatter if present
            metadata = {}
            if content.startswith('---'):
                try:
                    # Find the second '---' to get the frontmatter
                    end_index = content.find('---', 3)
                    if end_index != -1:
                        frontmatter = content[3:end_index].strip()
                        metadata = yaml.safe_load(frontmatter)
                        content = content[end_index + 3:].strip()
                except Exception as e:
                    self.logger.warning(f"Error parsing frontmatter: {e}")

            # Extract basic information from filename
            filename = os.path.basename(file_path)
            match = re.match(r'^(\d{12})_(.+)\.md$', filename)
            if match:
                timestamp, title = match.groups()
                metadata['created_at'] = datetime.strptime(timestamp, '%Y%m%d%H%M').isoformat()
                metadata['title'] = title.replace('_', ' ').title()

            # Parse content for additional metadata
            metadata.update(self._parse_content_metadata(content))

            return {
                'metadata': metadata,
                'content': content
            }
        except Exception as e:
            self.logger.error(f"Error parsing work effort file: {e}")
            return None

    def _parse_content_metadata(self, content: str) -> Dict[str, Any]:
        """Parse metadata from content."""
        metadata = {}

        # Look for common metadata patterns
        patterns = {
            'status': r'status:\s*(\w+)',
            'priority': r'priority:\s*(\w+)',
            'assignee': r'assignee:\s*(.+)$',
            'due_date': r'due:\s*(\d{4}-\d{2}-\d{2})',
            'tags': r'tags:\s*\[(.*?)\]',
            'dependencies': r'depends_on:\s*\[(.*?)\]'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if key in ['tags', 'dependencies']:
                    value = [item.strip() for item in value.split(',') if item.strip()]
                metadata[key] = value

        return metadata

    def parse_manager_config(self, config_file: str) -> Optional[Dict[str, Any]]:
        """Parse a manager configuration file."""
        try:
            if not os.path.exists(config_file):
                self.logger.error(f"Config file not found: {config_file}")
                return None

            with open(config_file, 'r') as f:
                config = json.load(f)

            # Validate required fields
            required_fields = ['work_efforts_dir', 'templates_dir', 'history_dir']
            for field in required_fields:
                if field not in config:
                    self.logger.error(f"Missing required field in config: {field}")
                    return None

            return config
        except Exception as e:
            self.logger.error(f"Error parsing manager config: {e}")
            return None

    def parse_work_effort_template(self, template_file: str) -> Optional[str]:
        """Parse a work effort template file."""
        try:
            if not os.path.exists(template_file):
                self.logger.error(f"Template file not found: {template_file}")
                return None

            with open(template_file, 'r') as f:
                template = f.read()

            return template
        except Exception as e:
            self.logger.error(f"Error parsing template file: {e}")
            return None

    def parse_work_effort_history(self, history_file: str) -> Optional[List[Dict[str, Any]]]:
        """Parse a work effort history file."""
        try:
            if not os.path.exists(history_file):
                self.logger.error(f"History file not found: {history_file}")
                return None

            with open(history_file, 'r') as f:
                history = json.load(f)

            if not isinstance(history, list):
                self.logger.error("History file must contain a list of events")
                return None

            # Validate each history entry
            for entry in history:
                if not all(key in entry for key in ['timestamp', 'event_type', 'details']):
                    self.logger.error("Invalid history entry format")
                    return None

            return history
        except Exception as e:
            self.logger.error(f"Error parsing history file: {e}")
            return None

    def parse_work_effort_dependencies(self, dependencies_file: str) -> Optional[Dict[str, List[str]]]:
        """Parse a work effort dependencies file."""
        try:
            if not os.path.exists(dependencies_file):
                self.logger.error(f"Dependencies file not found: {dependencies_file}")
                return None

            with open(dependencies_file, 'r') as f:
                dependencies = json.load(f)

            if not isinstance(dependencies, dict):
                self.logger.error("Dependencies file must contain a dictionary")
                return None

            return dependencies
        except Exception as e:
            self.logger.error(f"Error parsing dependencies file: {e}")
            return None