import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

class WorkEffortManagerIndexer:
    """Indexes work efforts in a directory."""

    def __init__(self, project_dir: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the indexer.

        Args:
            project_dir: The root directory of the project.
            config: Optional configuration dictionary.
        """
        self.project_dir = project_dir
        self.config = config or {}
        self.indexed_work_efforts = {}
        self.logger = logging.getLogger(__name__)

    def index_all_work_efforts(self) -> None:
        """Index all work efforts in the project."""
        try:
            # Get work efforts directory
            work_efforts_dir = self.config.get("work_efforts_dir", os.path.join(self.project_dir, "_AI-Setup", "work_efforts"))

            # Create directory if it doesn't exist
            os.makedirs(work_efforts_dir, exist_ok=True)

            # Create status directories if they don't exist
            for status in ["active", "completed", "archived", "paused"]:
                os.makedirs(os.path.join(work_efforts_dir, status), exist_ok=True)

            # Scan all work effort files
            indexed_efforts = {}
            for status in ["active", "completed", "archived", "paused"]:
                status_dir = os.path.join(work_efforts_dir, status)
                if not os.path.exists(status_dir):
                    continue

                for filename in os.listdir(status_dir):
                    if not filename.endswith(".md"):
                        continue

                    file_path = os.path.join(status_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                            metadata = self._parse_work_effort(content, file_path)
                            if metadata:
                                metadata["status"] = status
                                indexed_efforts[metadata["id"]] = metadata
                    except Exception as e:
                        self.logger.error(f"Error indexing {filename}: {str(e)}")

            # Update indexed work efforts
            self.indexed_work_efforts = indexed_efforts
            self.logger.info(f"✅ Indexed {len(indexed_efforts)} work efforts in {work_efforts_dir}")

        except Exception as e:
            self.logger.error(f"❌ Failed to index work efforts: {str(e)}")
            self.indexed_work_efforts = {}

    def _parse_work_effort(self, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse work effort data from content.

        Args:
            content: The content of the work effort file.
            file_path: The path to the work effort file.

        Returns:
            A dictionary containing the parsed work effort data.
        """
        try:
            # Extract metadata from frontmatter
            metadata = self._extract_frontmatter(content)
            if not metadata:
                return None

            # Extract metadata from filename
            filename_metadata = self._extract_filename_metadata(file_path)
            metadata.update(filename_metadata)

            # Add file path
            metadata["file_path"] = file_path

            self.logger.debug(f"Extracted metadata: {metadata}")

            # Wrap metadata in a metadata field
            work_effort_data = {
                "id": metadata.get("id"),
                "metadata": {
                    **metadata,
                    "id": metadata.get("id")  # Include id in metadata
                }
            }

            return work_effort_data

        except Exception as e:
            self.logger.error(f"Error parsing work effort: {str(e)}")
            return None

    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from frontmatter.

        Args:
            content: The content of the work effort file.

        Returns:
            A dictionary containing the extracted metadata.
        """
        try:
            # Split content into frontmatter and body
            parts = content.split("---", 2)
            if len(parts) != 3:
                self.logger.debug("No frontmatter found in content")
                # Create default metadata if no frontmatter
                metadata = {
                    "id": datetime.now().strftime("%Y%m%d%H%M") + "_untitled",
                    "title": "Untitled",
                    "status": "active"
                }
                return metadata

            # Parse frontmatter
            frontmatter = parts[1].strip()
            if not frontmatter:
                self.logger.debug("Empty frontmatter found")
                metadata = {
                    "id": datetime.now().strftime("%Y%m%d%H%M") + "_untitled",
                    "title": "Untitled",
                    "status": "active"
                }
                return metadata

            metadata = {}

            # Try YAML parsing first
            try:
                import yaml
                metadata = yaml.safe_load(frontmatter) or {}
            except Exception as e:
                self.logger.debug(f"YAML parsing failed, falling back to key-value parsing: {str(e)}")
                # Fall back to key-value parsing
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()

            # Ensure required fields are present
            if not metadata.get("id"):
                # Generate an ID from the title if available
                title = metadata.get("title", "untitled")
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                metadata["id"] = f"{timestamp}_{title.lower().replace(' ', '_')}"

            if not metadata.get("title"):
                metadata["title"] = "Untitled"

            if not metadata.get("status"):
                metadata["status"] = "active"

            # Add created_at if not present
            if not metadata.get("created_at"):
                metadata["created_at"] = datetime.now().isoformat()

            # Add updated_at if not present
            if not metadata.get("updated_at"):
                metadata["updated_at"] = datetime.now().isoformat()

            self.logger.debug(f"Extracted metadata: {metadata}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting frontmatter: {str(e)}")
            # Return default metadata on error
            return {
                "id": datetime.now().strftime("%Y%m%d%H%M") + "_untitled",
                "title": "Untitled",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

    def _extract_filename_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from filename.

        Args:
            filename: The filename of the work effort file.

        Returns:
            A dictionary containing the extracted metadata.
        """
        try:
            # Extract timestamp and title from filename
            base_name = os.path.basename(filename)
            name_without_ext = os.path.splitext(base_name)[0]

            # Split into timestamp and title parts
            parts = name_without_ext.split("_", 1)

            metadata = {
                "created_at": datetime.now().isoformat()
            }

            # If filename has timestamp prefix, use it
            if len(parts) > 1 and len(parts[0]) == 12:  # YYYYMMDDHHmm format
                try:
                    timestamp = datetime.strptime(parts[0], "%Y%m%d%H%M")
                    metadata["created_at"] = timestamp.isoformat()
                except ValueError:
                    pass

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting filename metadata: {str(e)}")
            return {}

    def get_indexed_work_effort(self, work_effort_id: str) -> Optional[Dict[str, Any]]:
        """Get an indexed work effort by ID.

        Args:
            work_effort_id: The ID of the work effort.

        Returns:
            The indexed work effort data if found, None otherwise.
        """
        return self.indexed_work_efforts.get(work_effort_id)

    def get_indexed_work_efforts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all indexed work efforts with a specific status.

        Args:
            status: The status to filter by.

        Returns:
            A list of work effort data dictionaries.
        """
        return [
            work_effort
            for work_effort in self.indexed_work_efforts.values()
            if work_effort.get("metadata", {}).get("status") == status
        ]

    def get_indexed_work_efforts_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all indexed work efforts assigned to a specific person.

        Args:
            assignee: The assignee to filter by.

        Returns:
            A list of work effort data dictionaries.
        """
        return [
            work_effort
            for work_effort in self.indexed_work_efforts.values()
            if work_effort.get("metadata", {}).get("assignee") == assignee
        ]

    def clear_index(self) -> None:
        """Clear the index cache."""
        self.indexed_work_efforts = {}