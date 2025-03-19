#!/usr/bin/env python3
"""
Operations module for code_conductor package.

This module provides compatibility for tests by re-exporting classes and functions
from other modules.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Union
import logging

# Re-export common operations needed by tests
try:
    from src.code_conductor.work_efforts.filesystem.operations import FileSystemOperations
    from src.code_conductor.utils.file_operations import read_file, write_file, ensure_directory_structure
    from src.code_conductor.work_efforts.metadata import extract_metadata_from_file
    from src.code_conductor.work_efforts.storage import (
        save_work_effort, move_work_effort, load_work_efforts,
        load_work_efforts_from_dir
    )
except ImportError:
    # Fallbacks for testing
    class FileSystemOperations:
        """Placeholder for tests"""
        pass

    def read_file(path):
        """Read a file and return its contents"""
        with open(path, 'r') as f:
            return f.read()

    def write_file(path, content):
        """Write content to a file"""
        with open(path, 'w') as f:
            f.write(content)
        return True

    def ensure_directory_structure(directory_path):
        """
        Ensures that the specified directory structure exists.
        Creates directories if they don't exist.

        Args:
            directory_path: Path to directory to ensure exists

        Returns:
            dict: Dictionary of paths created or confirmed to exist
        """
        try:
            base_dir = directory_path

            # Define paths
            work_efforts_dir = os.path.join(base_dir, "work_efforts")
            active_dir = os.path.join(work_efforts_dir, "active")
            completed_dir = os.path.join(work_efforts_dir, "completed")
            archived_dir = os.path.join(work_efforts_dir, "archived")
            templates_dir = os.path.join(work_efforts_dir, "templates")
            scripts_dir = os.path.join(work_efforts_dir, "scripts")

            # Create directories
            for path in [work_efforts_dir, active_dir, completed_dir, archived_dir, templates_dir, scripts_dir]:
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)

            # Return paths
            return {
                "work_efforts": work_efforts_dir,
                "active": active_dir,
                "completed": completed_dir,
                "archived": archived_dir,
                "templates": templates_dir,
                "scripts": scripts_dir
            }
        except Exception as e:
            print(f"Error creating directory structure: {e}")
            return {}

    def extract_metadata_from_file(file_path):
        """
        Extracts metadata from the frontmatter of a markdown file.

        Args:
            file_path (str): Path to the markdown file

        Returns:
            dict: Dictionary containing the extracted metadata
        """
        try:
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                return {}

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # First try YAML frontmatter
            if content.startswith('---'):
                # Find the end of the frontmatter
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    # Extract the YAML content
                    yaml_content = content[3:end_idx].strip()
                    # Parse YAML
                    try:
                        import yaml
                        metadata = yaml.safe_load(yaml_content)
                        if isinstance(metadata, dict):
                            # Add filename to metadata
                            metadata['filename'] = os.path.basename(file_path)
                            return metadata
                    except Exception as e:
                        logging.error(f"Error parsing YAML frontmatter: {e}")

            # If YAML parsing fails, try regex-based approach for WorkEffort format
            metadata = {}

            # Extract title from first heading
            title_match = re.search(r'# (.*?)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()

            # Extract metadata from frontmatter-like sections
            patterns = {
                'assignee': r'assignee:\s*"([^"]*)"',
                'priority': r'priority:\s*"([^"]*)"',
                'due_date': r'due_date:\s*"([^"]*)"',
                'status': r'status:\s*"([^"]*)"',
                'created': r'created:\s*"([^"]*)"',
                'last_updated': r'last_updated:\s*"([^"]*)"',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    metadata[key] = match.group(1)

            # Extract tags
            tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
            if tags_match:
                tags_str = tags_match.group(1)
                # Parse comma-separated list of quoted strings
                tags = re.findall(r'"([^"]*)"', tags_str)
                metadata['tags'] = tags

            # Add filename to metadata
            metadata['filename'] = os.path.basename(file_path)

            return metadata
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
            return {}

    def save_work_effort(work_effort: Union[Dict[str, Any], 'WorkEffort'], target_dir: str) -> str:
        """
        Save a work effort to disk.

        Args:
            work_effort: Work effort to save (either a WorkEffort object or a dictionary)
            target_dir: Directory to save the work effort in

        Returns:
            Path to the saved work effort file, or empty string if save failed
        """
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        try:
            # Check if work_effort is a WorkEffort object or dictionary
            if hasattr(work_effort, 'to_markdown'):
                # It's a WorkEffort object
                content = work_effort.to_markdown()
                title = work_effort.title
                # Use created timestamp if available, otherwise use current time
                timestamp = getattr(work_effort, 'created', datetime.now().strftime("%Y%m%d%H%M"))
                # If filename is already set, use it
                if work_effort.filename and work_effort.filename.endswith('.md'):
                    filename = work_effort.filename
                    file_path = os.path.join(target_dir, filename)
                else:
                    # Create filename from title and timestamp
                    from .work_effort import create_filename_from_title
                    # Convert timestamp format if needed
                    if isinstance(timestamp, str) and len(timestamp) > 12:
                        try:
                            # Try to parse from "YYYY-MM-DD HH:MM" format
                            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                            timestamp = dt.strftime("%Y%m%d%H%M")
                        except ValueError:
                            # If parsing fails, use current timestamp
                            timestamp = datetime.now().strftime("%Y%m%d%H%M")

                    filename = create_filename_from_title(title, timestamp)
                    file_path = os.path.join(target_dir, filename)
            else:
                # Handle as dictionary (original implementation)
                # Generate filename from metadata
                metadata = work_effort.get("metadata", {})
                title = metadata.get("title", "untitled")
                timestamp = metadata.get("created", datetime.now().strftime("%Y%m%d%H%M"))

                # If timestamp is in a different format, convert it
                if isinstance(timestamp, str) and len(timestamp) > 12:
                    try:
                        # Try to parse from "YYYY-MM-DD HH:MM" format
                        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                        timestamp = dt.strftime("%Y%m%d%H%M")
                    except ValueError:
                        # If parsing fails, use current timestamp
                        timestamp = datetime.now().strftime("%Y%m%d%H%M")

                # Create safe filename
                from .work_effort import create_filename_from_title
                filename = create_filename_from_title(title, timestamp)

                # Create full file path
                file_path = os.path.join(target_dir, filename)

                # Get content from dictionary
                content = work_effort.get("content", "")

            # Write content to file
            with open(file_path, "w") as f:
                f.write(content)

            return file_path
        except Exception as e:
            logging.error(f"Error saving work effort: {str(e)}")
            return ""

    def move_work_effort(source_path, target_dir):
        """
        Move a work effort from source_path to target_dir.

        Args:
            source_path: Path to the work effort file
            target_dir: Directory to move the work effort

        Returns:
            str: Path to the moved file
        """
        try:
            ensure_directory_structure(target_dir)

            # Get filename
            filename = os.path.basename(source_path)

            # Create target path
            target_path = os.path.join(target_dir, filename)

            # Move file
            shutil.move(source_path, target_path)

            return target_path
        except Exception as e:
            print(f"Error moving work effort: {e}")
            return None

    def load_work_efforts(directory_path):
        """
        Load all work efforts from a directory.

        Args:
            directory_path: Path to the directory containing work_efforts

        Returns:
            dict: Dictionary of work efforts organized by status
        """
        try:
            if not os.path.exists(directory_path):
                return {"active": {}, "completed": {}, "archived": {}}

            # Structure matches what tests expect
            result = {
                "active": {},
                "completed": {},
                "archived": {}
            }

            # Construct paths to each status directory
            work_efforts_dir = os.path.join(directory_path, "work_efforts")
            if not os.path.exists(work_efforts_dir):
                return result

            for status in ["active", "completed", "archived"]:
                status_dir = os.path.join(work_efforts_dir, status)
                if not os.path.exists(status_dir):
                    continue

                for filename in os.listdir(status_dir):
                    if not filename.endswith('.md'):
                        continue

                    file_path = os.path.join(status_dir, filename)
                    content = read_file(file_path)
                    metadata = extract_metadata_from_file(file_path)

                    # Ensure metadata has status
                    if "status" not in metadata:
                        metadata["status"] = status

                    # Get file stats for last_modified time
                    try:
                        stat_info = os.stat(file_path)
                        last_modified = stat_info.st_mtime
                    except:
                        last_modified = datetime.now().timestamp()

                    work_effort = {
                        'metadata': metadata,
                        'content': content,
                        'path': file_path,
                        'last_modified': last_modified,
                        'filename': filename
                    }

                    # Store in the appropriate status dictionary
                    result[status][filename] = work_effort

            return result
        except Exception as e:
            logging.error(f"Error loading work efforts: {e}")
            return {"active": {}, "completed": {}, "archived": {}}

    def load_work_efforts_from_dir(directory_path):
        """Alias for load_work_efforts for compatibility"""
        return load_work_efforts(directory_path)
