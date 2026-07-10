"""Persistent memory store for skills (learned facts, preferences, patterns).

Each skill is a small piece of knowledge that Sven has acquired during
conversation. Skills are stored as JSON and can be discovered by their
short description — the LLM reads the list of descriptions to decide
whether any of them are relevant to the current context.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Skill:
    """A single stored piece of knowledge."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    description: str = ""
    content: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(**data)


class MemoryStore:
    """Read/write skills from a JSON file on disk."""

    def __init__(self, storage_path: Path):
        self._path = storage_path
        # Ensure the parent directory exists so we never fail on first write.
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, name: str, description: str, content: str = "", tags: list[str] | None = None) -> Skill:
        """Persist a new skill and return it."""
        skills = self._load()
        skill = Skill(name=name, description=description, content=content, tags=tags or [])

        # Reject duplicates by name (case-insensitive).
        if any(s.name.lower() == skill.name.lower() for s in skills):
            raise ValueError(f"Skill '{name}' already exists.")

        skills.append(skill)
        self._save(skills)
        return skill

    def list_all(self) -> list[dict[str, Any]]:
        """Return every skill as a dict — *without* the full content."""
        return [{"id": s.id, "name": s.name, "description": s.description, "tags": s.tags} for s in self._load()]

    def get(self, identifier: str) -> Skill | None:
        """Retrieve a skill by id or name (case-insensitive)."""
        skills = self._load()
        for s in skills:
            if s.id == identifier or s.name.lower() == identifier.lower():
                return s
        return None

    def delete(self, identifier: str) -> bool:
        """Remove a skill by id or name. Returns True if something was removed."""
        skills = self._load()
        before = len(skills)
        skills = [s for s in skills if s.id != identifier and s.name.lower() != identifier.lower()]
        if len(skills) == before:
            return False
        self._save(skills)
        return True

    def update(self, identifier: str, **fields: Any) -> Skill | None:
        """Patch a skill's fields. Returns the updated skill or None."""
        skills = self._load()
        for s in skills:
            if s.id == identifier or s.name.lower() == identifier.lower():
                for key, value in fields.items():
                    setattr(s, key, value)
                self._save(skills)
                return s
        return None

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> list[Skill]:
        if not self._path.exists():
            return []
        try:
            with self._path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
            return [Skill.from_dict(item) for item in raw]
        except (json.JSONDecodeError, KeyError):
            # Corrupted file — start fresh and warn.
            import warnings
            warnings.warn(f"Corrupted memory store at {self._path}, starting empty.")
            return []

    def _save(self, skills: list[Skill]) -> None:
        with self._path.open("w", encoding="utf-8") as fp:
            json.dump([s.to_dict() for s in skills], fp, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Convenience helpers used by the tool layer.
# --------------------------------------------------------------------------- #

def get_store(data_dir: str | Path) -> MemoryStore:
    """Return a MemoryStore pointed at the standard data directory."""
    return MemoryStore(Path(data_dir) / "skills.json")