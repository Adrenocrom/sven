from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

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
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            name=data["name"],
            description=data.get("description", ""),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


# --------------------------------------------------------------------------- #
# Storage helpers
# --------------------------------------------------------------------------- #

def _sanitize_name(name: str) -> str:
    """Convert a skill name into a filesystem-safe directory slug."""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}"


def _skill_path(storage_dir: Path, slug: str) -> Path:
    """Return the path to SKILL.md for a given skill slug."""
    return storage_dir / slug / "SKILL.md"


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content.
    
    Returns:
        Tuple of (metadata dict, body text without frontmatter)
    """
    if not content.startswith("---"):
        return {}, content
    
    # Find the closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content
    
    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()
    
    try:
        metadata = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        metadata = {}
    
    return metadata, body


def _build_markdown(skill: Skill) -> str:
    """Convert a Skill object to markdown with frontmatter."""
    # Build frontmatter
    frontmatter = {
        "name": skill.name,
        "description": skill.description,
        "tags": skill.tags,
        "created_at": skill.created_at,
    }
    
    yaml_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    
    # Combine frontmatter and content
    return f"---\n{yaml_str}---\n\n{skill.content}\n"

# --------------------------------------------------------------------------- #
# MemoryStore — one directory per skill with SKILL.md
# --------------------------------------------------------------------------- #

class MemoryStore:
    """Read/write skills from individual markdown files on disk."""

    def __init__(self, storage_dir: Path):
        self._dir = storage_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, name: str, description: str, content: str = "", tags: list[str] | None = None) -> Skill:
        """Persist a new skill and return it."""
        slug = _sanitize_name(name)
        skill_path = _skill_path(self._dir, slug)
        
        # Check if already exists (case-insensitive check)
        if skill_path.exists():
            raise ValueError(f"Skill '{name}' already exists.")
        
        # Create directory and write file
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        
        skill = Skill(
            name=name,
            description=description,
            content=content,
            tags=tags or [],
        )
        
        with skill_path.open("w", encoding="utf-8") as fp:
            fp.write(_build_markdown(skill))
        
        return skill

    def list_all(self) -> list[dict[str, Any]]:
        """Return every skill as a dict — *without* the full content."""
        skills = []
        for slug_dir in sorted(self._dir.iterdir()):
            if not slug_dir.is_dir():
                continue
            skill_file = slug_dir / "SKILL.md"
            if skill_file.exists():
                try:
                    metadata, _ = self._read_metadata(skill_file)
                    skills.append({
                        "id": metadata.get("id", uuid.uuid4().hex[:12]),
                        "name": metadata["name"],
                        "description": metadata.get("description", ""),
                        "tags": metadata.get("tags", []),
                    })
                except Exception:
                    continue  # Skip corrupted files
        return skills

    def get(self, identifier: str) -> Skill | None:
        """Retrieve a skill by name (case-insensitive)."""
        slug = _sanitize_name(identifier)
        skill_path = _skill_path(self._dir, slug)
        
        if not skill_path.exists():
            return None
        
        try:
            metadata, content = self._read_metadata(skill_path)
            return Skill(
                id=metadata.get("id", uuid.uuid4().hex[:12]),
                name=metadata["name"],
                description=metadata.get("description", ""),
                content=content,
                tags=metadata.get("tags", []),
                created_at=metadata.get("created_at", datetime.now(timezone.utc).isoformat()),
            )
        except Exception:
            return None

    def delete(self, identifier: str) -> bool:
        """Remove a skill by name. Returns True if something was removed."""
        slug = _sanitize_name(identifier)
        skill_path = _skill_path(self._dir, slug)
        
        if not skill_path.exists():
            return False
        
        # Remove the entire directory (SKILL.md + any subdirectories)
        import shutil
        shutil.rmtree(skill_path.parent)
        return True

    def update(self, identifier: str, **fields: Any) -> Skill | None:
        """Patch a skill's fields. Returns the updated skill or None."""
        slug = _sanitize_name(identifier)
        skill_path = _skill_path(self._dir, slug)
        
        if not skill_path.exists():
            return None
        
        try:
            metadata, content = self._read_metadata(skill_path)
        except Exception:
            return None
        
        # Apply updates
        for key, value in fields.items():
            if key == "content":
                content = value  # Content is stored separately
            elif key in ("name", "description", "tags", "created_at"):
                metadata[key] = value
        
        # Rebuild the skill object
        skill = Skill(
            id=metadata.get("id", uuid.uuid4().hex[:12]),
            name=metadata["name"],
            description=metadata.get("description", ""),
            content=content,
            tags=metadata.get("tags", []),
            created_at=metadata.get("created_at", datetime.now(timezone.utc).isoformat()),
        )
        
        # Write back
        with skill_path.open("w", encoding="utf-8") as fp:
            fp.write(_build_markdown(skill))
        
        return skill

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _read_metadata(self, path: Path) -> tuple[dict[str, Any], str]:
        """Read a SKILL.md file and return (metadata, content)."""
        with path.open("r", encoding="utf-8") as fp:
            content = fp.read()
        
        metadata, body = _parse_frontmatter(content)
        return metadata, body

# --------------------------------------------------------------------------- #
# Convenience helpers used by the tool layer.
# --------------------------------------------------------------------------- #

def get_store(data_dir: str | Path) -> MemoryStore:
    """Return a MemoryStore pointed at the skills directory."""
    return MemoryStore(Path(data_dir) / "skills")

