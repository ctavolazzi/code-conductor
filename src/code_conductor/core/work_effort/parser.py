from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

class WorkEffortParser:
    """Parser for work effort data from various formats."""

    @staticmethod
    def parse_markdown(content: str) -> Dict[str, Any]:
        """Parse work effort data from markdown format."""
        data = {
            'title': '',
            'description': '',
            'priority': 'medium',
            'assignee': '',
            'due_date': None,
            'tags': [],
            'status': 'not_started',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'completed_at': None,
            'dependencies': [],
            'related_work_efforts': [],
            'notes': ''
        }

        lines = content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            if line.startswith('# '):
                data['title'] = line[2:].strip()
            elif line.startswith('## '):
                if current_section and section_content:
                    data[current_section.lower()] = '\n'.join(section_content).strip()
                current_section = line[3:].strip()
                section_content = []
            elif current_section:
                section_content.append(line)

        if current_section and section_content:
            data[current_section.lower()] = '\n'.join(section_content).strip()

        return data

    @staticmethod
    def parse_json(content: str) -> Dict[str, Any]:
        """Parse work effort data from JSON format."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """Parse work effort data from a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_path = Path(file_path)
        content = file_path.read_text()

        if file_path.suffix == '.md':
            return WorkEffortParser.parse_markdown(content)
        elif file_path.suffix == '.json':
            return WorkEffortParser.parse_json(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """Convert work effort data to markdown format."""
        markdown = [f"# {data.get('title', 'Untitled Work Effort')}"]

        sections = [
            ('Description', 'description'),
            ('Priority', 'priority'),
            ('Assignee', 'assignee'),
            ('Due Date', 'due_date'),
            ('Tags', 'tags'),
            ('Status', 'status'),
            ('Created At', 'created_at'),
            ('Updated At', 'updated_at'),
            ('Completed At', 'completed_at'),
            ('Dependencies', 'dependencies'),
            ('Related Work Efforts', 'related_work_efforts'),
            ('Notes', 'notes')
        ]

        for section_title, key in sections:
            value = data.get(key)
            if value:
                markdown.extend(['', f"## {section_title}", str(value)])

        return '\n'.join(markdown)

    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """Convert work effort data to JSON format."""
        return json.dumps(data, indent=2)