from typing import Dict, List, Any, Optional, Set
import os
import json
import logging
from datetime import datetime

class WorkEffortManagerTracer:
    """Tracer for work effort manager data."""

    def __init__(self, project_dir: str):
        """Initialize the tracer with a project directory."""
        self.project_dir = project_dir
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, Dict[str, Any]] = {}

    def trace_dependencies(self, work_effort_id: str, recursive: bool = False) -> List[str]:
        """Trace dependencies of a work effort."""
        try:
            dependencies = []
            visited = set()
            self._trace_dependencies_recursive(work_effort_id, dependencies, visited, recursive)
            return dependencies
        except Exception as e:
            self.logger.error(f"Error tracing dependencies: {e}")
            return []

    def _trace_dependencies_recursive(self, work_effort_id: str, dependencies: List[str], visited: Set[str], recursive: bool) -> None:
        """Helper method for recursive dependency tracing."""
        if work_effort_id in visited:
            return

        visited.add(work_effort_id)
        deps_file = os.path.join(self.project_dir, '.code_conductor', 'dependencies.json')

        try:
            if os.path.exists(deps_file):
                with open(deps_file, 'r') as f:
                    all_deps = json.load(f)

                if work_effort_id in all_deps:
                    direct_deps = all_deps[work_effort_id]
                    dependencies.extend(direct_deps)

                    if recursive:
                        for dep in direct_deps:
                            self._trace_dependencies_recursive(dep, dependencies, visited, recursive)
        except Exception as e:
            self.logger.error(f"Error reading dependencies file: {e}")

    def trace_related(self, work_effort_id: str, recursive: bool = False) -> List[str]:
        """Trace related work efforts."""
        try:
            related = []
            visited = set()
            self._trace_related_recursive(work_effort_id, related, visited, recursive)
            return related
        except Exception as e:
            self.logger.error(f"Error tracing related work efforts: {e}")
            return []

    def _trace_related_recursive(self, work_effort_id: str, related: List[str], visited: Set[str], recursive: bool) -> None:
        """Helper method for recursive related work effort tracing."""
        if work_effort_id in visited:
            return

        visited.add(work_effort_id)
        deps_file = os.path.join(self.project_dir, '.code_conductor', 'dependencies.json')

        try:
            if os.path.exists(deps_file):
                with open(deps_file, 'r') as f:
                    all_deps = json.load(f)

                # Find work efforts that depend on this one
                for we_id, deps in all_deps.items():
                    if work_effort_id in deps and we_id not in related:
                        related.append(we_id)
                        if recursive:
                            self._trace_related_recursive(we_id, related, visited, recursive)
        except Exception as e:
            self.logger.error(f"Error reading dependencies file: {e}")

    def trace_chain(self, work_effort_id: str) -> List[List[str]]:
        """Trace the dependency chain of a work effort."""
        try:
            chains = []
            visited = set()
            current_chain = []
            self._trace_chain_recursive(work_effort_id, chains, current_chain, visited)
            return chains
        except Exception as e:
            self.logger.error(f"Error tracing dependency chain: {e}")
            return []

    def _trace_chain_recursive(self, work_effort_id: str, chains: List[List[str]], current_chain: List[str], visited: Set[str]) -> None:
        """Helper method for recursive chain tracing."""
        if work_effort_id in visited:
            if current_chain:
                chains.append(current_chain[:])
            return

        visited.add(work_effort_id)
        current_chain.append(work_effort_id)

        deps_file = os.path.join(self.project_dir, '.code_conductor', 'dependencies.json')

        try:
            if os.path.exists(deps_file):
                with open(deps_file, 'r') as f:
                    all_deps = json.load(f)

                if work_effort_id in all_deps:
                    deps = all_deps[work_effort_id]
                    if not deps:
                        chains.append(current_chain[:])
                    else:
                        for dep in deps:
                            self._trace_chain_recursive(dep, chains, current_chain[:], visited)
                else:
                    chains.append(current_chain[:])
        except Exception as e:
            self.logger.error(f"Error reading dependencies file: {e}")
            if current_chain:
                chains.append(current_chain[:])

    def trace_history(self, work_effort_id: str) -> List[Dict[str, Any]]:
        """Trace the history of a work effort."""
        try:
            history_dir = os.path.join(self.project_dir, '.code_conductor', 'history')
            history_file = os.path.join(history_dir, f"{work_effort_id}.json")

            if not os.path.exists(history_file):
                return []

            with open(history_file, 'r') as f:
                history = json.load(f)

            # Sort history by timestamp
            history.sort(key=lambda x: x.get('timestamp', ''))
            return history
        except Exception as e:
            self.logger.error(f"Error tracing history: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self.cache.clear()

    def _load_work_effort(self, work_effort_id: str) -> Optional[Dict[str, Any]]:
        """Load a work effort by its ID."""
        try:
            if work_effort_id in self.cache:
                return self.cache[work_effort_id]

            work_efforts_dir = os.path.join(self.project_dir, '.code_conductor', 'work_efforts', 'active')
            work_effort_file = os.path.join(work_efforts_dir, f"{work_effort_id}.md")

            if not os.path.exists(work_effort_file):
                return None

            with open(work_effort_file, 'r') as f:
                content = f.read()

            # Parse the work effort file (assuming it has frontmatter)
            metadata = {}
            if content.startswith('---'):
                try:
                    end_index = content.find('---', 3)
                    if end_index != -1:
                        frontmatter = content[3:end_index].strip()
                        import yaml
                        metadata = yaml.safe_load(frontmatter)
                        content = content[end_index + 3:].strip()
                except Exception as e:
                    self.logger.warning(f"Error parsing frontmatter: {e}")

            work_effort = {
                'id': work_effort_id,
                'metadata': metadata,
                'content': content
            }

            self.cache[work_effort_id] = work_effort
            return work_effort
        except Exception as e:
            self.logger.error(f"Error loading work effort: {e}")
            return None