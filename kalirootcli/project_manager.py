
import os
import json
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

PROJECTS_REGISTRY_PATH = os.path.expanduser("~/.kaliroot/projects.json")

@dataclass
class ProjectEntry:
    path: str
    name: str
    goal: str
    created_at: str
    last_accessed: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "goal": self.goal,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectEntry':
        return cls(
            path=data.get("path", ""),
            name=data.get("name", ""),
            goal=data.get("goal", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_accessed=data.get("last_accessed", datetime.now().isoformat())
        )

class ProjectManager:
    """Manages the history and registry of created projects."""

    def __init__(self):
        self.registry_path = PROJECTS_REGISTRY_PATH
        self.projects: List[ProjectEntry] = self._load_registry()

    def _load_registry(self) -> List[ProjectEntry]:
        if not os.path.exists(self.registry_path):
            return []
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                return [ProjectEntry.from_dict(p) for p in data]
        except Exception as e:
            logger.error(f"Error loading project registry: {e}")
            return []

    def _save_registry(self):
        try:
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            with open(self.registry_path, 'w') as f:
                json.dump([p.to_dict() for p in self.projects], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving project registry: {e}")

    def add_or_update_project(self, path: str, name: str, goal: str):
        """Adds a project or updates its last access time."""
        now = datetime.now().isoformat()
        
        # Check if exists
        existing = next((p for p in self.projects if p.path == path), None)
        
        if existing:
            existing.last_accessed = now
            existing.goal = goal # Update goal if changed
            # Move to front
            self.projects.remove(existing)
            self.projects.insert(0, existing)
        else:
            new_project = ProjectEntry(
                path=path,
                name=name,
                goal=goal,
                created_at=now,
                last_accessed=now
            )
            self.projects.insert(0, new_project)
        
        # Keep only last 20
        self.projects = self.projects[:20]
        self._save_registry()

    def get_recent_projects(self) -> List[ProjectEntry]:
        return self.projects
