"""Per-file skill storage.

Each skill is stored as its own JSON file in a dedicated directory.
This makes skills easy to browse, version-control individually, and
avoids loading the entire collection just to check one entry.

Migration: if an old single-file ``skills.json`` exists, it's read once
and converted into individual files on first use.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------- #
# Skill model
# --------------------------------------------------------------------------- #

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


# --------------------------------------------------------------------------- #
# Storage helpers
# --------------------------------------------------------------------------- #

def _sanitize_name(name: str) -> str:
    """Convert a skill name into a filesystem-safe filename."""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.json"


def _load_old_store(path: Path) -> list[Skill]:
    """Read the legacy single-file store (skills.json)."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as fp:
            raw = json.load(fp)
        skills = [Skill.from_dict(item) for item in raw]
        # Rename to .bak so we don't accidentally read it again.
        path.rename(path.with_suffix(".json.bak"))
        return skills
    except (json.JSONDecodeError, KeyError):
        import warnings
        warnings.warn(f"Corrupted legacy memory store at {path}, ignoring.")
        return []


# --------------------------------------------------------------------------- #
# MemoryStore — one file per skill
# --------------------------------------------------------------------------- #

class MemoryStore:
    """Read/write skills from individual JSON files on disk."""

    def __init__(self, storage_dir: Path):
        self._dir = storage_dir
        self._dir.mkdir(parents=True, exist_ok=True)

        # Migrate legacy single-file store if present.
        old_file = storage_dir.parent / "skills.json"
        if old_file.exists():
            self._migrate_legacy(old_file)

    def _migrate_legacy(self, old_path: Path) -> None:
        """Convert skills.json → one file per skill."""
        legacy = _load_old_store(old_path)
        for skill in legacy:
            fname = _sanitize_name(skill.name)
            if (self._dir / fname).exists():
                continue  # already exists, skip
            with (self._dir / fname).open("w", encoding="utf-8") as fp:
                json.dump(skill.to_dict(), fp, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, name: str, description: str, content: str = "", tags: list[str] | None = None) -> Skill:
        """Persist a new skill and return it."""
        skills = self._load_all()
        skill = Skill(name=name, description=description, content=content, tags=tags or [])

        if any(s.name.lower() == skill.name.lower() for s in skills):
            raise ValueError(f"Skill '{name}' already exists.")

        fname = _sanitize_name(skill.name)
        with (self._dir / fname).open("w", encoding="utf-8") as fp:
            json.dump(skill.to_dict(), fp, indent=2, ensure_ascii=False)
        return skill

    def list_all(self) -> list[dict[str, Any]]:
        """Return every skill as a dict — *without* the full content."""
        skills = self._load_all()
        return [{"id": s.id, "name": s.name, "description": s.description, "tags": s.tags} for s in skills]

    def get(self, identifier: str) -> Skill | None:
        """Retrieve a skill by id or name (case-insensitive)."""
        # Fast path: try filename match (id is hex, names are slugified — unlikely collision).
        fname = _sanitize_name(identifier)
        if (self._dir / fname).exists():
            return self._read_file(self._dir / fname)

        # Slow path: scan all files.
        for f in sorted(self._dir.glob("*.json")):
            skill = self._read_file(f)
            if skill is None:
                continue
            if skill.id == identifier or skill.name.lower() == identifier.lower():
                return skill
        return None

    def delete(self, identifier: str) -> bool:
        """Remove a skill by id or name. Returns True if something was removed."""
        # Find the file first.
        fname = _sanitize_name(identifier)
        target = self._dir / fname
        if not target.exists():
            for f in sorted(self._dir.glob("*.json")):
                skill = self._read_file(f)
                if skill is None:
                    continue
                if skill.id == identifier or skill.name.lower() == identifier.lower():
                    target = f
                    break
            else:
                return False

        target.unlink()
        return True

    def update(self, identifier: str, **fields: Any) -> Skill | None:
        """Patch a skill's fields. Returns the updated skill or None."""
        fname = _sanitize_name(identifier)
        target = self._dir / fname
        if not target.exists():
            for f in sorted(self._dir.glob("*.json")):
                skill = self._read_file(f)
                if skill is None:
                    continue
                if skill.id == identifier or skill.name.lower() == identifier.lower():
                    target = f
                    break
            else:
                return None

        skill = self._read_file(target)
        if skill is None:
            return None

        for key, value in fields.items():
            setattr(skill, key, value)

        with target.open("w", encoding="utf-8") as fp:
            json.dump(skill.to_dict(), fp, indent=2, ensure_ascii=False)
        return skill

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_all(self) -> list[Skill]:
        skills = []
        for f in sorted(self._dir.glob("*.json")):
            skill = self._read_file(f)
            if skill is not None:
                skills.append(skill)
        return skills

    @staticmethod
    def _read_file(path: Path) -> Skill | None:
        try:
            with path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            return Skill.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            import warnings
            warnings.warn(f"Corrupted skill file at {path}, skipping.")
            return None


# --------------------------------------------------------------------------- #
# Convenience helpers used by the tool layer.
# --------------------------------------------------------------------------- #

def get_store(data_dir: str | Path) -> MemoryStore:
    """Return a MemoryStore pointed at the skills directory."""
    return MemoryStore(Path(data_dir) / "skills")