from typing import Dict, List, Optional
import os
import json
import logging
from datetime import datetime

class WorkEffortIndexer:
    """Class to handle indexing of work efforts."""

    def __init__(self, project_dir: str):
        """Initialize the indexer with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.index_file = os.path.join(project_dir, ".code_conductor", "index.json")
        self._ensure_index_dir()

    def _ensure_index_dir(self):
        """Ensure the index directory exists."""
        index_dir = os.path.dirname(self.index_file)
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

    def index_work_effort(self, work_effort_id: str, data: Dict) -> bool:
        """Index a single work effort."""
        try:
            index = self._load_index()
            index[work_effort_id] = {
                "title": data.get("title", ""),
                "status": data.get("status", "active"),
                "created_at": data.get("created_at", datetime.now().isoformat()),
                "updated_at": data.get("updated_at", datetime.now().isoformat()),
                "tags": data.get("tags", []),
                "assignee": data.get("assignee", ""),
                "priority": data.get("priority", "medium")
            }
            self._save_index(index)
            return True
        except Exception as e:
            self.logger.error(f"Error indexing work effort {work_effort_id}: {str(e)}")
            return False

    def remove_from_index(self, work_effort_id: str) -> bool:
        """Remove a work effort from the index."""
        try:
            index = self._load_index()
            if work_effort_id in index:
                del index[work_effort_id]
                self._save_index(index)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing work effort {work_effort_id} from index: {str(e)}")
            return False

    def get_indexed_work_effort(self, work_effort_id: str) -> Optional[Dict]:
        """Get an indexed work effort by ID."""
        try:
            index = self._load_index()
            return index.get(work_effort_id)
        except Exception as e:
            self.logger.error(f"Error getting indexed work effort {work_effort_id}: {str(e)}")
            return None

    def search_index(self, query: str) -> List[str]:
        """Search the index for work efforts matching the query."""
        try:
            index = self._load_index()
            results = []
            query = query.lower()

            for work_effort_id, data in index.items():
                if (query in data["title"].lower() or
                    query in " ".join(data["tags"]).lower() or
                    query in data["assignee"].lower()):
                    results.append(work_effort_id)

            return results
        except Exception as e:
            self.logger.error(f"Error searching index: {str(e)}")
            return []

    def _load_index(self) -> Dict:
        """Load the index from disk."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading index: {str(e)}")
                return {}
        return {}

    def _save_index(self, index: Dict):
        """Save the index to disk."""
        try:
            with open(self.index_file, "w") as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")

    def clear_index(self):
        """Clear the entire index."""
        try:
            self._save_index({})
        except Exception as e:
            self.logger.error(f"Error clearing index: {str(e)}")