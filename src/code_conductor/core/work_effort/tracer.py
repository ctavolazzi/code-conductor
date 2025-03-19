from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import json
import logging
from datetime import datetime

class WorkEffortTracer:
    """Tracer for work effort dependencies and relationships."""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.logger = logging.getLogger(__name__)

    def trace_dependencies(self, work_effort_id: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """Trace dependencies of a work effort."""
        work_effort = self._load_work_effort(work_effort_id)
        if not work_effort:
            return []

        dependencies = []
        visited = set()

        def _trace_recursive(we_id: str) -> None:
            if we_id in visited:
                return

            visited.add(we_id)
            we = self._load_work_effort(we_id)
            if not we:
                return

            dependencies.append(we)

            if recursive and we.get("dependencies"):
                for dep_id in we["dependencies"]:
                    _trace_recursive(dep_id)

        for dep_id in work_effort.get("dependencies", []):
            if recursive:
                _trace_recursive(dep_id)
            else:
                dep = self._load_work_effort(dep_id)
                if dep:
                    dependencies.append(dep)

        return dependencies

    def trace_related(self, work_effort_id: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """Trace related work efforts."""
        work_effort = self._load_work_effort(work_effort_id)
        if not work_effort:
            return []

        related = []
        visited = set()

        def _trace_recursive(we_id: str) -> None:
            if we_id in visited:
                return

            visited.add(we_id)
            we = self._load_work_effort(we_id)
            if not we:
                return

            related.append(we)

            if recursive and we.get("related_work_efforts"):
                for rel_id in we["related_work_efforts"]:
                    _trace_recursive(rel_id)

        for rel_id in work_effort.get("related_work_efforts", []):
            if recursive:
                _trace_recursive(rel_id)
            else:
                rel = self._load_work_effort(rel_id)
                if rel:
                    related.append(rel)

        return related

    def trace_chain(self, work_effort_id: str) -> List[Dict[str, Any]]:
        """Trace the dependency chain of a work effort."""
        work_effort = self._load_work_effort(work_effort_id)
        if not work_effort:
            return []

        chain = [work_effort]
        current = work_effort

        while current.get("dependencies"):
            next_id = current["dependencies"][0]  # Follow first dependency
            next_we = self._load_work_effort(next_id)
            if not next_we or next_we["id"] in [we["id"] for we in chain]:
                break
            chain.append(next_we)
            current = next_we

        return chain

    def trace_history(self, work_effort_id: str) -> List[Dict[str, Any]]:
        """Trace the history of a work effort."""
        work_effort = self._load_work_effort(work_effort_id)
        if not work_effort:
            return []

        history = []
        history_dir = self.project_dir / "work_efforts" / "history"
        if not history_dir.exists():
            return []

        for file in history_dir.glob(f"*_{work_effort_id}_*.json"):
            try:
                with open(file) as f:
                    history_entry = json.load(f)
                history.append(history_entry)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Error loading history entry {file}: {e}")

        # Sort by timestamp
        history.sort(key=lambda x: datetime.fromisoformat(x.get("updated_at", "1970-01-01T00:00:00")))
        return history

    def _load_work_effort(self, work_effort_id: str) -> Optional[Dict[str, Any]]:
        """Load a work effort by ID."""
        try:
            work_efforts_dir = self.project_dir / "work_efforts" / "active"
            for file in work_efforts_dir.glob("*.json"):
                with open(file) as f:
                    we = json.load(f)
                if we.get("id") == work_effort_id:
                    return we
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error loading work effort {work_effort_id}: {e}")

        return None